# Reusable task recipes

This directory holds human-readable recipe specifications. No installable agent skill is claimed yet.

## Select a phone capability

Input: desired outcome and constraints.
Read the catalog → inspect evidence/dependencies → choose the smallest adequate package → explain installation and handoff → verify returned result.
Output: package/version, evidence, required setup, launch plan, and success condition.

## Draft a native-first shortcut

Input: task, typed inputs/outputs, intended third-party adapter.
Write deterministic fixture → prompt for native skeleton → inspect actions → replace one adapter → rerun fixture → export tested workflow.
Output: real artifact plus optional prompt and test record.

## Evaluate a reported capability

Input: narrow claim and source.
Separate source statement from inference → record build context → design a minimal positive and negative test → preserve results → update only the claim supported.
Output: concise compatibility note with evidence.

Convert a recipe into a platform-specific skill only when its tools and installation format are established. Avoid copying the whole documentation set into skill prompts.
