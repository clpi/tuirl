from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, DataTable, Button, Input, Label
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
    #dialog {
        padding: 1 2;
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
    }
    #title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        text-style: bold;
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
    }
    .action-bar {
        height: 3;
        margin: 1 0;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_entry", "Add Entry"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="ssh-tab"):
            with TabPane("SSH", id="ssh-tab"):
                with Horizontal(classes="action-bar"):
                    yield Button("Add SSH Key", id="btn_add_ssh", variant="primary")
                yield DataTable(id="ssh_table")

            with TabPane("GPG", id="gpg-tab"):
                with Horizontal(classes="action-bar"):
                    yield Button("Add GPG Key", id="btn_add_gpg", variant="primary")
                yield DataTable(id="gpg_table")

            with TabPane("Database", id="db-tab"):
                with Horizontal(classes="action-bar"):
                    yield Button("Add Database", id="btn_add_db", variant="primary")
                yield DataTable(id="db_table")
        yield Footer()

    def on_mount(self) -> None:
        ssh_table = self.query_one("#ssh_table", DataTable)
        ssh_table.add_columns("Name", "Host", "User", "Port", "Identity File", "Description")

        gpg_table = self.query_one("#gpg_table", DataTable)
        gpg_table.add_columns("Name", "Key ID", "Email", "Description")

        db_table = self.query_one("#db_table", DataTable)
        db_table.add_columns("Name", "Type", "Host", "Port", "User", "Database", "Description")

        self.load_data()

    def load_data(self) -> None:
        ssh_table = self.query_one("#ssh_table", DataTable)
        ssh_table.clear()
        db.connect(reuse_if_open=True)
        for ssh in SSHKey.select():
            ssh_table.add_row(ssh.name, ssh.host, ssh.user, str(ssh.port), ssh.identity_file or "", ssh.description or "")

        gpg_table = self.query_one("#gpg_table", DataTable)
        gpg_table.clear()
        for gpg in GPGKey.select():
            gpg_table.add_row(gpg.name, gpg.key_id, gpg.email, gpg.description or "")

        db_table = self.query_one("#db_table", DataTable)
        db_table.clear()
        for database in Database.select():
            db_table.add_row(database.name, database.type, database.host, str(database.port), database.user, database.db_name, database.description or "")
        db.close()

    def action_add_entry(self) -> None:
        active_tab = self.query_one(TabbedContent).active
        if active_tab == "ssh-tab":
            self.add_ssh()
        elif active_tab == "gpg-tab":
            self.add_gpg()
        elif active_tab == "db-tab":
            self.add_db()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_add_ssh":
            self.add_ssh()
        elif event.button.id == "btn_add_gpg":
            self.add_gpg()
        elif event.button.id == "btn_add_db":
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
