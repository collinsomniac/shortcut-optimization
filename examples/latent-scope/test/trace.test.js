import assert from "node:assert/strict";
import { test } from "node:test";
import { startTrace, recordToken } from "../src/trace.js";

test("exported observation keeps the sampled token, returned rivals, and timing", () => {
  const messages=[{role:"user",content:"Hello"}];
  const trace=startTrace({model:"m",prompt:"Hello",messages,settings:{temperature:.8},startedAt:"2026-01-01T00:00:00Z"});
  messages[0].content="later edit";
  recordToken(trace,{token:" world",logprob:Math.log(.3),top_logprobs:[{token:" there",logprob:Math.log(.6)}]},83.6);
  assert.equal(trace.messages[0].content,"Hello");
  assert.equal(trace.tokens[0].elapsedMs,84);
  assert.equal(trace.tokens[0].token," world");
  assert.equal(trace.tokens[0].topLogprobs[0].token," there");
  assert.equal(trace.source,"webllm-chat-logprobs");
  assert.equal(JSON.parse(JSON.stringify(trace)).tokens.length,1);
});
