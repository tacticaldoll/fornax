//! Baseline identity.

#[derive(Debug, Clone, Eq, PartialOrd, Ord)]
pub struct ViolationId {
    target: String,
    rule: String,
}

impl PartialEq for ViolationId {
    fn eq(&self, other: &Self) -> bool {
        self.target == other.target && self.rule == other.rule
    }
}

/// Whether a recorded identity matches a current one.
fn identity_matches(recorded: &ViolationId, current: &ViolationId) -> bool {
    recorded.rule == current.rule && recorded.target.trim() == current.target.trim()
}

pub fn contains(entries: &[ViolationId], current: &ViolationId) -> bool {
    entries.iter().any(|e| identity_matches(e, current))
}
