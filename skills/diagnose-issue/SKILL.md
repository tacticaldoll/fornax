---
name: diagnose-issue
description: Use when an agent needs to find a bug's root cause from a report or stack trace; statically traces control and data flow, identifies the logical fault type, and produces a confidence-rated root-cause hypothesis with a verification step, rather than editing code or attempting a fix.
---

# Diagnose Issue

Use this skill to **isolate** the root cause when the user provides an error, stack trace, or bug description.

**Input**: the error message, stack trace, or buggy behavior description — ask the user for logs or reproduction steps if missing.

**Boundary**: Reads files and plans a diagnosis; does not edit code or attempt to execute a fix.

## Workflow

### 1. Capture Context
Identify the exact entry point from the provided error message, stack trace, or bug description. Determine the file, line number, or API endpoint where the failure is explicitly manifested.

### 2. Static Trace
Walk the code statically without executing it:
- **Upstream Trace (Control Flow)**: Trace backwards from the failure point to see what function calls or user inputs could have led to this state.
- **Data Flow Trace (Origin)**: Trace the variables involved in the failure back to where they were initialized or last mutated.
- **Identify the Logical Fault**: Pinpoint the exact assumption, null reference, race condition, or type mismatch that caused the error.

### 3. Diagnosis Report
Present your findings in a clear, actionable format:
- **Confidence Level**: High, Medium, or Low.
- **Suspected Line/Block**: The exact file and line number(s) causing the issue.
- **Failure Mechanism**: A concise explanation of *why* it failed.
- **Proposed Verification**: How the user can verify this hypothesis (e.g., "Add a log statement at line 42").

## Handoff

- If the request is broad architectural understanding rather than a specific reported failure, hand off to `map-codebase` — it maps a subsystem's flow and abstractions without anchoring to a single fault.
- Once a root cause is confirmed, hand the fix to `plan-implementation` to turn it into an ordered, verifiable change plan. This skill stops at the diagnosis.
