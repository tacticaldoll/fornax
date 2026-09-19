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
