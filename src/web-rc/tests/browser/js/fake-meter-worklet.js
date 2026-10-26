// fake-meter-worklet.js -- a test stand-in for the meter's side of
// stop-latch.js (latch r2 A4, C1, C5): writes the heartbeat and trips the
// latch on a schedule, so the output worklet can be tested without a mic.
// It imports the same stop-latch.js URL as the real worklets, so it shares
// their module instance.
//
// processorOptions (frames; all optional):
//   from, until   beat while from <= currentFrame < until (default: always)
//   trip          { at, cause, until }  trip every quantum in [at, until)
//   bad           { at, kind }  from `at` on, write a bad beat instead:
//                 "nan", "repeat" (the last good beat) or "decrease"

import { stopLatch } from "../../../static/js/stop-latch.js";

class FakeMeter extends AudioWorkletProcessor {
  constructor(options) {
    super();
    const o = (options && options.processorOptions) || {};
    this.from = o.from ?? 0;
    this.until = o.until ?? Infinity;
    this.tripAt = o.trip || null;
    this.bad = o.bad || null;
  }

  process() {
    const f = currentFrame;
    const t = this.tripAt;
    if (t && f >= t.at && f < (t.until ?? Infinity)) stopLatch.trip(t.cause);
    if (f >= this.from && f < this.until) {
      let v = f;
      if (this.bad && f >= this.bad.at) {
        v = { nan: NaN, repeat: stopLatch.beatFrame, decrease: f - 1000 }[this.bad.kind];
      }
      stopLatch.beat(v);
    }
    return true;
  }
}

registerProcessor("webrc-test-beater", FakeMeter);
