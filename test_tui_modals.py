import pytest
from textual.app import App
from src.tui import SSHModal, GPGModal, DatabaseModal

class DummyApp(App):
    pass

@pytest.mark.asyncio
async def test_ssh_modal_get_form_data():
    app = DummyApp()
    async with app.run_test() as pilot:
        modal = SSHModal()
        app.push_screen(modal)
        await pilot.pause()

        modal.query_one("#ssh_name").value = "myssh"
        modal.query_one("#ssh_host").value = "192.168.1.1"
        modal.query_one("#ssh_user").value = "root"
        modal.query_one("#ssh_port").value = "2222"
        modal.query_one("#ssh_identity").value = "~/.ssh/id_rsa"
        modal.query_one("#ssh_desc").value = "Test SSH key"

        data = modal.get_form_data()
        assert data == {
            "name": "myssh",
            "host": "192.168.1.1",
            "user": "root",
            "port": "2222",
            "identity_file": "~/.ssh/id_rsa",
            "description": "Test SSH key",
        }

@pytest.mark.asyncio
async def test_ssh_modal_get_form_data_default_port():
    app = DummyApp()
    async with app.run_test() as pilot:
        modal = SSHModal()
        app.push_screen(modal)
        await pilot.pause()

        modal.query_one("#ssh_name").value = "myssh2"
        modal.query_one("#ssh_host").value = "192.168.1.2"
        modal.query_one("#ssh_user").value = "admin"
        # Not setting port, it should default to 22
        modal.query_one("#ssh_identity").value = ""
        modal.query_one("#ssh_desc").value = ""

        data = modal.get_form_data()
        assert data == {
            "name": "myssh2",
            "host": "192.168.1.2",
            "user": "admin",
            "port": 22,
            "identity_file": "",
            "description": "",
        }

@pytest.mark.asyncio
async def test_gpg_modal_get_form_data():
    app = DummyApp()
    async with app.run_test() as pilot:
        modal = GPGModal()
        app.push_screen(modal)
        await pilot.pause()

        modal.query_one("#gpg_name").value = "mygpg"
        modal.query_one("#gpg_key_id").value = "12345678"
        modal.query_one("#gpg_email").value = "test@example.com"
        modal.query_one("#gpg_desc").value = "Test GPG key"

        data = modal.get_form_data()
        assert data == {
            "name": "mygpg",
            "key_id": "12345678",
            "email": "test@example.com",
            "description": "Test GPG key",
        }

@pytest.mark.asyncio
async def test_db_modal_get_form_data():
    app = DummyApp()
    async with app.run_test() as pilot:
        modal = DatabaseModal()
        app.push_screen(modal)
        await pilot.pause()

        modal.query_one("#db_name").value = "mydb"
        modal.query_one("#db_type").value = "postgres"
        modal.query_one("#db_host").value = "localhost"
        modal.query_one("#db_port").value = "5432"
        modal.query_one("#db_user").value = "dbuser"
        modal.query_one("#db_dbname").value = "testdb"
        modal.query_one("#db_desc").value = "Test Database"

        data = modal.get_form_data()
        assert data == {
            "name": "mydb",
            "type": "postgres",
            "host": "localhost",
            "port": "5432",
            "user": "dbuser",
            "db_name": "testdb",
            "description": "Test Database",
        }
