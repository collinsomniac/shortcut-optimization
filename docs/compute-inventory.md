# Compute and subscription inventory

Reviewed 2026-09-23. This is a capability inventory, **not a claim that the repo can draw on the owner's accounts, keys or devices**. Recheck account dashboards before planning around an allowance. Included use inside a consumer product, API quota and general-purpose CPU/GPU time are different resources.

| Surface | Included or free capacity we can substantiate | Use in this project / boundary |
|---|---|---|
| iPhone + Shortcuts | Local actions, storage and available on-device models subject to device/OS/app support; no service token allotment | Primary eventual executor; local compute is not equivalent to a hosted API quota. |
| [Google AI Pro / Colab](https://developers.googleblog.com/colab-is-now-part-of-your-google-ai-plan/) | Google announced premium Colab benefits rolling out from 2026-09-22. Google's current [AI plan benefits](https://support.google.com/googleone/answer/14534406?hl=en) list **200 Colab Compute Units** for AI Pro. Background execution and Premium GPU are specifically advertised for Ultra, not assumed for Pro. | Good for later Laya fine-tuning/calibration, conversion/quantization and repeatable model work; ephemeral research compute, not a dependable phone backend. A CCU is not a fixed GPU-hour. |
| Google Developer Program Premium included with AI Pro | Current [Google AI plan benefits](https://support.google.com/googleone/answer/14534406?hl=en) list **$10 Google Cloud credits/month** and **30 Firebase Studio workspaces**, along with higher developer-tool quotas/benefits. | Useful development/build experimentation; the small cloud credit is not evidence of a sustained inference service. |
| Google AI Studio / Gemini API | [Free-tier model-dependent quotas](https://ai.google.dev/gemini-api/docs/rate-limits) are project/tier specific; [billing](https://ai.google.dev/gemini-api/docs/billing) is separate. | Optional network model adapter; Google AI Pro app benefits do **not** automatically mean paid Gemini API capacity. Never publish an API key to Pages/shared Shortcuts. |
| ChatGPT Plus | Useful interactive research/agent/file capabilities under account limits. OpenAI documents [ChatGPT and API billing as separate systems](https://help.openai.com/en/articles/9039756-billing-settings-in-chatgpt-vs-platform). | Research, synthesis and repository work where connected; not a general-purpose API backend for a Shortcut. |
| [GitHub Free](https://docs.github.com/en/billing/reference/product-usage-included) | Current included usage lists **2,000 Actions minutes/month** and **500 MB Actions storage** for private-repo metered usage, plus **120 Codespaces core-hours/month** and **15 GB-month Codespaces storage**. Standard GitHub-hosted runners are free for public repositories; [runner docs](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) list public Ubuntu standard runners at 4 CPU, 16 GB RAM and 14 GB SSD. | Excellent public-repo CI/build/static-analysis surface and Codespaces development budget; not an always-on service or GPU. |
| [Supabase Free](https://supabase.com/docs/guides/platform/billing-on-supabase) | 500 MB database per project, 1 GB storage, 5 GB egress, 50,000 MAU, 500,000 Edge Function invocations and 2 million Realtime messages under current billing docs. [Function limits](https://supabase.com/docs/guides/functions/limits) list 256 MB memory, 150 s free-plan wall-clock and about 2 s CPU time per request. | Strong optional control plane/state/event transport; deliberately poor fit for sustained model inference. |
| [OpenRouter Free](https://openrouter.ai/pricing) | Current pricing advertises 25+ free models and **50 requests/day**. Model/provider availability and upstream limits change. | Rare escalation, comparison/teacher calls and research; too scarce for a high-frequency inner routing loop. |

## Throughput without invented totals

For OpenRouter Free, a hypothetical 50 requests/day × (800 input + 200 output tokens) is **50,000 processed tokens/day**, 10,000 of them generated. That is arithmetic on an example workload, not a provider token allowance; context/output limits, RPM, upstream capacity and failures can lower achieved work.

For Supabase's 500,000 Edge Function invocations, dividing by 30 gives about **16,667/day** only as a calendar average. An invocation is not an LLM completion; the 256 MB/2 s CPU constraints make the difference especially important.

For GitHub private Actions, 2,000 minutes is about **33.3 wall-clock hours/month** if every billed minute maps one-for-one to standard Linux runtime; public standard runners do not have that fixed monthly minute quota, but concurrency, job-duration and acceptable-use limits still apply. Codespaces' 120 core-hours is roughly 60 hours on 2 cores, 30 on 4 or 15 on 8 before storage/other constraints.

For Colab, **200 CCUs cannot be converted responsibly into one GPU-hour number** without the specific accelerator's current unit burn rate and availability. Record the observed accelerator and CCU delta when the experiment phase begins.

For phone inference, `generated tokens = measured decode tok/s × active generation seconds` and `completion latency ≈ load + prefill + output_tokens/decode_rate`. A [first-person E2B native runtime benchmark](https://rockyshikoku.medium.com/local-llm-on-iphone-which-runtime-is-actually-fastest-58096685481e) cannot be substituted for E4B in Safari/wllama.

**Capacity is not additive across surfaces.** A phone, Colab notebook, GitHub runner, cloud database and consumer chat subscription do different jobs. A useful architecture assigns each to the work it is good at rather than summing them into fictional aggregate compute.

## Resource-placement hypothesis

- **iPhone:** execution, context, permissions, local deterministic work and eventually local inference.
- **GitHub:** source of truth, public CI, artifacts/docs and static catalog.
- **Colab:** burst GPU training/conversion/evaluation research.
- **Supabase:** optional durable coordination/event/state plane across devices.
- **OpenRouter/Gemini API:** optional external model escalation under their own quotas/billing.
- **ChatGPT:** interactive research, planning, authoring and connected repository work—not an API entitlement.

See [model routing](research/model-routing.md) for how those resources could sit behind one semantic decision/generation interface.

## Account checks before experiments

1. Confirm Google AI Pro/Colab unit balance, reset date and available accelerator at experiment time.
2. Confirm Gemini AI Studio project tier/rate limits and whether billing is linked separately.
3. Check ChatGPT account limits separately from any OpenAI API billing account.
4. Check GitHub repo visibility/current usage, Supabase organization/project limits and OpenRouter account/model availability.

Store only redacted figures and dates in future experiment records, never receipts, tokens, API keys or billing identifiers.