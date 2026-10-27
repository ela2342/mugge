// stop-latch.js -- the meter-to-output auto-STOP path on the render thread
// (US-179 E3/E4, Architect note b: a meter stop must not depend on the main
// thread). Latch ruling: Architect r2 9a6db097, AE release 6f220842.
//
// meter-worklet.js and output-worklet.js both import this module. Their
// processors run in the context's one AudioWorkletGlobalScope, so they share
// this module instance: the meter trips the latch in the quantum it sees a
// stop cause, and the output processor reads it at the start of its next
// process() call and starts its STOP ramp (4e). No message hop. The meter
// tells the main thread in parallel, through its normal report.
//
// Epochs (r2 A1-A3): constructing an output processor is the only way to
// arm a new epoch; nothing clears a trip on an existing node. A trip stops
// every output armed at or before the current epoch; a node whose epoch is
// older than the current one stops too (it should already be gone: the main
// thread disconnects the old node before it builds a new one). A trip from
// before an output was armed does not stop it, but a cause still held trips
// the new epoch, because the meter re-reports it every quantum.
//
// Heartbeat (r2 A4): the meter writes its beat count here every process(),
// after it has evaluated its stop conditions: its own counter, +1 per call,
// not currentFrame (Architect 3fb4cd0c B1: the browser can stamp two quanta
// with the same frame). A new output plays nothing until it has seen a beat
// written after its construction, and it stops if the beats go stale
// (OutputGate).
//
// Scope (r2 A5): this state lives only as long as the AudioContext. A new
// context starts with an empty latch; nothing may rely on trip memory
// surviving a context.

export const LATCH = Object.freeze({
  STALE_QUANTA: 4,          // no new beat for this many quanta = stale
  HEARTBEAT: "heartbeat",   // stop cause: the meter's beats are missing or bad
  SUPERSEDED: "superseded", // stop cause: a newer output was armed
});

export class StopLatch {
  constructor() {
    this.epoch = 0;
    this.trippedEpoch = 0;
    this.cause = null;
    this.beatCount = null;    // the last good beat, null = never written
    this.beatFault = false;   // a non-finite or non-increasing beat was written
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
    if (this.epoch === 0) return false;
    return epoch < this.epoch || this.trippedEpoch >= epoch;
  }

  /** The meter's heartbeat. A bad beat is a fault for the whole scope. */
  beat(count) {
    if (!Number.isFinite(count) ||
        (this.beatCount !== null && !(count > this.beatCount))) {
      this.beatFault = true;
      return;
    }
    this.beatCount = count;
  }
}

/**
 * The render-thread gate of one output processor (r2 A1, A3, A4). Construct
 * it in the processor's constructor (it arms the epoch) and call check()
 * once per quantum before rendering.
 */
export class OutputGate {
  constructor(latch) {
    this.latch = latch;
    this.epoch = latch.arm();
    this.lastBeat = latch.beatCount;  // beats up to here predate this node
    this.fresh = false;
    this.quiet = 0;
    this.cause = null;                // the stop cause, once stopped
  }

  /**
   * Returns { stop, play }: stop is true in the one quantum the gate stops
   * the node (this.cause names why); play is false while the node must
   * output zeros without advancing (no fresh beat seen yet, not stopped).
   */
  check() {
    if (this.cause !== null) return { stop: false, play: true };
    const l = this.latch;
    const b = l.beatCount;
    let beatBad = l.beatFault;
    if (!beatBad) {
      if (b !== null && (this.lastBeat === null || b > this.lastBeat)) {
        this.lastBeat = b;
        this.fresh = true;
        this.quiet = 0;
      } else if (b !== null && this.lastBeat !== null && b < this.lastBeat) {
        beatBad = true;
      } else if (++this.quiet >= LATCH.STALE_QUANTA) {
        beatBad = true;
      }
    }
    if (l.tripped(this.epoch)) {
      this.cause = l.epoch > this.epoch ? LATCH.SUPERSEDED : l.cause;
    } else if (beatBad) {
      this.cause = LATCH.HEARTBEAT;
    }
    if (this.cause !== null) return { stop: true, play: true };
    return { stop: false, play: this.fresh };
  }
}

/** The instance shared by the worklet processors. */
export const stopLatch = new StopLatch();
