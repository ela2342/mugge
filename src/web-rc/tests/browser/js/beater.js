// Test helper: add the fake meter heartbeat (fake-meter-worklet.js) to an
// offline context, before any output node is built.

const BEATER = new URL("./fake-meter-worklet.js", import.meta.url);

export async function addBeater(ctx, options = {}) {
  await ctx.audioWorklet.addModule(BEATER);
  const node = new AudioWorkletNode(ctx, "webrc-test-beater", {
    numberOfInputs: 0, numberOfOutputs: 1, outputChannelCount: [1],
    processorOptions: options,
  });
  node.connect(ctx.destination);
  return node;
}
