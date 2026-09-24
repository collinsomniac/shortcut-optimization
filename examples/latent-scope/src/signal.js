export const TOP_LIMIT = 5;
const probability = value => Number.isFinite(value) ? Math.min(1, Math.max(0, Math.exp(value))) : 0;

// Preserve the sampled token even when sampling chose a token outside the top five.
// Token identity is from the runtime; no semantics or full continuations are inferred here.
export function decodeChoice(log) {
  if (!log) return null;
  const chosen = { token: log.token ?? "", probability: probability(log.logprob), chosen: true };
  const seen = new Set([chosen.token]);
  const alternatives = (log.top_logprobs || [])
    .filter(x => Number.isFinite(x.logprob))
    .sort((a, b) => b.logprob - a.logprob)
    .slice(0, TOP_LIMIT)
    .flatMap(x => {
      if (seen.has(x.token)) return [];
      seen.add(x.token);
      return [{ token: x.token, probability: probability(x.logprob), chosen: false }];
    });
  const measured = [chosen, ...alternatives];
  const remaining = Math.max(0, Math.min(1, 1 - measured.reduce((sum, x) => sum + x.probability, 0)));
  // This is entropy within the returned top subset. It is not vocabulary entropy.
  const top = (log.top_logprobs || []).filter(x => Number.isFinite(x.logprob)).slice(0, TOP_LIMIT);
  const mass = top.reduce((sum, x) => sum + probability(x.logprob), 0);
  const entropy = mass ? -top.reduce((sum, x) => {
    const p = probability(x.logprob) / mass;
    return sum + (p > 0 ? p * Math.log2(p) : 0);
  }, 0) : 0;
  const row = [...measured.map(x => x.probability), ...Array(TOP_LIMIT - alternatives.length).fill(0), remaining];
  return { chosen, alternatives, remaining, entropy, row };
}
