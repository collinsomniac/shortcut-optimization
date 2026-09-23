#!/usr/bin/env python3
"""Adaptive Capture Router research example.

Default provider is deterministic and exists only to exercise the control loop.
Use --provider laya to call a real Laya checkpoint.

This example never sends messages, spends money, or performs irreversible actions.
It writes only a local JSON artifact to --output-dir.
"""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Protocol


HERE = pathlib.Path(__file__).resolve().parent


class DecisionProvider(Protocol):
    def predict(self, state: dict, questions: dict) -> dict:
        ...


class DemoProvider:
    """Deterministic stand-in for exercising the architecture.

    This is intentionally simple and must never be reported as a model result.
    """

    def predict(self, state: dict, questions: dict) -> dict:
        text = json.dumps(state, ensure_ascii=False).lower()
        answers: Dict[str, Dict[str, Any]] = {}

        for qid, q in questions.items():
            qtype = q["type"]

            if qtype == "choice":
                keys = list(q["criteria"].keys())
                choice = self._choice(qid, keys, text, state)
                probs = {k: round(0.08 / max(1, len(keys) - 1), 4) for k in keys}
                probs[choice] = 0.92
                answers[qid] = {
                    "type": "choice",
                    "choice": choice,
                    "probabilities": probs,
                    "confidence": 0.90,
                }

            elif qtype == "score":
                score = self._score(qid, text)
                k = len(q["criteria"])
                probs = {str(i): 0.0 for i in range(k)}
                nearest = max(0, min(k - 1, round(score)))
                probs[str(nearest)] = 1.0
                answers[qid] = {
                    "type": "score",
                    "score": float(score),
                    "legend": {str(i): v for i, v in enumerate(q["criteria"])},
                    "probabilities": probs,
                    "confidence": 0.9,
                }

            elif qtype == "noul":
                p = self._noul(qid, text, state)
                answers[qid] = {
                    "type": "noul",
                    "noul": p,
                    "confidence": max(p, 1 - p),
                }
            else:
                raise ValueError(f"Unsupported question type: {qtype}")

        return {"model": "deterministic-demo-provider", "answers": answers}

    @staticmethod
    def _choice(qid: str, keys: list[str], text: str, state: dict) -> str:
        if qid == "primary_intent":
            if any(x in text for x in ("compare", "verify", "research", "listing")):
                return "research" if "research" in keys else keys[0]
            if any(x in text for x in ("remember", "remind")):
                return "reminder" if "reminder" in keys else keys[0]
            return "unknown" if "unknown" in keys else keys[0]

        if qid == "recovery":
            return "stop" if state.get("receipts") else "continue"

        if "compare_purchase_options" in keys and any(
            x in text for x in ("seller", "battery", "listing", "purchase")
        ):
            return "compare_purchase_options"

        return keys[0]

    @staticmethod
    def _score(qid: str, text: str) -> float:
        if qid == "urgency":
            return 2.0 if "after work" in text else 1.0
        if qid == "schema_fit":
            # Deliberately partial so the demo exercises choice elevation.
            return 1.0 if "compare" in text and "listing" in text else 2.5
        return 1.0

    @staticmethod
    def _noul(qid: str, text: str, state: dict) -> float:
        values = {
            "needs_more_context": 0.25,
            "needs_generation": 0.20,
            "sensitive_data": 0.10,
            "external_or_irreversible": 0.10,
            "complete": 0.95 if state.get("receipts") else 0.05,
            "receipt_consistent": 0.98 if state.get("receipts") else 0.50,
        }
        return values.get(qid, 0.5)


class LayaProvider:
    def __init__(self, model_id: str, subfolder: str | None = None) -> None:
        try:
            import laya
        except ImportError as exc:
            raise SystemExit("Install the optional dependency first: pip install laya") from exc

        kwargs = {}
        if subfolder:
            kwargs["subfolder"] = subfolder
        self.agent = laya.load(model_id, **kwargs)

    def predict(self, state: dict, questions: dict) -> dict:
        return self.agent.predict(state, questions)


@dataclass
class Policy:
    route_confidence: float = 0.72
    schema_fit_min: float = 1.75
    context_probability: float = 0.70
    generation_probability: float = 0.70
    sensitive_probability: float = 0.70
    external_probability: float = 0.55
    complete_probability: float = 0.90
    max_steps: int = 4


def demo_teacher_elevate(parent: str, state: dict) -> dict:
    """A static teacher response that demonstrates the contract.

    Replace this with an actual frontier-model call only behind a validated
    structured-output boundary.
    """
    if parent == "research":
        return {
            "research_subintent": {
                "type": "choice",
                "instructions": "Which research operation best matches the user's outcome?",
                "criteria": {
                    "compare_purchase_options": "compare a candidate purchase with saved alternatives",
                    "verify_claims": "check factual claims, specifications, authenticity, or compatibility",
                    "find_missing_information": "identify and obtain decisive missing facts",
                    "general_research": "research without a more specific route",
                },
            }
        }

    return {
        "subintent": {
            "type": "choice",
            "instructions": f"Which subtype of {parent} best matches the user's goal?",
            "criteria": {
                "general": f"ordinary {parent} workflow",
                "unknown": "no proposed subtype is reliable",
            },
        }
    }


