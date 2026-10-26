// Tiny assertion helpers for the web-rc JS units.

export function assert(cond, msg) {
  if (!cond) throw new Error("assertion failed: " + (msg || ""));
}

export function eq(actual, expected, msg) {
  if (!Object.is(actual, expected)) {
    throw new Error((msg ? msg + ": " : "") + "expected " +
      JSON.stringify(expected) + ", got " + JSON.stringify(actual));
  }
}

export function close(actual, expected, tol, msg) {
  if (!(Math.abs(actual - expected) <= tol)) {
    throw new Error((msg ? msg + ": " : "") + "expected " + expected +
      " +- " + tol + ", got " + actual);
  }
}

export function throws(fn, msg) {
  try {
    fn();
  } catch (e) {
    return e;
  }
  throw new Error("expected an exception: " + (msg || ""));
}
