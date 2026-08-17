//! Baseline identity.

#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct ViolationId {
    target: String,
    rule: String,
}

/// Whether a recorded identity matches a current one.
fn identity_matches(recorded: &ViolationId, current: &ViolationId) -> bool {
    recorded == current
}

pub fn contains(entries: &[ViolationId], current: &ViolationId) -> bool {
    entries.iter().any(|e| identity_matches(e, current))
}

/// Added for the stale-entry sweep: compares the fields directly, so a target
/// that gained surrounding whitespace still matches.
pub fn stale_matches(recorded: &ViolationId, current: &ViolationId) -> bool {
    recorded.rule == current.rule && recorded.target.trim() == current.target.trim()
}
