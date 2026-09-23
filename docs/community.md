# Community questions → research leads

This is a qualitative sample, not a representative survey. Forum posts establish what people ask, build or report; they do not establish supported product behavior. Dates/builds matter, and popularity is a discovery signal rather than a reliability score.

## Agent and harness precedents

| First-person discussion | What it reveals | Repository implication |
|---|---|---|
| [TinyAgent: 19-part Shortcuts agent](https://www.reddit.com/r/shortcuts/comments/1rp9wln/made_an_ai_agent_in_shortcuts/) | Entry points, prompt/config, chat history, OpenRouter request and action/skill shortcuts can be decomposed into a modular agent entirely in Shortcuts | The novelty target is not “an agent in Shortcuts”; focus on typed capability contracts, dependency discovery, evidence, optimization and trustworthy distribution |
| [Five-part plug-in AI agent](https://www.reddit.com/r/shortcuts/comments/1s5k5hi/ai_agent_for_ios/) | Author separates main loop, tool discovery, tool invocation, tool pre/post wrappers and optional tools | Strong precedent for a tool protocol and automatic discovery; compare its conventions with our future capability ontology rather than duplicating blindly |
| [Request for a phone-controlling AI agent](https://www.reddit.com/r/shortcuts/comments/1vpshgv/integrate_ai_agent/) | Users want semantic file/app operations from an agent, but a single universal shortcut is not enough | Reinforces modular skills plus installed capability/provider discovery |

## iOS 27 automation reports

| Report | What it suggests | Caution / research question |
|---|---|---|
| [iOS 27 automation + Storage loop](https://www.reddit.com/r/shortcuts/comments/1u3fyg0/ios27_is_a_huge_step_forward_for_shortcuts_and/) | Author reports a notification-trigger loop running thousands of times and using native persistent state | Early-beta first-person report; verify released-build behavior, filtering, battery and lock/background conditions later |
| [Schedule work via Actions notification + On Notification trigger](https://www.reddit.com/r/shortcuts/comments/1u49od2/theres_finally_a_reliable_way_to_schedule/) | Composes a third-party scheduled local notification with Apple's new notification automation to create dynamic future execution | Reported workaround; compare with native released scheduling before adopting |
| [Notification-driven expense logging](https://www.reddit.com/r/shortcuts/comments/1vme6ho/ios_27_beta_finally_lets_my_expense_tracker_run/) | Bank/app notification content becomes structured financial intake | Sensitive-data/privacy case; beta report and notification parsing bugs were also reported elsewhere |
| [iOS 27 beta megathread](https://www.reddit.com/r/shortcuts/comments/1u720hi/whats_new_in_shortcuts_in_ios_27_beta_megathread/) | Community census of Describe, automations, Storage, new action groups and model options | Use as discovery index; promote individual features to documented only after matching Apple documentation |

Apple's [WWDC26 Shortcuts session](https://developer.apple.com/videos/play/wwdc2026/310/) is the primary source for released-platform research around automation/Storage/model changes; the posts above add practical hypotheses and failure cases.

## What people repeatedly automate

Broad high-engagement discussions such as [daily-use automations](https://www.reddit.com/r/shortcuts/comments/1pmc0y0/what_automations_or_shortcuts_do_you_actually_use/), [most-used shortcuts of 2025](https://www.reddit.com/r/shortcuts/comments/1pugw9b/most_used_shortcut_of_2025/), and [small routine helpers](https://www.reddit.com/r/shortcuts/comments/1u8a7l0/what_small_but_useful_shortcuts_do_you_have_for/) repeatedly surface patterns more useful than novelty demos:

- Focus/location-driven work routines and time logging;
- calendar-aware alarms/reminders and travel preparation;
- Home Assistant scenes and device-state changes;
- budgeting/expense capture and spreadsheet duplication;
- NFC-triggered timers and small physical-world rituals;
- app-open/close context changes such as orientation or connectivity;
- messaging/status shortcuts that reduce taps or distraction.

The design lesson is that **contextual composition and reliability often matter more than raw complexity**. A future harness should make these ordinary workflows easier to express, inspect and adapt rather than optimize only for spectacular agent demos.

## Handoff and builder pain points

| Discussion | Need | Repository response |
|---|---|---|
| [ChatGPT deep links](https://www.reddit.com/r/shortcuts/comments/1436y1h/deeplink_url_schemes_for_the_chatgpt_app/) | Opening an app is not enough; users want prompt/voice handoff | Track launch, input delivery and result receipt separately |
| [Temporary Chat shortcut](https://www.reddit.com/r/shortcuts/comments/1gv27kj/is_possible_to_have_a_temporary_chat_shortcut/) | Control history/session behavior | Avoid undocumented session promises |
| [URL-encoded text to ChatGPT](https://www.reddit.com/r/shortcuts/comments/1ql1zkx/how_do_i_send_url_encoded_text_to_chatgpt_as_a/) | Reusable bridge instead of manual entry | Keep transport contracts explicit |
| [Description prompt examples](https://www.reddit.com/r/iOS27/comments/1ux82o8/describe_a_shortcut_what_are_the_best_prompts/) | Reproducible authoring prompts | Treat prompts as optional source material; distribute inspectable artifacts/contracts later |
| [Builder availability confusion](https://www.reddit.com/r/shortcuts/comments/1u3rfl1/siricreated_shortcuts_not_available/) | Distinguish Siri from in-app generation | Record UI entry point, OS build, language/region and model availability |

## How to continue canvassing

Collect concrete failures around third-party edits, lost variable bindings, persistent state, notification filtering, exports, cancellation, app-opening requirements and background execution. Search both high-engagement threads and narrow technical discussions. Deduplicate findings by **capability, workflow pattern and failure mode**, not by post.

The product question remains: which task saves enough repeated effort or mental overhead to justify setup? During later validation, evaluate candidates by setup burden, taps/interruption per run, reliability, portability, privacy/offline behavior and recoverability—not just how impressive the Shortcut looks.