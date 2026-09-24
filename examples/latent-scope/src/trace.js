// A trace contains returned observations, not inferred hidden states.
export function startTrace({ model, prompt, messages, settings, startedAt }) {
  return {
    schemaVersion: 1, source: "webllm-chat-logprobs", model, startedAt, prompt,
    messages: messages.map(({ role, content }) => ({ role, content })),
    settings: { ...settings }, tokens: [], output: "", status: "running"
  };
}

export function recordToken(trace, log, elapsedMs) {
  trace.tokens.push({
    index: trace.tokens.length, elapsedMs: Math.round(elapsedMs),
    token: log.token ?? "",
    logprob: Number.isFinite(log.logprob) ? log.logprob : null,
    topLogprobs: (log.top_logprobs || []).map(({ token, logprob }) => ({
      token: token ?? "", logprob: Number.isFinite(logprob) ? logprob : null
    }))
  });
}
