// stop-latch.js -- the meter-to-output auto-STOP path on the render thread
// (US-179 E3/E4, Architect note b: a meter stop must not depend on the main
// thread).
//
// meter-worklet.js and output-worklet.js both import this module. Their
// processors run in the context's one AudioWorkletGlobalScope, so they share
// this module instance: the meter trips the latch in the quantum it sees a
// stop cause, and the output processor reads it at the start of its next
// process() call and starts its STOP ramp (4e). No message hop. The meter
// tells the main thread in parallel, through its normal report.
//
// Each output processor arms the latch when it is constructed and keeps the
// epoch it got. A trip stops every output armed at or before the current
// epoch; a trip from before an output was armed does not stop it (the main
// thread starts outputs only after it has handled earlier stops).

export class StopLatch {
  constructor() {
    this.epoch = 0;
    this.trippedEpoch = 0;
    this.cause = null;
  }

  /** A new output starts: returns its epoch. */
  arm() {
    this.epoch += 1;
    this.cause = null;
    return this.epoch;
  }

  /** The meter saw a stop cause. */
  trip(cause) {
    if (this.trippedEpoch !== this.epoch) {
      this.trippedEpoch = this.epoch;
      this.cause = cause;
    }
  }

  /** Must the output armed at `epoch` stop? */
  tripped(epoch) {
    return this.epoch > 0 && this.trippedEpoch >= epoch;
  }
}

/** The instance shared by the worklet processors. */
export const stopLatch = new StopLatch();
