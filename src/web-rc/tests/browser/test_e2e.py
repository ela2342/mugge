"""One channel measured end to end in the browser (US-179 AC11).

The assembled page, unchanged, in Chromium with a simulated 48 kHz room
(fake_room.js) on a named output device: setup, a calibration file, the
safety acknowledgement, the level check, both sweeps, the Pyodide
analysis, the result step, the WAV and the report. The room hears only
output channel 2 of that device, through a direct sound and one
reflection, so the delay the page reports is the room's to the sample.

What this pins in app.js (the wiring the unit tests can't see):
- the recording's start frame and clock reach flow.recorded(): a wrong
  frame moves the reported delay, a missing one is an audio error;
- the calibration file's text reaches the analysis: its curve shows in
  the measured response;
- the chosen output device opens the context (sinkId);
- the report button saves report_text's file.
"""

import json
from pathlib import Path

import pytest
from playwright.sync_api import expect

from .test_page import FAKE_MEDIA, page_url  # noqa: F401 (fixture)

ROOM_JS = (Path(__file__).parent / "fake_room.js").read_text()

RATE = 48000
SINK = "Fake Audio Output 2"
CHANNEL = 1                      # "Output 2"
DIRECT = 1200                    # samples: 25 ms
REFLECTION = (DIRECT + 2400, 0.25)
NOISE_RMS = 1e-4                 # -80 dBFS
CAL_STEP_DB = 6.0
# A UMIK-1 style file: Sens Factor 0 dB, the mic reads CAL_STEP_DB hot
# from 100 Hz up; the analysis takes that off the measured response.
CAL_TEXT = (
    '"Sens Factor =0.000dB, SERNO: 0000001"\n'
    "10\t0.0\n90\t0.0\n110\t{s:.1f}\n20000\t{s:.1f}\n".format(s=CAL_STEP_DB))


# F-468: holds the first `n` meter worklet addModule() calls, the k-th until
# __hold.release(k); __hold.reached counts the calls held so far.
HOLD_METERS_JS = """((n) => {
  const add = AudioWorklet.prototype.addModule;
  const releases = [];
  window.__hold = { reached: 0, release: (k) => releases[k]() };
  AudioWorklet.prototype.addModule = function (url, ...rest) {
    if (window.__hold.reached >= n || !String(url).endsWith("/meter-worklet.js")) {
      return add.call(this, url, ...rest);
    }
    window.__hold.reached += 1;
    return new Promise((resolve, reject) => {
      releases.push(() => add.call(this, url, ...rest).then(resolve, reject));
    });
  };
})(%d);
"""


@pytest.fixture()
def room_page(browser_type):
    browser = browser_type.launch(args=FAKE_MEDIA)
    context = browser.new_context(accept_downloads=True)
    room = {"sinkLabel": SINK, "channel": CHANNEL,
            "taps": [[DIRECT, 1.0], list(REFLECTION)], "noiseRms": NOISE_RMS}
    context.add_init_script("window.__room = " + json.dumps(room) + ";\n" +
                            ROOM_JS)
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    yield page, errors
    browser.close()


def _level_check(page):
    """Start, then "+" until the target is reached; the meter decides."""
    page.click("#start")
    for _ in range(12):
        page.wait_for_timeout(600)
        lc = page.evaluate("""() => { const lc = window.__webrcApp.flow.run.lc;
            return lc && { running: lc.running, reached: lc.targetReached }; }""")
        assert lc and lc["running"], page.text_content("#notice")
        if lc["reached"]:
            return
        page.click("#plus")
    pytest.fail("level target not reached: " + page.text_content("#mic-level"))


