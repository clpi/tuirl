from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Button, Input, Label, ListView, ListItem
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen

from .models import SSHKey, GPGKey, Database, db

class SSHModal(ModalScreen[dict]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Add SSH Key", id="title")
            yield Input(placeholder="Name", id="ssh_name")
            yield Input(placeholder="Host", id="ssh_host")
            yield Input(placeholder="User", id="ssh_user")
            yield Input(placeholder="Port (default: 22)", id="ssh_port")
            yield Input(placeholder="Identity File (optional)", id="ssh_identity")
            yield Input(placeholder="Description (optional)", id="ssh_desc")
            with Horizontal():
                yield Button("Save", variant="success", id="save_ssh")
                yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_ssh":
            data = {
                "name": self.query_one("#ssh_name").value,
                "host": self.query_one("#ssh_host").value,
                "user": self.query_one("#ssh_user").value,
                "port": self.query_one("#ssh_port").value or 22,
                "identity_file": self.query_one("#ssh_identity").value,
                "description": self.query_one("#ssh_desc").value,
            }
            self.dismiss(data)
        elif event.button.id == "cancel":
            self.dismiss(None)

class GPGModal(ModalScreen[dict]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Add GPG Key", id="title")
            yield Input(placeholder="Name", id="gpg_name")
            yield Input(placeholder="Key ID", id="gpg_key_id")
            yield Input(placeholder="Email", id="gpg_email")
            yield Input(placeholder="Description (optional)", id="gpg_desc")
            with Horizontal():
                yield Button("Save", variant="success", id="save_gpg")
                yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_gpg":
            data = {
                "name": self.query_one("#gpg_name").value,
                "key_id": self.query_one("#gpg_key_id").value,
                "email": self.query_one("#gpg_email").value,
                "description": self.query_one("#gpg_desc").value,
            }
            self.dismiss(data)
        elif event.button.id == "cancel":
            self.dismiss(None)

class DatabaseModal(ModalScreen[dict]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Add Database", id="title")
            yield Input(placeholder="Name", id="db_name")
            yield Input(placeholder="Type (e.g., postgres)", id="db_type")
            yield Input(placeholder="Host", id="db_host")
            yield Input(placeholder="Port", id="db_port")
            yield Input(placeholder="User", id="db_user")
            yield Input(placeholder="Database Name", id="db_dbname")
            yield Input(placeholder="Description (optional)", id="db_desc")
            with Horizontal():
                yield Button("Save", variant="success", id="save_db")
                yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_db":
            data = {
                "name": self.query_one("#db_name").value,
                "type": self.query_one("#db_type").value,
                "host": self.query_one("#db_host").value,
                "port": self.query_one("#db_port").value,
                "user": self.query_one("#db_user").value,
                "db_name": self.query_one("#db_dbname").value,
                "description": self.query_one("#db_desc").value,
            }
            self.dismiss(data)
        elif event.button.id == "cancel":
            self.dismiss(None)

class TrackerApp(App):
    CSS = """
    #app-container {
        layout: horizontal;
        height: 100%;
    }

    #sidebar {
        width: 25;
        height: 100%;
        dock: left;
        background: $panel;
        border-right: vkey $background;
    }

    #sidebar > ListView {
        height: 100%;
        background: transparent;
    }

    #sidebar > ListView > ListItem {
        padding: 1 2;
    }

    #main-content {
        width: 1fr;
        height: 100%;
        background: $surface;
        padding: 1 2;
    }

    #dialog {
        padding: 1 2;
        width: 60;
        height: auto;
        border: thick $primary 50%;
        background: $surface;
        border-top: round $primary;
        border-right: round $primary;
        border-bottom: round $primary;
        border-left: round $primary;
    }

    #title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        text-style: bold;
        color: $text;
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
        height: 1fr;
        border: round $primary;
        background: $panel;
    }

    .action-bar {
        height: 3;
        margin: 0 0 1 0;
        align: left middle;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_entry", "Add Entry"),
    ]

    theme = "tokyo-night"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="app-container"):
            with Vertical(id="sidebar"):
                yield ListView(
                    ListItem(Label("SSH Keys", classes="menu-label"), id="menu-ssh"),
                    ListItem(Label("GPG Keys", classes="menu-label"), id="menu-gpg"),
                    ListItem(Label("Databases", classes="menu-label"), id="menu-db"),
                    id="menu"
                )

            with Vertical(id="main-content"):
                with Horizontal(classes="action-bar"):
                    yield Button("Add Entry", id="btn_add", variant="primary")
                yield DataTable(id="data_table", cursor_type="row", zebra_stripes=True)

        yield Footer()

    def on_mount(self) -> None:
        self.current_view = "menu-ssh"
        table = self.query_one(DataTable)
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
        table = self.query_one(DataTable)
        table.clear(columns=True)

        if view_id == "menu-ssh":
            table.add_columns("Name", "Host", "User", "Port", "Identity File", "Description")
        elif view_id == "menu-gpg":
            table.add_columns("Name", "Key ID", "Email", "Description")
        elif view_id == "menu-db":
            table.add_columns("Name", "Type", "Host", "Port", "User", "Database", "Description")

        self.load_data()

    def load_data(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        db.connect(reuse_if_open=True)

        if self.current_view == "menu-ssh":
            for ssh in SSHKey.select():
                table.add_row(ssh.name, ssh.host, ssh.user, str(ssh.port), ssh.identity_file or "", ssh.description or "")
        elif self.current_view == "menu-gpg":
            for gpg in GPGKey.select():
                table.add_row(gpg.name, gpg.key_id, gpg.email, gpg.description or "")
        elif self.current_view == "menu-db":
            for database in Database.select():
                table.add_row(database.name, database.type, database.host, str(database.port), database.user, database.db_name, database.description or "")

        if not db.is_closed():
            db.close()

    def action_add_entry(self) -> None:
        self.add_entry()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_add":
            self.add_entry()

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
                    SSHKey.create(**data)
                    self.load_data()
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
                    GPGKey.create(**data)
                    self.load_data()
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
                    Database.create(**data)
                    self.load_data()
                except Exception as e:
                    self.notify(f"Error adding Database: {e}", severity="error")
                finally:
                    if not db.is_closed():
                        db.close()
        self.push_screen(DatabaseModal(), check_reply)

if __name__ == "__main__":
    app = TrackerApp()
    app.run()
