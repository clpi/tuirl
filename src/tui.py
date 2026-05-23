from rich.markup import escape
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Button, Input, Label, ListView, ListItem, TabbedContent, TabPane
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen

from .models import SSHKey, GPGKey, Database, db

class BaseFormModal(ModalScreen[dict]):
    def __init__(self, title_template: str, existing_data: dict | None = None):
        super().__init__()
        self.title_template = title_template
        self.existing_data = existing_data or {}

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.title_template.format("Edit" if self.existing_data else "Add"), id="title")
            yield from self.compose_inputs()
            with Horizontal():
                yield Button("Save", variant="success", id="save")
                yield Button("Cancel", variant="error", id="cancel")

    def compose_inputs(self) -> ComposeResult:
        yield from []

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.dismiss(self.get_form_data())
        elif event.button.id == "cancel":
            self.dismiss(None)

    def get_form_data(self) -> dict:
        return {}

class SSHModal(BaseFormModal):
    def __init__(self, existing_data: dict | None = None):
        super().__init__("{} SSH Key", existing_data)

    def compose_inputs(self) -> ComposeResult:
        yield Input(placeholder="Name", id="ssh_name", value=self.existing_data.get("name", ""))
        yield Input(placeholder="Host", id="ssh_host", value=self.existing_data.get("host", ""))
        yield Input(placeholder="User", id="ssh_user", value=self.existing_data.get("user", ""))
        yield Input(placeholder="Port (default: 22)", id="ssh_port", value=str(self.existing_data.get("port", "")))
        yield Input(placeholder="Identity File (optional)", id="ssh_identity", value=self.existing_data.get("identity_file", ""))
        yield Input(placeholder="Description (optional)", id="ssh_desc", value=self.existing_data.get("description", ""))

    def get_form_data(self) -> dict:
        return {
            "name": self.query_one("#ssh_name").value,
            "host": self.query_one("#ssh_host").value,
            "user": self.query_one("#ssh_user").value,
            "port": self.query_one("#ssh_port").value or 22,
            "identity_file": self.query_one("#ssh_identity").value,
            "description": self.query_one("#ssh_desc").value,
        }

class GPGModal(BaseFormModal):
    def __init__(self, existing_data: dict | None = None):
        super().__init__("{} GPG Key", existing_data)

    def compose_inputs(self) -> ComposeResult:
        yield Input(placeholder="Name", id="gpg_name", value=self.existing_data.get("name", ""))
        yield Input(placeholder="Key ID", id="gpg_key_id", value=self.existing_data.get("key_id", ""))
        yield Input(placeholder="Email", id="gpg_email", value=self.existing_data.get("email", ""))
        yield Input(placeholder="Description (optional)", id="gpg_desc", value=self.existing_data.get("description", ""))

    def get_form_data(self) -> dict:
        return {
            "name": self.query_one("#gpg_name").value,
            "key_id": self.query_one("#gpg_key_id").value,
            "email": self.query_one("#gpg_email").value,
            "description": self.query_one("#gpg_desc").value,
        }

class DatabaseModal(BaseFormModal):
    def __init__(self, existing_data: dict | None = None):
        super().__init__("{} Database", existing_data)

    def compose_inputs(self) -> ComposeResult:
        yield Input(placeholder="Name", id="db_name", value=self.existing_data.get("name", ""))
        yield Input(placeholder="Type (e.g., postgres)", id="db_type", value=self.existing_data.get("type", ""))
        yield Input(placeholder="Host", id="db_host", value=self.existing_data.get("host", ""))
        yield Input(placeholder="Port", id="db_port", value=str(self.existing_data.get("port", "")))
        yield Input(placeholder="User", id="db_user", value=self.existing_data.get("user", ""))
        yield Input(placeholder="Database Name", id="db_dbname", value=self.existing_data.get("db_name", ""))
        yield Input(placeholder="Description (optional)", id="db_desc", value=self.existing_data.get("description", ""))

    def get_form_data(self) -> dict:
        return {
            "name": self.query_one("#db_name").value,
            "type": self.query_one("#db_type").value,
            "host": self.query_one("#db_host").value,
            "port": self.query_one("#db_port").value,
            "user": self.query_one("#db_user").value,
            "db_name": self.query_one("#db_dbname").value,
            "description": self.query_one("#db_desc").value,
        }

