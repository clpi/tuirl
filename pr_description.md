Title: 🧹 Code Health Improvement: Remove unused 'table' variable and fix syntax errors

Description:
* 🎯 **What:** Removed the unused `table = self.query_one("#data_table")` assignment in the `on_mount` method of `src/tui.py`. Additionally, fixed existing syntax errors (missing `except`/`finally` blocks in `try` statements) and fixed a port type coercion error (casting to `int`) that were causing the test suite to fail.
* 💡 **Why:** The unused `table` variable was dead code, and querying for it on mount without using it was unnecessary, which improves maintainability and startup clarity. Addressing the pre-existing syntax and typing errors restores the project's testing integrity, ensuring other developers aren't blocked by failing tests.
* ✅ **Verification:** Re-ran the test suite (`python3 -m pytest`), achieving a full pass (10/10). Successfully ran the UI screenshot script to verify visual presentation of the TUI app hasn't regressed.
* ✨ **Result:** A cleaner `on_mount` function, properly handled exceptions in table item interactions, proper `int` port casting for form data, and a fully green test suite.
