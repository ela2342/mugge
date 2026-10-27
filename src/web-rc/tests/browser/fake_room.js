// fake_room.js -- a simulated 48 kHz room for the web-rc E2E test (US-179).
//
// Loaded as a Playwright init script, before the page's own code. The page
// runs unchanged; only the browser APIs at its edges are replaced:
//
//   getUserMedia      the fake mic's track reports 48 kHz (Chromium's fake
//                     device runs at 44.1 kHz with the DSP flags off)
//   AudioContext      a context opened on the room's sink runs at 48 kHz
//                     (the fake output devices run at 44.1 kHz)
//   createMediaStreamSource
//                     in a context on the room's sink, the mic is the room:
//                     what the page sends to window.__room.channel of the
//                     destination, through the taps [delay samples, gain],
//                     plus a noise floor
//
// Everything stays in the page's one context and one render graph, so the
// room adds exactly the tap delays: the delay the page reports is the
// first tap's, to the sample. A context on any other sink hears nothing.
// The room is silent again after each suspension of the context.
//
// window.__room (set by the test before the page loads):
//   { sinkLabel, channel, taps: [[samples, gain], ...], noiseRms }
// The script adds: sinkId (resolved from sinkLabel), contexts (the opts of
// every AudioContext the page made), live (those contexts themselves, in
// the same order), heard (contexts given the room).

(() => {
  const room = window.__room;
  room.contexts = [];
  room.live = [];
  room.heard = 0;
  const RATE = 48000;
  const md = navigator.mediaDevices;

  const gum = md.getUserMedia.bind(md);
  md.getUserMedia = async (constraints) => {
    const stream = await gum(constraints);
    for (const track of stream.getAudioTracks()) {
      const settings = track.getSettings.bind(track);
      track.getSettings = () => ({ ...settings(), sampleRate: RATE });
    }
    return stream;
  };

  const enumerate = md.enumerateDevices.bind(md);
  async function roomSinkId() {
    // Labels (and ids) are known only once the mic is granted.
    if (!room.sinkId) {
      const d = (await enumerate()).find((x) => x.kind === "audiooutput" &&
        x.label === room.sinkLabel);
      room.sinkId = d ? d.deviceId : null;
    }
    return room.sinkId;
  }
  md.enumerateDevices = async () => {
    const devices = await enumerate();
    await roomSinkId();
    return devices;
  };

  const Native = window.AudioContext;
  class RoomContext extends Native {
    constructor(opts = {}) {
      const ours = !!opts.sinkId && opts.sinkId === room.sinkId;
      super(ours ? { ...opts, sampleRate: RATE } : opts);
      this.__ours = ours;
      room.contexts.push({ sinkId: opts.sinkId || "", rate: this.sampleRate });
      room.live.push(this);
    }
  }
  window.AudioContext = RoomContext;

  const connect = AudioNode.prototype.connect;
  AudioNode.prototype.connect = function (dest, ...rest) {
    const r = connect.call(this, dest, ...rest);
    if (dest instanceof AudioDestinationNode && dest.context.__roomIn) {
      connect.call(this, dest.context.__roomIn);
    }
    return r;
  };

  const source = Native.prototype.createMediaStreamSource;
  RoomContext.prototype.createMediaStreamSource = function (stream) {
    if (!this.__ours) return source.call(this, stream);
    room.heard += 1;
    const n = this.destination.maxChannelCount;
    const split = new ChannelSplitterNode(this, { numberOfOutputs: n });
    const mic = new GainNode(this, { channelCount: 1,
      channelCountMode: "explicit" });
    // A suspended context stops the render clock, not the room: what was in
    // flight has decayed by the time it resumes (the suspensions here are
    // far longer than the last tap). Fresh delay lines on every suspend;
    // the swap lands before the next rendered quantum.
    let taps = [];
    const build = () => {
      for (const n of taps) n.disconnect();
      taps = [];
      for (const [samples, gain] of room.taps) {
        const g = new GainNode(this, { gain });
        const d = new DelayNode(this, { maxDelayTime: 1,
          delayTime: samples / RATE });
        connect.call(split, g, room.channel);
        connect.call(g, d);
        connect.call(d, mic);
        taps.push(g, d);
      }
    };
    build();
    this.addEventListener("statechange", () => {
      if (this.state === "suspended") build();
    });
    // A deterministic noise floor, so silence is not digital zero.
    const buf = new AudioBuffer({ length: 7 * RATE + 13, sampleRate: RATE });
    const x = buf.getChannelData(0);
    let s = 12345;
    for (let i = 0; i < x.length; i++) {
      s = (s * 1103515245 + 12345) >>> 0;
      x[i] = ((s / 4294967296) - 0.5) * Math.sqrt(12) * room.noiseRms;
    }
    const noise = new AudioBufferSourceNode(this, { buffer: buf, loop: true });
    connect.call(noise, mic);
    noise.start();
    this.__roomIn = split;
    return mic;
  };
})();
