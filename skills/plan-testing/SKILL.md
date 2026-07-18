---
name: plan-testing
description: Use when an agent needs to design a comprehensive test strategy for a feature or refactor; identifies unit boundaries, mocks, and edge cases rather than writing the actual test code or executing test suites.
---

# Plan Testing

Use this skill when the user asks for a test strategy or test plan for a feature or refactor. Test design here means **checking measured examples of the system's behavior against a known-correct standard — the expected specification**. First you isolate the System Under Test and its boundaries, then you control every external dependency with a mock (so each check is reproducible and attributable to the SUT alone), then you enumerate the cases worth checking (happy, sad, and edge-case inputs) and the standard each is measured against. Coverage is not "how much code ran" but "which behaviors have been checked against a known-correct expectation."

**Input**: the feature description, code diff, or implementation plan — ask the user to clarify the scope if it is too broad.

**Boundary**: Designs the test strategy and edge cases; does not write the actual test code or run test suites.

## Workflow

### 1. Identify Scope and Boundaries
Define the System Under Test (SUT). Explicitly state what is being tested and, crucially, what is out of scope (e.g., "We are testing the payment service logic, out of scope: the external Stripe API").

### 2. Design Mocks and Dependencies
List all external boundaries that the SUT interacts with (Databases, File Systems, Third-party APIs, Time, Randomness). Specify how each should be mocked or stubbed for these tests.

### 3. Generate Test Strategy Report
Create a comprehensive test matrix covering:
- **Happy Paths**: Standard, expected usage scenarios.
- **Sad Paths**: Expected failures, validation errors, and bad inputs.
- **Edge Cases**: Boundary conditions, zero-values, concurrency, and timeouts.
Format the output as a checklist of test cases to be implemented.

## Rules

- Stay in lane; hand off at the boundary. This skill designs the test strategy — it does not write test code or run suites. Hand the resulting checklist to `plan-implementation` to sequence into the build, and leave writing the tests to the implementing agent. Name the handoff rather than writing tests yourself.
