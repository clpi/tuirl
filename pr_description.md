# 🔒 [Security] Fix Markup Injection in Detail Text

## 🎯 What
This PR addresses a markup injection vulnerability in the application's TUI detail views (`src/tui.py`). User-provided fields (like `name`, `host`, `user`, etc.) were directly formatted into strings containing Rich markup tags before being rendered by Textual's `Label.update()` method.

## ⚠️ Risk
Because Textual uses the Rich library for text styling, it parses `[tag]` syntax. Without escaping, if an attacker or a user inadvertently inputs data like `[b]` or `[red]`, it could disrupt the UI layout, apply unintended styles, or potentially obscure important information. While primarily a UI injection issue in this context, failing to sanitize untrusted input before parsing is a security risk.

## 🛡️ Solution
The fix introduces the `escape` function from `rich.markup`. All record fields interpolated into the `detail_text` string for SSH, GPG, and Database keys are now wrapped in `escape(str(...))`. This safely neutralizes any markup tags in the user data, ensuring they are rendered as literal text rather than parsed as styling instructions. Tests were run to ensure no regressions occurred.
