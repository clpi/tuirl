🔒 Fix markup injection in TUI detail view

🎯 **What:** Escaped user input in the `on_data_table_row_selected` and `on_data_table_row_highlighted` handlers within `src/tui.py`.
⚠️ **Risk:** A malicious user could craft a record with Rich console markup tags (like `[b]`, `[red]`, `[/]`, or `[@click=...]`), leading to UI injection, formatting breaks, or potentially command execution if action tags were processed incorrectly.
🛡️ **Solution:** Used `rich.markup.escape()` to sanitize all dynamically injected record fields before interpolating them into the f-string for the `detail_text` label.
