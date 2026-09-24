import assert from "node:assert/strict";
import { test } from "node:test";
import { decodeChoice } from "../src/signal.js";

test("chosen token is not duplicated and remaining mass is accounted for", () => {
  const x = decodeChoice({ token:" blue", logprob:Math.log(.6), top_logprobs:[
    {token:" blue",logprob:Math.log(.6)}, {token:" red",logprob:Math.log(.2)},
    {token:" green",logprob:Math.log(.1)}
  ]});
  assert.deepEqual(x.alternatives.map(v=>v.token),[" red"," green"]);
  assert.ok(Math.abs(x.remaining-.1)<1e-7);
  assert.ok(Math.abs(x.row.reduce((a,b)=>a+b,0)-1)<1e-7);
});

test("sampled token outside top five stays first and leftover alternatives remain distinct", () => {
  const x = decodeChoice({ token:" rare", logprob:Math.log(.01), top_logprobs:
    [".1",".2",".3",".4",".5"].map((t,i)=>({token:t,logprob:Math.log(.25-i*.04)}))
  });
  assert.equal(x.row.length,7);
  assert.equal(x.chosen.token," rare");
  assert.equal(x.alternatives.length,5);
  assert.ok(x.remaining>0);
});

test("missing data does not fabricate confidence", () => {
  const x=decodeChoice({token:"x",logprob:NaN,top_logprobs:[]});
  assert.equal(x.chosen.probability,0);
  assert.equal(x.remaining,1);
  assert.equal(x.entropy,0);
});
