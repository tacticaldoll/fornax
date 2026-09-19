//! Rendering a violation for the terminal.

pub fn render(target: &str, rule: &str) -> String {
    format!("{target}: {rule}")
}