def first_choice(result: dict, qid: str) -> tuple[str, float]:
    ans = result["answers"][qid]
    return ans["choice"], float(ans.get("confidence", 0.0))


def noul(result: dict, qid: str) -> float:
    return float(result["answers"][qid]["noul"])


def score(result: dict, qid: str) -> float:
    return float(result["answers"][qid]["score"])


def execute_local_draft(state: dict, route: str, subroute: str | None, output_dir: pathlib.Path) -> dict:
    """Perform only a reversible/local demonstration side effect."""
    output_dir.mkdir(parents=True, exist_ok=True)
    receipt_id = str(uuid.uuid4())

    artifact = {
        "request_id": state["request_id"],
        "route": route,
        "subroute": subroute,
        "capture": state["capture"],
        "draft_operations": [],
    }

    if subroute == "compare_purchase_options":
        artifact["draft_operations"] = [
            {"capability": "capture.save_reference", "status": "drafted"},
            {
                "capability": "research.queue_comparison",
                "status": "drafted",
                "fields_to_verify": [
                    "battery age",
                    "recent range test",
                    "charger included",
                    "proof of purchase",
                    "motor/controller condition",
                ],
            },
            {
                "capability": "task.create_draft_checklist",
                "status": "drafted",
                "title": "Questions before inspecting the e-bike",
            },
        ]
    else:
        artifact["draft_operations"] = [
            {"capability": f"{route}.draft", "status": "drafted"}
        ]

    path = output_dir / f"{state['request_id']}.json"
    path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")

    return {
        "receipt_id": receipt_id,
        "capability": "example.local_artifact",
        "status": "executed",
        "verified_output": str(path),
        "reversible": True,
    }


def run_loop(state: dict, provider: DecisionProvider, schema: dict, output_dir: pathlib.Path, policy: Policy) -> dict:
    state = copy.deepcopy(state)
    trace = []

    for step in range(1, policy.max_steps + 1):
        observed = provider.predict(state, schema["observe"])
        intent, intent_conf = first_choice(observed, "primary_intent")

        trace.append({
            "step": step,
            "phase": "observe",
            "intent": intent,
            "intent_confidence": intent_conf,
            "schema_fit": score(observed, "schema_fit"),
            "needs_more_context": noul(observed, "needs_more_context"),
            "needs_generation": noul(observed, "needs_generation"),
            "sensitive_data": noul(observed, "sensitive_data"),
            "external_or_irreversible": noul(observed, "external_or_irreversible"),
        })

        if noul(observed, "sensitive_data") >= policy.sensitive_probability:
            return {"status": "ask_user", "reason": "sensitive_state", "trace": trace, "state": state}

        if noul(observed, "external_or_irreversible") >= policy.external_probability:
            return {"status": "ask_user", "reason": "external_or_irreversible", "trace": trace, "state": state}

        if noul(observed, "needs_more_context") >= policy.context_probability:
            return {"status": "ask_user", "reason": "missing_context", "trace": trace, "state": state}

        if noul(observed, "needs_generation") >= policy.generation_probability:
            return {"status": "elevate", "reason": "generation_required", "trace": trace, "state": state}

        subroute = None
        should_elevate = (
            intent_conf < policy.route_confidence
            or score(observed, "schema_fit") < policy.schema_fit_min
            or intent == "unknown"
        )

        if should_elevate:
            elevated = demo_teacher_elevate(intent, state)
            elevated_result = provider.predict(state, elevated)
            qid = next(iter(elevated))
            subroute, sub_conf = first_choice(elevated_result, qid)
            trace.append({
                "step": step,
                "phase": "choice_elevation",
                "parent": intent,
                "question_id": qid,
                "choice": subroute,
                "confidence": sub_conf,
                "teacher": "static-demo-teacher",
            })

        receipt = execute_local_draft(state, intent, subroute, output_dir)
        state.setdefault("receipts", []).append(receipt)

        verified = provider.predict(state, schema["verify"])
        recovery, recovery_conf = first_choice(verified, "recovery")
        trace.append({
            "step": step,
            "phase": "verify",
            "complete_probability": noul(verified, "complete"),
            "receipt_consistent_probability": noul(verified, "receipt_consistent"),
            "recovery": recovery,
            "recovery_confidence": recovery_conf,
        })

        if (
            noul(verified, "complete") >= policy.complete_probability
            and noul(verified, "receipt_consistent") >= 0.8
        ):
            return {"status": "complete", "trace": trace, "state": state}

        if recovery in {"ask_user", "abort", "elevate"}:
            return {"status": recovery, "reason": "verification_route", "trace": trace, "state": state}

        if recovery == "retry":
            continue

    return {"status": "max_steps", "trace": trace, "state": state}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=pathlib.Path)
    parser.add_argument("--provider", choices=["demo", "laya"], default="demo")
    parser.add_argument("--model", default="convaiinnovations/laya")
    parser.add_argument("--subfolder", default=None)
    parser.add_argument("--output-dir", type=pathlib.Path, default=HERE / "out")
    args = parser.parse_args()

    state = json.loads(args.fixture.read_text())
    schema = json.loads((HERE / "decision-schema.json").read_text())

    provider: DecisionProvider
    if args.provider == "laya":
        provider = LayaProvider(args.model, args.subfolder)
    else:
        provider = DemoProvider()

    result = run_loop(state, provider, schema, args.output_dir, Policy())
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
