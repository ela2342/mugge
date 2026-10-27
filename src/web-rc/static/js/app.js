// app.js -- the page driver for the standalone room correction (US-179).
//
// Wires the DOM, the flow controller (flow.js), the audio I/O (audio-io.js)
// and the Pyodide pipeline (rc-client.js) together. Every decision is the
// flow's; this file forwards events to it, carries out the commands it
// returns and copies view.js's view model into the page.

import { AudioIO, deviceKey, isSuperseded } from "./audio-io.js";
import { parseCalibration } from "./calibration.js";
import { Flow, STEP } from "./flow.js";
import { RcClient } from "./rc-client.js";
import {
  ROLE, SUB_LIMIT_REFUSAL, changeEnclosure, changeLimit, changeRole,
  checkDeclaration, limitRangeText, parseLimitHz,
} from "./safety.js";
import { BASE_SEED } from "./crest-plan.js";
import {
  MEASURED_DB, MEASURED_FFT, curveToBins, drawImpulse, drawPrediction,
  drawRepeatability,
} from "./plot.js";
import {
  REPORT_FILE, channelLabel, reportChannels, viewModel,
} from "./view.js";

const TICK_MS = 250;
// UX ed62580f: shown while the newest open is in flight (F-468).
const OPENING_TEXT = "Opening the audio devices…";
const AUDIO_TYPES = new Set(["noise-start", "sweep-start", "gain", "output-stop",
  "meter-calibration", "resume", "record", "record-cancel"]);

export class App {
  constructor(doc, { io, rc, now } = {}) {
    this.doc = doc;
    this.$ = (id) => doc.getElementById(id);
    this.now = now || (() => performance.now());
    this.flow = new Flow();
    this.io = io || new AudioIO({
      onMeter: (m) => this.apply(this.flow.meter(this.now(), m)),
      onOutput: (m) => this.apply(this.flow.output(m, this.now())),
      onRecorded: (id, samples, startFrame, clock, glitch) => {
        // AE 42dada94 G5: log the render clock glitch with its frames.
        if (glitch) {
          console.warn("web-rc: render clock glitch in a capture: frame " +
            glitch.before + " then " + glitch.after);
        }
        this.apply(this.flow.recorded(id, samples, startFrame, clock, glitch));
      },
      onResumed: (token) => this.apply(this.flow.resumed(token)),
      onError: () => this.apply(this.flow.audioError()),
    });
    this.rc = rc || null;
    this.pipelineError = "";
    this.openError = "";
    this.opening = false;
    this.reportError = "";
    this.devicesKey = null;
    this.devices = [];
    this.limitText = "";
    this.tuningText = "";
    this._renderQueued = false;
    this._plotted = null;
  }

  start() {
    if (!this.rc) {
      try {
        this.rc = new RcClient();
      } catch (e) {
        this._pipelineFailed(e);
      }
    }
    if (this.rc) this.rc.ready.catch((e) => this._pipelineFailed(e));
    this._bind();
    this._listDevices();
    setInterval(() => this._tick(), TICK_MS);
    this.render();
  }

  // -- commands -------------------------------------------------------------

  apply(cmds) {
    for (const cmd of cmds) this._execute(cmd);
    this.queueRender();
  }

  _execute(cmd) {
    if (AUDIO_TYPES.has(cmd.type)) {
      this.io.execute(cmd);
    } else if (cmd.type === "make-sweep") {
      this._call("make_sweep", [cmd.plan.fStartHz, cmd.plan.seconds],
        (s) => this.flow.sweepReady(cmd.token, Float32Array.from(s)),
        (msg) => this.flow.sweepFailed(cmd.token, msg));
    } else if (cmd.type === "analyze") {
      const calibrated = cmd.request.calibrated;
      this._call("analyze", [cmd.request],
        (r) => this.flow.analysisDone(cmd.token, { ...r, calibrated }),
        (msg) => this.flow.analysisFailed(cmd.token, msg));
    } else {
      throw new Error("unknown command " + cmd.type);
    }
  }

  _call(fn, args, done, failed) {
    if (!this.rc) {
      this.apply(failed(this.pipelineError || "The room-correction code is not loaded."));
      return;
    }
    this.rc.call(fn, ...args).then(
      (result) => this.apply(done(result)),
      (e) => this.apply(failed(String(e && e.message || e))),
    );
  }