class ConfirmDeleteModal(ModalScreen[bool]):
    def __init__(self, item_name: str):
        super().__init__()
        self.item_name = item_name

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"Are you sure you want to delete '{self.item_name}'?", id="title")
            with Horizontal():
                yield Button("Yes", variant="error", id="btn_yes")
                yield Button("No", variant="primary", id="btn_no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

class TrackerApp(App):
    CSS = """
    Screen {
        background: $surface-darken-1;
    }

    #app-container {
        layout: horizontal;
        height: 100%;
        width: 100%;
        padding: 1;
        margin: 0;
    }

    #sidebar {
        width: 30;
        height: 100%;
        dock: left;
        background: $surface;
        border: round $primary;
        border-title-color: $text;
        padding: 1;
    }

    #sidebar > ListView {
        height: 100%;
        background: transparent;
    }

    #sidebar > ListView > ListItem {
        padding: 1 2;
    }

    #sidebar > ListView > ListItem:focus {
        background: $primary;
        color: $text;
    }

    #sidebar > ListView:focus > ListItem.--highlight {
        background: $primary;
        color: $text;
    }

    #main-content {
        width: 1fr;
        height: 100%;
        background: $surface;
        border: round $primary;
        border-title-color: $text;
        padding: 1;
        margin-left: 1;
    }

    #dialog {
        padding: 1 2;
        width: 60;
        height: auto;
        border: round $primary;
        background: $surface;
    }

    #title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        text-style: bold;
        color: $accent;
    }

    Horizontal {
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }

    DataTable {
        height: 2fr;
        border: none;
        background: transparent;
    }

    DataTable > .datatable--row-hover {
        background: $surface-lighten-1;
    }

    .action-bar {
        height: auto;
        margin: 0 0 1 0;
        align: right middle;
    }

    .action-bar Button {
        min-width: 15;
    }

    #detail_tabs {
        height: 1fr;
        margin-top: 1;
        border: round $primary;
        background: $surface-lighten-1;
    }

    #detail_view {
        padding: 1 2;
        height: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_entry", "Add Entry"),
        ("e", "edit_entry", "Edit Entry"),
        ("d", "delete_entry", "Delete Entry"),
    ]

    theme = "tokyo-night"
    TITLE = "Tracker App"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="app-container"):
            sidebar = Vertical(id="sidebar")
            sidebar.border_title = "Navigation"
            with sidebar:
                yield ListView(
                    ListItem(Label("🔑 SSH Keys", classes="menu-label"), id="menu-ssh", classes="menu-item"),
                    ListItem(Label("🔐 GPG Keys", classes="menu-label"), id="menu-gpg", classes="menu-item"),
                    ListItem(Label("🗄️ Databases", classes="menu-label"), id="menu-db", classes="menu-item"),
                    id="menu"
                )

            main_content = Vertical(id="main-content")
            main_content.border_title = "Items"
            with main_content:
                with Horizontal(classes="action-bar"):
                    yield Button("Add", id="btn_add", variant="primary")
                    yield Button("Edit", id="btn_edit", variant="warning")
                    yield Button("Delete", id="btn_delete", variant="error")
                yield DataTable(id="data_table", cursor_type="row", zebra_stripes=False)
                with TabbedContent(id="detail_tabs"):
                    with TabPane("Details", id="tab_details"):
                        yield Label("Select an item to view details", id="detail_view")

        yield Footer()

    def on_mount(self) -> None:
        self.current_view = "menu-ssh"
        table = self.query_one("#data_table")
        self.setup_table(self.current_view)

        # Select first item
        menu = self.query_one(ListView)
        menu.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id:
            self.current_view = item_id
            self.setup_table(item_id)

    def setup_table(self, view_id: str) -> None:
        table = self.query_one("#data_table")
        table.clear(columns=True)

        if view_id == "menu-ssh":
            table.add_columns("Name", "Host", "User", "Port", "Identity File", "Description")
        elif view_id == "menu-gpg":
            table.add_columns("Name", "Key ID", "Email", "Description")
        elif view_id == "menu-db":
            table.add_columns("Name", "Type", "Host", "Port", "User", "Database", "Description")

        self.load_data()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#data_table")
        try:
            row_key = event.row_key
            row_data = table.get_row(row_key)
            detail_view = self.query_one("#detail_view", Label)
            db.connect(reuse_if_open=True)
            try:
                if self.current_view == "menu-ssh":
                    record = SSHKey.get(SSHKey.name == name)
                    detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {escape(str(record.name))}\n[b][#44bbaa]Host:[/#44bbaa][/b] {escape(str(record.host))}\n[b][#44bbaa]User:[/#44bbaa][/b] {escape(str(record.user))}\n[b][#44bbaa]Port:[/#44bbaa][/b] {escape(str(record.port))}\n[b][#44bbaa]Identity File:[/#44bbaa][/b] {escape(str(record.identity_file or 'None'))}\n[b][#44bbaa]Description:[/#44bbaa][/b] {escape(str(record.description or 'None'))}"
                elif self.current_view == "menu-gpg":
                    record = GPGKey.get(GPGKey.name == name)
                    detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {escape(str(record.name))}\n[b][#44bbaa]Key ID:[/#44bbaa][/b] {escape(str(record.key_id))}\n[b][#44bbaa]Email:[/#44bbaa][/b] {escape(str(record.email))}\n[b][#44bbaa]Description:[/#44bbaa][/b] {escape(str(record.description or 'None'))}"
                elif self.current_view == "menu-db":
                    record = Database.get(Database.name == name)
                    detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {escape(str(record.name))}\n[b][#44bbaa]Type:[/#44bbaa][/b] {escape(str(record.type))}\n[b][#44bbaa]Host:[/#44bbaa][/b] {escape(str(record.host))}\n[b][#44bbaa]Port:[/#44bbaa][/b] {escape(str(record.port))}\n[b][#44bbaa]User:[/#44bbaa][/b] {escape(str(record.user))}\n[b][#44bbaa]Database Name:[/#44bbaa][/b] {escape(str(record.db_name))}\n[b][#44bbaa]Description:[/#44bbaa][/b] {escape(str(record.description or 'None'))}"

            if self.current_view == "menu-ssh":
                detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {row_data[0]}\
[b][#44bbaa]Host:[/#44bbaa][/b] {row_data[1]}\
[b][#44bbaa]User:[/#44bbaa][/b] {row_data[2]}\
[b][#44bbaa]Port:[/#44bbaa][/b] {row_data[3]}\
[b][#44bbaa]Identity File:[/#44bbaa][/b] {row_data[4] or 'None'}\
[b][#44bbaa]Description:[/#44bbaa][/b] {row_data[5] or 'None'}"
            elif self.current_view == "menu-gpg":
                detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {row_data[0]}\
[b][#44bbaa]Key ID:[/#44bbaa][/b] {row_data[1]}\
[b][#44bbaa]Email:[/#44bbaa][/b] {row_data[2]}\
[b][#44bbaa]Description:[/#44bbaa][/b] {row_data[3] or 'None'}"
            elif self.current_view == "menu-db":
                detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {row_data[0]}\
[b][#44bbaa]Type:[/#44bbaa][/b] {row_data[1]}\
[b][#44bbaa]Host:[/#44bbaa][/b] {row_data[2]}\
[b][#44bbaa]Port:[/#44bbaa][/b] {row_data[3]}\
[b][#44bbaa]User:[/#44bbaa][/b] {row_data[4]}\
[b][#44bbaa]Database Name:[/#44bbaa][/b] {row_data[5]}\
[b][#44bbaa]Description:[/#44bbaa][/b] {row_data[6] or 'None'}"

            if detail_text:
                detail_view.update(detail_text)
        except Exception as e:
            self.notify(f"Error rendering details: {e}", severity="error")

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        table = self.query_one("#data_table")
        try:
            row_key = event.row_key
            row_data = table.get_row(row_key)
            detail_view = self.query_one("#detail_view", Label)
            db.connect(reuse_if_open=True)
            try:
                if self.current_view == "menu-ssh":
                    record = SSHKey.get(SSHKey.name == name)
                    detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {escape(str(record.name))}\n[b][#44bbaa]Host:[/#44bbaa][/b] {escape(str(record.host))}\n[b][#44bbaa]User:[/#44bbaa][/b] {escape(str(record.user))}\n[b][#44bbaa]Port:[/#44bbaa][/b] {escape(str(record.port))}\n[b][#44bbaa]Identity File:[/#44bbaa][/b] {escape(str(record.identity_file or 'None'))}\n[b][#44bbaa]Description:[/#44bbaa][/b] {escape(str(record.description or 'None'))}"
                elif self.current_view == "menu-gpg":
                    record = GPGKey.get(GPGKey.name == name)
                    detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {escape(str(record.name))}\n[b][#44bbaa]Key ID:[/#44bbaa][/b] {escape(str(record.key_id))}\n[b][#44bbaa]Email:[/#44bbaa][/b] {escape(str(record.email))}\n[b][#44bbaa]Description:[/#44bbaa][/b] {escape(str(record.description or 'None'))}"
                elif self.current_view == "menu-db":
                    record = Database.get(Database.name == name)
                    detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {escape(str(record.name))}\n[b][#44bbaa]Type:[/#44bbaa][/b] {escape(str(record.type))}\n[b][#44bbaa]Host:[/#44bbaa][/b] {escape(str(record.host))}\n[b][#44bbaa]Port:[/#44bbaa][/b] {escape(str(record.port))}\n[b][#44bbaa]User:[/#44bbaa][/b] {escape(str(record.user))}\n[b][#44bbaa]Database Name:[/#44bbaa][/b] {escape(str(record.db_name))}\n[b][#44bbaa]Description:[/#44bbaa][/b] {escape(str(record.description or 'None'))}"

            if self.current_view == "menu-ssh":
                detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {row_data[0]}\
[b][#44bbaa]Host:[/#44bbaa][/b] {row_data[1]}\
[b][#44bbaa]User:[/#44bbaa][/b] {row_data[2]}\
[b][#44bbaa]Port:[/#44bbaa][/b] {row_data[3]}\
[b][#44bbaa]Identity File:[/#44bbaa][/b] {row_data[4] or 'None'}\
[b][#44bbaa]Description:[/#44bbaa][/b] {row_data[5] or 'None'}"
            elif self.current_view == "menu-gpg":
                detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {row_data[0]}\
[b][#44bbaa]Key ID:[/#44bbaa][/b] {row_data[1]}\
[b][#44bbaa]Email:[/#44bbaa][/b] {row_data[2]}\
[b][#44bbaa]Description:[/#44bbaa][/b] {row_data[3] or 'None'}"
            elif self.current_view == "menu-db":
                detail_text = f"[b][#44bbaa]Name:[/#44bbaa][/b] {row_data[0]}\
[b][#44bbaa]Type:[/#44bbaa][/b] {row_data[1]}\
[b][#44bbaa]Host:[/#44bbaa][/b] {row_data[2]}\
[b][#44bbaa]Port:[/#44bbaa][/b] {row_data[3]}\
[b][#44bbaa]User:[/#44bbaa][/b] {row_data[4]}\
[b][#44bbaa]Database Name:[/#44bbaa][/b] {row_data[5]}\
[b][#44bbaa]Description:[/#44bbaa][/b] {row_data[6] or 'None'}"

            if detail_text:
                detail_view.update(detail_text)
        except Exception:
            pass

    def load_data(self) -> None:
        table = self.query_one("#data_table")
        table.clear()
        db.connect(reuse_if_open=True)

        if self.current_view == "menu-ssh":
            for id, name, host, user, port, identity_file, description in SSHKey.select(SSHKey.id, SSHKey.name, SSHKey.host, SSHKey.user, SSHKey.port, SSHKey.identity_file, SSHKey.description).tuples():
                table.add_row(name, host, user, str(port), identity_file or "", description or "", key=str(id))
        elif self.current_view == "menu-gpg":
            for id, name, key_id, email, description in GPGKey.select(GPGKey.id, GPGKey.name, GPGKey.key_id, GPGKey.email, GPGKey.description).tuples():
                table.add_row(name, key_id, email, description or "", key=str(id))
        elif self.current_view == "menu-db":
            for id, name, type_, host, port, user, db_name, description in Database.select(Database.id, Database.name, Database.type, Database.host, Database.port, Database.user, Database.db_name, Database.description).tuples():
                table.add_row(name, type_, host, str(port), user, db_name, description or "", key=str(id))

        if not db.is_closed():
            db.close()

    def action_edit_entry(self) -> None:
        self.edit_entry()

    def get_selected_item_name(self) -> str | None:
        table = self.query_one("#data_table", DataTable)
        try:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
            row_data = table.get_row(row_key)
            return str(row_data[0]) # The name is the first column
        except Exception:
            return None

    def action_delete_entry(self) -> None:
        name = self.get_selected_item_name()
        if not name:
            self.notify("Please select an item to delete.", severity="warning")
            return

        def check_reply(confirm: bool) -> None:
            if confirm:
                db.connect(reuse_if_open=True)
                try:
                    if self.current_view == "menu-ssh":
                        SSHKey.delete().where(SSHKey.name == name).execute()
                    elif self.current_view == "menu-gpg":
                        GPGKey.delete().where(GPGKey.name == name).execute()
                    elif self.current_view == "menu-db":
                        Database.delete().where(Database.name == name).execute()
                    self.load_data()
                    self.notify(f"Deleted '{name}'.")
                except Exception as e:
                    self.notify(f"Error deleting record: {e}", severity="error")
                finally:
                    if not db.is_closed():
                        db.close()

        self.push_screen(ConfirmDeleteModal(name), check_reply)

    def action_add_entry(self) -> None:
        self.add_entry()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_add":
            self.add_entry()
        elif event.button.id == "btn_edit":
            self.edit_entry()
        elif event.button.id == "btn_delete":
            self.action_delete_entry()

    def edit_entry(self) -> None:
        name = self.get_selected_item_name()
        if not name:
            self.notify("Please select an item to edit.", severity="warning")
            return

        db.connect(reuse_if_open=True)
        try:
            if self.current_view == "menu-ssh":
                record = SSHKey.get(SSHKey.name == name)
                data = {"name": record.name, "host": record.host, "user": record.user, "port": record.port, "identity_file": record.identity_file, "description": record.description}
                self.edit_ssh(record, data)
            elif self.current_view == "menu-gpg":
                record = GPGKey.get(GPGKey.name == name)
                data = {"name": record.name, "key_id": record.key_id, "email": record.email, "description": record.description}
                self.edit_gpg(record, data)
            elif self.current_view == "menu-db":
                record = Database.get(Database.name == name)
                data = {"name": record.name, "type": record.type, "host": record.host, "port": record.port, "user": record.user, "db_name": record.db_name, "description": record.description}
                self.edit_db(record, data)
        except Exception as e:
            self.notify(f"Error fetching record: {e}", severity="error")
        finally:
            if not db.is_closed():
                db.close()

    def edit_ssh(self, record, data) -> None:
        def check_reply(new_data: dict | None) -> None:
            if new_data and new_data["name"]:
                try:
                    db.connect(reuse_if_open=True)
                    for k, v in new_data.items():
                        setattr(record, k, v)
                    record.save()

                    table = self.query_one("#data_table")
                    row_key = str(record.id)
                    columns = [col for col in table.columns]
                    table.update_cell(row_key, columns[0], record.name, update_width=True)
                    table.update_cell(row_key, columns[1], record.host, update_width=True)
                    table.update_cell(row_key, columns[2], record.user, update_width=True)
                    table.update_cell(row_key, columns[3], str(record.port), update_width=True)
                    table.update_cell(row_key, columns[4], record.identity_file or "", update_width=True)
                    table.update_cell(row_key, columns[5], record.description or "", update_width=True)
                except Exception as e:
                    self.notify(f"Error editing SSH Key: {e}", severity="error")
                finally:
                    if not db.is_closed():
                        db.close()
        self.push_screen(SSHModal(data), check_reply)

    def edit_gpg(self, record, data) -> None:
        def check_reply(new_data: dict | None) -> None:
            if new_data and new_data["name"]:
                try:
                    db.connect(reuse_if_open=True)
                    for k, v in new_data.items():
                        setattr(record, k, v)
                    record.save()

                    table = self.query_one("#data_table")
                    row_key = str(record.id)
                    columns = [col for col in table.columns]
                    table.update_cell(row_key, columns[0], record.name, update_width=True)
                    table.update_cell(row_key, columns[1], record.key_id, update_width=True)
                    table.update_cell(row_key, columns[2], record.email, update_width=True)
                    table.update_cell(row_key, columns[3], record.description or "", update_width=True)
                except Exception as e:
                    self.notify(f"Error editing GPG Key: {e}", severity="error")
                finally:
                    if not db.is_closed():
                        db.close()
        self.push_screen(GPGModal(data), check_reply)

    def edit_db(self, record, data) -> None:
        record_name = record.name
        def check_reply(new_data: dict | None) -> None:
            if new_data and new_data["name"]:
                try:
                    db.connect(reuse_if_open=True)
                    fresh_record = Database.get(Database.name == record_name)
                    for k, v in new_data.items():
                        setattr(fresh_record, k, v)
                    fresh_record.save()

                    table = self.query_one("#data_table")
                    row_key = str(fresh_record.id)
                    columns = [col for col in table.columns]
                    table.update_cell(row_key, columns[0], fresh_record.name, update_width=True)
                    table.update_cell(row_key, columns[1], fresh_record.type, update_width=True)
                    table.update_cell(row_key, columns[2], fresh_record.host, update_width=True)
                    table.update_cell(row_key, columns[3], str(fresh_record.port), update_width=True)
                    table.update_cell(row_key, columns[4], fresh_record.user, update_width=True)
                    table.update_cell(row_key, columns[5], fresh_record.db_name, update_width=True)
                    table.update_cell(row_key, columns[6], fresh_record.description or "", update_width=True)
                except Exception as e:
                    self.notify(f"Error editing Database: {e}", severity="error")
                finally:
                    if not db.is_closed():
                        db.close()
        self.push_screen(DatabaseModal(data), check_reply)

    def add_entry(self) -> None:
        if self.current_view == "menu-ssh":
            self.add_ssh()
        elif self.current_view == "menu-gpg":
            self.add_gpg()
        elif self.current_view == "menu-db":
            self.add_db()

    def add_ssh(self) -> None:
        def check_reply(data: dict | None) -> None:
            if data and data["name"]:
                try:
                    db.connect(reuse_if_open=True)
                    record = SSHKey.create(**data)
                    table = self.query_one("#data_table")
                    table.add_row(record.name, record.host, record.user, str(record.port), record.identity_file or "", record.description or "", key=str(record.id))
                except Exception as e:
                    self.notify(f"Error adding SSH Key: {e}", severity="error")
                finally:
                    if not db.is_closed():
                        db.close()
        self.push_screen(SSHModal(), check_reply)

    def add_gpg(self) -> None:
        def check_reply(data: dict | None) -> None:
            if data and data["name"]:
                try:
                    db.connect(reuse_if_open=True)
                    record = GPGKey.create(**data)
                    table = self.query_one("#data_table")
                    table.add_row(record.name, record.key_id, record.email, record.description or "", key=str(record.id))
                except Exception as e:
                    self.notify(f"Error adding GPG Key: {e}", severity="error")
                finally:
                    if not db.is_closed():
                        db.close()
        self.push_screen(GPGModal(), check_reply)

    def add_db(self) -> None:
        def check_reply(data: dict | None) -> None:
            if data and data["name"]:
                try:
                    db.connect(reuse_if_open=True)
                    record = Database.create(**data)
                    table = self.query_one("#data_table")
                    table.add_row(record.name, record.type, record.host, str(record.port), record.user, record.db_name, record.description or "", key=str(record.id))
                except Exception as e:
                    self.notify(f"Error adding Database: {e}", severity="error")
                finally:
                    if not db.is_closed():
                        db.close()
        self.push_screen(DatabaseModal(), check_reply)

if __name__ == "__main__":
    app = TrackerApp()
    app.run()
