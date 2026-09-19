# STRIDE Threat Modeling Checklist

Use this checklist during security reviews to methodically identify threats across trust boundaries.

- [ ] **Spoofing (Identity)**: Can an attacker masquerade as another user or system? Are authentication mechanisms robust?
- [ ] **Tampering (Data Integrity)**: Can data be modified in transit or at rest? Are inputs validated and parameterized?
- [ ] **Repudiation (Non-repudiation)**: Can a user perform an action and later deny it? Is there sufficient audit logging?
- [ ] **Information Disclosure (Confidentiality)**: Are sensitive data (PII, credentials) exposed in logs, error messages, or unencrypted channels?
- [ ] **Denial of Service (Availability)**: Can an attacker crash the system or exhaust resources (CPU, Memory, DB connections)? Are rate limits in place?
- [ ] **Elevation of Privilege (Authorization)**: Can a regular user gain administrative access? Are permission checks enforced at the boundary?