  _pipelineFailed(e) {
    this.pipelineError = "The room-correction code failed to load: " +
      String(e && e.message || e) + ". Reload the page.";
    this.queueRender();
  }

  // -- devices (AC2, E5) ----------------------------------------------------

  async _listDevices() {
    const md = navigator.mediaDevices;
    if (!md || !md.enumerateDevices) return;
    this.devices = await md.enumerateDevices();
    this.devicesKey = deviceKey(this.devices);
    this.queueRender();
  }

  /** E5a/E5b: any change of the device list stops and resets. */
  async _deviceChange() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const key = deviceKey(devices);
    this.devices = devices;
    if (key === this.devicesKey) {
      this.queueRender();
      return;
    }
    this.devicesKey = key;
    if (this.io.isOpen) {
      this.apply(this.flow.deviceChange(null));
      this.opening = false;       // the close cancels an open in flight
      await this.io.close();
      this.flow.setAudio(null);
    }
    this.queueRender();
  }

  /** Open the chosen devices. Re-opening counts as a switch (E5b). */
  async _open() {
    const micId = this.$("mic").value;
    const sinkId = this.$("sink").value;
    const switched = this.flow.audio !== null;
    if (switched) this.apply(this.flow.deviceChange(null));
    this.opening = true;
    this.queueRender();
    try {
      await this.io.open({ micId, sinkId });
    } catch (e) {
      if (isSuperseded(e)) return;   // the newer open owns the outcome (F-468)
      this.opening = false;
      this.flow.setAudio(null);
      this.openError = "Can't open the audio devices: " +
        String(e && e.message || e);
      this.queueRender();
      return;
    }
    this.opening = false;
    this.openError = "";
    if (switched) this.apply(this.flow.deviceChange(this.io.info()));
    else this.flow.setAudio(this.io.info());
    this.io.execute({ type: "meter-calibration", splOffsetDb: this.flow.splOffsetDb });
    await this._listDevices();  // labels are known once access is granted
  }

  /** AC2b: a rate change while open stops and returns to setup. */
  _checkRates() {
    if (!this.io.isOpen || !this.flow.audio) return;
    const info = this.io.info();
    const a = this.flow.audio;
    if (info.outputRate !== a.outputRate || info.inputRate !== a.inputRate) {
      this.apply(this.flow.rateChange({
        outputRate: info.outputRate, inputRate: info.inputRate,
      }));
    }
  }

  _tick() {
    this._checkRates();
    this.apply(this.flow.tick(this.now()));
  }

  // -- DOM events -----------------------------------------------------------

  _bind() {
    const $ = this.$;
    const on = (id, ev, fn) => $(id).addEventListener(ev, fn);
    const decl = (d) => this.apply(this.flow.setDeclaration(d));

    on("open", "click", () => this._open());
    on("stop", "click", () => this.apply(this.flow.userStop()));
    on("channel", "change", (e) => {
      const v = e.target.value;
      this.apply(this.flow.setChannel(v === "" ? null : Number(v)));
    });
    for (const r of this.doc.querySelectorAll('input[name="role"]')) {
      r.addEventListener("change", () => {
        decl(changeRole(this.flow.decl, r.value));
        this.limitText = String(this.flow.decl.limitHz);
        $("limit").value = this.limitText;
      });
    }
    on("limit", "input", (e) => {
      this.limitText = e.target.value;
      decl(changeLimit(this.flow.decl, parseLimitHz(this.limitText)));
    });
    on("capability", "change", (e) => decl({ ...this.flow.decl,
      capabilityConfirmed: e.target.checked }));
    for (const r of this.doc.querySelectorAll('input[name="enclosure"]')) {
      r.addEventListener("change", () => decl(changeEnclosure(this.flow.decl,
        r.value, this.flow.decl.portTuningHz)));
    }
    on("tuning", "input", (e) => {
      this.tuningText = e.target.value;
      const t = this.tuningText.trim();
      const hz = /^[0-9]+(\.[0-9]+)?$/.test(t) ? Number(t) : null;
      decl(changeEnclosure(this.flow.decl, this.flow.decl.enclosure, hz));
    });
    on("port-confirm", "change", (e) => decl({ ...this.flow.decl,
      portConfirmed: e.target.checked }));

    on("cal-file", "change", async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      const text = await file.text();
      this.apply(this.flow.loadCalibration(file.name, parseCalibration(text), text));
    });
    on("cal-bind", "click", () => this.apply(this.flow.bindCalibration()));
    on("cal-other", "click", () => {
      this.apply(this.flow.clearCalibration());
      $("cal-file").value = "";
      $("cal-file").click();
    });

    on("confirm", "click", () => this.apply(this.flow.confirmSetup()));
    on("ack", "click", () => this.apply(this.flow.acknowledge()));
    for (const b of this.doc.querySelectorAll("button.back")) {
      b.addEventListener("click", () => this.apply(this.flow.backToSetup()));
    }
    on("start", "click", () => this.apply(this.flow.startLevel(this.now())));
    on("again", "click", () => this.apply(this.flow.startLevel(this.now())));
    on("plus", "click", () => this.apply(this.flow.stepUp(this.now())));
    on("measure", "click", () => this.apply(this.flow.measure(this.now())));
    on("report", "click", () => this._downloadReport());

    // 4e STOP on Esc; 4d page hidden; AC11 unsaved work.
    this.doc.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.apply(this.flow.userStop());
    });
    this.doc.addEventListener("visibilitychange", () => {
      this.apply(this.doc.hidden ? this.flow.hidden() : this.flow.visible());
    });
    window.addEventListener("pagehide", () => this.apply(this.flow.hidden()));
    window.addEventListener("pageshow", () => {
      if (!this.doc.hidden) this.apply(this.flow.visible());
    });
    window.addEventListener("beforeunload", (e) => {
      if (this.flow.hasUnsavedWork()) {
        e.preventDefault();
        e.returnValue = "";
      }
    });
    if (navigator.mediaDevices) {
      navigator.mediaDevices.addEventListener("devicechange",
        () => this._deviceChange());
    }
  }

  _download(channel) {
    const d = this.flow.downloads().find((x) => x.channel === channel);
    if (!d) return;
    this._save(new Blob([d.bytes], { type: "audio/wav" }), d.name);
    this.flow.markDownloaded(channel);
    this.queueRender();
  }

  /** AC10: the report for every filter so far, made by report_text. */
  _downloadReport() {
    this.reportError = "";
    this._call("report_text", [reportChannels(this.flow), BASE_SEED],
      (text) => {
        this._save(new Blob([text], { type: "text/plain" }), REPORT_FILE);
        return [];
      },
      (msg) => {
        this.reportError = "The report could not be made: " + msg;
        return [];
      });
  }

  _save(blob, name) {
    const url = URL.createObjectURL(blob);
    const a = this.doc.createElement("a");
    a.href = url;
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  // -- rendering ------------------------------------------------------------

  queueRender() {
    if (this._renderQueued) return;
    this._renderQueued = true;
    requestAnimationFrame(() => {
      this._renderQueued = false;
      this.render();
    });
  }

  render() {
    const $ = this.$;
    const vm = viewModel(this.flow, {
      sinkId: this.io.sinkId,
      sinkLabel: this._label("audiooutput", this.io.sinkId),
      pipelineError: this.pipelineError,
    });
    const text = (id, t) => {
      $(id).textContent = t;
      $(id).hidden = !t;
    };

    $("header").textContent = vm.header;
    text("pipeline-error", vm.pipelineError);
    $("notice").hidden = !vm.notice;
    $("notice-text").textContent = vm.notice;
    text("notice-detail", vm.noticeDetail);
    $("stop").hidden = !vm.stopVisible;
    for (const s of Object.values(STEP)) $("step-" + s).hidden = vm.step !== s;

    // setup
    this._options("mic", "audioinput", "Default microphone");
    this._options("sink", "audiooutput", "Browser default output");
    $("sink").disabled = !("setSinkId" in AudioContext.prototype);
    const lines = $("rate-lines");
    lines.replaceChildren(...vm.setup.rateLines.map((l) => this._li(l)));
    text("open-status", this.opening ? OPENING_TEXT : "");
    text("rate-refusal", vm.setup.rateRefusal || this.openError || "");
    this._channelOptions(vm.setup.channels, vm.setup.channel);
    for (const r of this.doc.querySelectorAll('input[name="role"]')) {
      r.checked = r.value === vm.setup.role;
    }
    const limit = $("limit");
    limit.disabled = !vm.setup.role;
    if (!vm.setup.role) limit.value = this.limitText = "";
    text("limit-error", this._limitError());
    $("capability").checked = vm.setup.capabilityConfirmed;
    $("capability").disabled = !vm.setup.capabilityText;
    $("capability-text").textContent = vm.setup.capabilityText ||
      "Choose the speaker and its low limit first.";
    for (const r of this.doc.querySelectorAll('input[name="enclosure"]')) {
      r.checked = r.value === vm.setup.enclosure;
    }
    $("tuning-row").hidden = vm.setup.enclosure !== "ported";
    if (vm.setup.enclosure !== "ported") $("tuning").value = this.tuningText = "";
    text("port-warning", vm.setup.portWarning);
    $("port-confirm-row").hidden = !vm.setup.portWarning;
    $("port-confirm").checked = vm.setup.portConfirmed;
    $("port-confirm-text").textContent = vm.setup.portConfirmText;

    text("cal-status", vm.setup.calStatus);
    $("cal-unbound").hidden = !vm.setup.calUnbound;
    $("cal-unbound-text").textContent = vm.setup.calUnbound;
    $("cal-bind").textContent = vm.setup.calFile
      ? "Use " + vm.setup.calFile + " for this microphone" : "";
    text("cal-gain-note", vm.setup.calGainNote);
    text("deep-bass-hint", vm.setup.deepBassHint);
    $("problems").replaceChildren(...vm.setup.problems.map((p) => this._li(p)));
    $("confirm").disabled = !vm.setup.canConfirm;

    // 4a
    $("ack-title").textContent = vm.ack.title;
    $("ack-intro").textContent = vm.ack.intro;
    this._ackItems(vm.ack.items, vm.ack.ticked);
    $("ack").textContent = vm.ack.button;
    $("ack").disabled = !vm.ack.canAcknowledge;

    // level check
    $("uncal-banner").hidden = !vm.level.banner;
    $("uncal-banner-text").textContent = vm.level.banner;
    $("uncal-banner-reason").textContent = vm.level.bannerReason;
    $("band-label").textContent = vm.level.bandLabel;
    $("mic-level").textContent = vm.level.micLevel;
    $("cap").textContent = vm.level.cap;
    $("safety-limit").textContent = vm.level.safetyLimit;
    $("plus").textContent = vm.level.plusLabel;
    $("start").disabled = !vm.level.canStart;
    $("again").disabled = !vm.level.canStart;
    $("plus").disabled = !vm.level.canStepUp;
    $("measure").disabled = !vm.level.canMeasure;
    text("target-text", vm.level.targetText);
    text("hold-text", vm.level.holdText);
    text("again-hold-text", vm.level.holdText);

    // measure, result
    $("progress").textContent = vm.measure.progress;
    $("ready").textContent = vm.result.ready;
    $("result-channel").textContent = vm.result.channel;
    text("result-uncal", vm.result.uncalibrated);
    $("delay").textContent = vm.result.delay;
    $("prediction").textContent = vm.result.prediction;
    if (vm.step === STEP.RESULT) this._plots(vm.result.plots);
    $("report").disabled = vm.result.downloads.length === 0;
    text("report-error", this.reportError);
    $("pi-note").textContent = vm.result.piNote;
    $("downloads").replaceChildren(...vm.result.downloads.map((d) => {
      const li = this.doc.createElement("li");
      const b = this.doc.createElement("button");
      b.type = "button";
      b.textContent = "Download " + d.name;
      b.addEventListener("click", () => this._download(d.channel));
      li.append(b);
      if (d.mark) li.append(" (" + d.mark + ")");
      return li;
    }));
  }

  /** E5c inline: only the low-limit errors, at the field. */
  _limitError() {
    const role = this.flow.decl.role;
    if (!role || this.limitText.trim() === "") return "";
    const errors = checkDeclaration(this.flow.decl).errors;
    const own = [limitRangeText(role)];
    if (role === ROLE.SUBWOOFER) own.push(SUB_LIMIT_REFUSAL);
    return errors.find((e) => own.includes(e)) || "";
  }

  _label(kind, id) {
    const d = this.devices.find((x) => x.kind === kind && x.deviceId === id);
    return d ? d.label : "";
  }

  /** One checkbox per 4a item; rebuilt only when the texts change. */
  _ackItems(items, ticked) {
    const ul = this.$("ack-items");
    const have = [...ul.querySelectorAll("span")].map((s) => s.textContent);
    if (have.join("\n") !== items.join("\n")) {
      ul.replaceChildren(...items.map((t, i) => {
        const li = this.doc.createElement("li");
        const label = this.doc.createElement("label");
        const box = this.doc.createElement("input");
        box.type = "checkbox";
        box.id = "ack-item-" + i;
        box.addEventListener("change", () => {
          this.apply(this.flow.tickAck(i, box.checked));
        });
        const span = this.doc.createElement("span");
        span.textContent = t;
        label.append(box, " ", span);
        li.append(label);
        return li;
      }));
    }
    ul.querySelectorAll("input").forEach((box, i) => { box.checked = ticked[i]; });
  }

  _li(t) {
    const li = this.doc.createElement("li");
    li.textContent = t;
    return li;
  }

  _options(id, kind, defaultLabel) {
    const sel = this.$(id);
    const want = [["", defaultLabel], ...this.devices
      .filter((d) => d.kind === kind && d.deviceId && d.deviceId !== "default")
      .map((d, i) => [d.deviceId, d.label || kind + " " + (i + 1)])];
    const have = [...sel.options].map((o) => [o.value, o.textContent]);
    if (JSON.stringify(want) === JSON.stringify(have)) return;
    const keep = sel.value;
    sel.replaceChildren(...want.map(([v, l]) => new Option(l, v)));
    if (want.some(([v]) => v === keep)) sel.value = keep;
  }

  /** AC11 plots; redrawn only for a new result or a new page width. */
  _plots(plots) {
    const key = [this.flow.run.result, this.$("plot-measured").clientWidth];
    if (!plots || (this._plotted && key.every((k, i) => k === this._plotted[i]))) {
      return;
    }
    this._plotted = key;
    const css = getComputedStyle(this.doc.documentElement);
    const v = (name) => css.getPropertyValue(name).trim();
    const colors = {
      bg: v("--bg-spectrum"), grid: v("--border"), label: v("--text-label"),
      line: v("--text"), ok: v("--safe"), over: v("--danger"),
      unchecked: v("--text-micro"), target: v("--text-dim"),
      measured: v("--accent"), predicted: v("--primary"),
    };
    const m = plots.measured;
    const rate = plots.impulse.sampleRate;
    const renderer = window.PiAudioSpectrumRenderer.create({
      dbMin: MEASURED_DB[0], dbMax: MEASURED_DB[1], freqLo: m.freqs[0],
      freqHi: m.freqs[m.freqs.length - 1], fftSize: MEASURED_FFT,
      sampleRate: rate, peakHold: false, autoRange: false,
    });
    renderer.init("plot-measured");
    renderer.render(curveToBins(m.freqs, m.db, MEASURED_FFT, rate,
      MEASURED_DB[0]), true);
    this.$("plot-measured-caption").textContent = m.caption;
    this._draw("plot-impulse", drawImpulse, plots.impulse, colors);
    this._draw("plot-repeatability", drawRepeatability, plots.repeatability,
      colors);
    this.$("plot-prediction-figure").hidden = !plots.prediction;
    this.$("plot-prediction-none").hidden = !plots.noPrediction;
    this.$("plot-prediction-none").textContent = plots.noPrediction;
    if (plots.prediction) {
      this._draw("plot-prediction", drawPrediction, plots.prediction, colors);
    }
  }

  _draw(id, draw, plot, colors) {
    const canvas = this.$(id);
    const r = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.floor(r.width * dpr);
    canvas.height = Math.floor(r.height * dpr);
    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw(ctx, r.width, r.height, plot, colors);
    this.$(id + "-caption").textContent = plot.caption;
  }

  _channelOptions(channels, current) {
    const sel = this.$("channel");
    const want = [["", "Choose…"], ...channels.map((c) => [String(c),
      channelLabel(c)])];
    const have = [...sel.options].map((o) => [o.value, o.textContent]);
    if (JSON.stringify(want) !== JSON.stringify(have)) {
      sel.replaceChildren(...want.map(([v, l]) => new Option(l, v)));
    }
    sel.value = current === null ? "" : String(current);
  }
}

if (typeof window !== "undefined" && !window.__webrcNoAutostart) {
  const go = () => {
    window.__webrcApp = new App(document);
    window.__webrcApp.start();
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", go);
  } else {
    go();
  }
}
