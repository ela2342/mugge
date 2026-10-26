// rc-client.js -- page-side handle on rc-worker.js (US-179).
//
//   const rc = new RcClient();
//   await rc.ready;                      // rejects if Pyodide fails to load
//   const sweep = await rc.call("make_sweep", 40, 6);
//
// call() resolves with the result or rejects with an RcError whose kind is
// "rejected" (a capture failed closed, AC7) or "error".

export class RcError extends Error {
  constructor(kind, message) {
    super(message);
    this.name = "RcError";
    this.kind = kind;
  }
}

export class RcClient {
  constructor(url = new URL("./rc-worker.js", import.meta.url)) {
    this.worker = new Worker(url, { type: "module" });
    this.nextId = 1;
    this.pending = new Map();
    this.ready = new Promise((resolve, reject) => {
      this._ready = { resolve, reject };
    });
    this.worker.onmessage = (event) => this._onMessage(event.data);
    this.worker.onerror = (event) => {
      const err = new RcError("error", "worker error: " + (event.message || "unknown"));
      this._ready.reject(err);
      for (const { reject } of this.pending.values()) reject(err);
      this.pending.clear();
    };
  }

  _onMessage(msg) {
    if (msg.type === "ready") {
      this._ready.resolve();
      return;
    }
    if (msg.type === "failed") {
      this._ready.reject(new RcError("error", msg.message));
      return;
    }
    const p = this.pending.get(msg.id);
    if (!p) return;
    this.pending.delete(msg.id);
    if (msg.ok) p.resolve(msg.result);
    else p.reject(new RcError(msg.kind, msg.message));
  }

  call(fn, ...args) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.worker.postMessage({ id, fn, args });
    });
  }

  terminate() {
    this.worker.terminate();
  }
}
