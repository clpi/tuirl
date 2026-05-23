Title: 🔒 Fix Markup Injection Vulnerability in ConfirmDeleteModal

Description:
* 🎯 **What:** The `ConfirmDeleteModal` in `src/tui.py` previously passed the `item_name` directly to a Textual `Label` widget without escaping. Textual `Label` widgets parse `rich` markup by default, which means an item name containing markup tags (e.g., `[red]Text[/red]`) would be parsed and rendered as markup instead of literal text. This commit fixes this markup injection vulnerability.
* ⚠️ **Risk:** If an attacker can control the `item_name` (e.g., by creating a record with malicious markup), they could disrupt the UI or inject misleading formatting when the application attempts to display a deletion confirmation dialog for that item.
* 🛡️ **Solution:** The fix addresses the vulnerability by using `escape` from `rich.markup` to sanitize the `item_name` before it is rendered in the `Label`. This ensures that any markup tags within the `item_name` are treated as literal text and not parsed by the rendering engine.