def test_one_channel_end_to_end(room_page, page_url, tmp_path):  # noqa: F811
    page, errors = room_page
    page.goto(page_url)
    page.wait_for_function("window.__webrcApp !== undefined")

    # Open once for the device labels, then choose the room's output.
    page.click("#open")
    expect(page.locator("#sink option", has_text=SINK)).to_have_count(1)
    page.select_option("#sink", label=SINK)
    page.click("#open")
    page.wait_for_function("window.__room.heard === 1")
    expect(page.locator("#rate-lines li")).to_have_text([
        "Sample rate: 48000 Hz (output)", "Sample rate: 48000 Hz (input)"])
    sink_id = page.evaluate("window.__room.sinkId")
    # The page's open context is on the room's output (F-468: not just the
    # last one made), and every other context it made is closed.
    active = page.evaluate("""() => { const io = window.__webrcApp.io;
        return { sinkId: io.sinkId, rate: io.ctx && io.ctx.sampleRate,
                 others: window.__room.live.filter((c) => c !== io.ctx)
                     .map((c) => c.state) }; }""")
    assert sink_id and active["sinkId"] == sink_id and active["rate"] == RATE, (
        active)
    assert all(s == "closed" for s in active["others"]), active
    assert page.evaluate("window.__room.heard") == 1

    page.select_option("#channel", str(CHANNEL))
    page.check("input[name=role][value=subwoofer]")
    page.fill("#limit", "40")
    page.check("#capability")
    page.check("input[name=enclosure][value=closed]")
    page.set_input_files("#cal-file", files=[{
        "name": "mic-cal.txt", "mimeType": "text/plain",
        "buffer": CAL_TEXT.encode()}])
    expect(page.locator("#cal-gain-note")).to_be_visible()
    expect(page.locator("#problems li")).to_have_count(0)
    page.click("#confirm")

    expect(page.locator("#ack-items li").nth(3)).to_contain_text(
        f'Sound plays on "{SINK}".')
    boxes = page.locator("#ack-items input[type=checkbox]")
    for i in range(4):
        boxes.nth(i).check()
    page.click("#ack")
    expect(page.locator("#uncal-banner")).to_be_hidden()

    _level_check(page)
    page.click("#measure")
    expect(page.locator("#step-measure")).to_be_visible()
    # Two captures of 0.5 + 10 + 1 s in real time, then the analysis.
    page.wait_for_function("""() => { const f = window.__webrcApp.flow;
        return f.step === "result" || f.notice !== null; }""", timeout=180_000)
    assert page.evaluate("window.__webrcApp.flow.notice") is None, (
        page.evaluate("window.__webrcApp.flow.notice"))
    expect(page.locator("#step-result")).to_be_visible()

    r = page.evaluate("""() => { const r = window.__webrcApp.flow.run.result;
        const m = r.measured;
        return { delayS: r.delayS, calibrated: r.calibrated,
                 onsets: window.__webrcApp.flow.filters.size,
                 freqs: Array.from(m.freqs), db: Array.from(m.db) }; }""")
    # The delay is the room's direct sound, to within a sample, whichever
    # quantum each output started in (AE a1736914; onsets up to 384).
    assert r["delayS"] * RATE == pytest.approx(DIRECT, abs=1), r["delayS"]
    expect(page.locator("#delay")).to_contain_text(
        f"{1000 * DIRECT / RATE:.1f} ms")
    assert r["calibrated"] is True
    expect(page.locator("#result-uncal")).to_be_hidden()

    # The calibration's step, taken off: the band above 100 Hz reads
    # CAL_STEP_DB lower than below it (the room itself is flat there,
    # apart from the reflection's ripple).
    def mean_db(lo, hi):
        v = [d for f, d in zip(r["freqs"], r["db"]) if lo <= f <= hi]
        assert v, (lo, hi, r["freqs"][:3], r["freqs"][-3:])
        return sum(v) / len(v)

    step = mean_db(130, 190) - mean_db(35, 75)
    assert step == pytest.approx(-CAL_STEP_DB, abs=1.5), step

    downloads = page.locator("#downloads button")
    expect(downloads).to_have_text(
        ["Download combined_ch2-sub-browser-generated.wav"])
    with page.expect_download() as dl:
        downloads.first.click()
    wav = tmp_path / "filter.wav"
    dl.value.save_as(wav)
    assert dl.value.suggested_filename == "combined_ch2-sub-browser-generated.wav"
    assert wav.read_bytes()[:4] == b"RIFF"

    with page.expect_download() as dl:
        page.click("#report")
    report = tmp_path / "report.txt"
    dl.value.save_as(report)
    text = report.read_text()
    for line in ("Channel Output 2 (channel_index 1)", "  Role: Subwoofer",
                 "  File: combined_ch2-sub-browser-generated.wav",
                 "  Low limit: 40 Hz, subsonic HPF at 32 Hz",
                 "  Enclosure: closed", "  Mic calibration: yes",
                 "  Delay (audio latency + time of flight): "
                 f"{1000 * DIRECT / RATE:.1f} ms"):
        assert line + "\n" in text, (line, text)
    assert errors == []


def test_open_race_newest_open_wins(room_page, page_url):  # noqa: F811
    """F-468 (run 11): two opens in flight, the older one finishing last.

    The order is forced, not timed: the first open's meter worklet module
    is held until the second open has committed. Meanwhile a devicechange,
    as Chromium sends once the mic is granted, lists the labels early, so
    the room's output can be chosen while the first open is still waiting.
    The page must end on the newer choice, with the older context closed.
    """
    page, errors = room_page
    # Playwright's routing does not see worklet module fetches: hold the
    # first meter addModule() in the page instead.
    page.add_init_script(HOLD_METERS_JS % 1)
    page.goto(page_url)
    page.wait_for_function("window.__webrcApp !== undefined")

    # addModule() comes after getUserMedia: the mic is granted once held.
    page.click("#open")
    page.wait_for_function("window.__hold.reached === 1")
    page.evaluate(
        "navigator.mediaDevices.dispatchEvent(new Event('devicechange'))")
    expect(page.locator("#sink option", has_text=SINK)).to_have_count(1)
    page.select_option("#sink", label=SINK)
    page.click("#open")
    sink_id = page.evaluate("window.__room.sinkId")
    assert sink_id
    page.wait_for_function("(id) => window.__webrcApp.io.sinkId === id",
                           arg=sink_id)

    page.evaluate("window.__hold.release(0)")
    # The first open is done once it has committed or closed its context.
    page.wait_for_function("""() => { const c = window.__room.live[0];
        return window.__webrcApp.io.ctx === c || c.state === "closed"; }""")
    page.wait_for_function("window.__webrcApp.flow.audio !== null")
    state = page.evaluate("""() => { const app = window.__webrcApp;
        const io = app.io, room = window.__room, live = room.live;
        const text = (id) => { const e = document.getElementById(id);
            return e && !e.hidden ? e.textContent : ""; };
        return { sinkId: io.sinkId, rate: io.ctx && io.ctx.sampleRate,
                 newest: io.ctx === live[live.length - 1],
                 others: live.filter((c) => c !== io.ctx).map((c) => c.state),
                 mics: room.streams.filter((s) => s !== io.stream).map(
                     (s) => s.getTracks().map((t) => t.readyState).join()),
                 flowSink: app.flow.audio.sinkId,
                 openError: text("rate-refusal"),
                 opening: text("open-status") }; }""")
    # QE 390b9cd8 T3, in order: the newer choice, no leaked context, no
    # leaked mic, no error text.
    assert (state["sinkId"], state["rate"]) == (sink_id, RATE), state
    assert state["newest"] and state["flowSink"] == sink_id, state
    assert state["others"] == ["closed"], state
    assert state["mics"] == ["ended"], state
    assert state["openError"] == "" and state["opening"] == "", state
    assert errors == []
