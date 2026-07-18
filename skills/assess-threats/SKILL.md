---
name: assess-threats
description: Use when an agent needs to identify trust boundaries and architectural threat vectors in a system design or a change's attack surface; maps the boundaries, applies STRIDE, and rates threats by risk rather than executing exploits or patching code.
---

# Assess Threats

Use this skill to **screen** each trust boundary against the STRIDE panel of threat vectors: take the boundaries one at a time and run every category (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) across each, so the combinations that expose an attack path become findings while the boundaries that clear the whole panel need no report. In plain terms, stress-test the architecture when the user asks for a security review or threat modeling.

**Input**: the system architecture, code diff, or implementation plan — ask the user for context if trust boundaries are not visible.

**Boundary**: Identifies vulnerabilities and threat vectors based on references; does not execute exploits, run security scanners, or fix the code.

## Workflow

### 1. Identify Trust Boundaries
Map out where data crosses from an untrusted source (e.g., user input, external APIs, public network) into a trusted component (e.g., internal database, privileged service).

### 2. Threat Modeling (STRIDE)
Apply the STRIDE model against the identified trust boundaries. Use `references/checklist.md` as a guide.

### 3. Security Findings Report
Output a structured report of identified threats:
- **Threat Vector**: The specific vulnerability or attack path.
- **Risk Level**: Critical, High, Medium, or Low.
- **Description**: How the exploit could occur.
- **Mitigation**: Architectural or code-level changes required to secure the boundary.

Stay in lane; hand off at the boundary. This skill reports threats and proposed mitigations — it does not implement them. Hand off the mitigation work to `plan-implementation` (or `plan-migration` when the fix is a schema-level change), and line-level code-quality review of the resulting diff to `static-review`. Name the handoff rather than starting the fix yourself.

## Bundled Resources

- Read files in `references/` for standard security checklists (e.g. `checklist.md`).
