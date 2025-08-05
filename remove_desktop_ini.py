from pathlib import Path
import os
import base64

from textual.app import App, ComposeResult
from textual.containers import Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Checkbox
from textual.screen import ModalScreen
from textual.containers import Grid
from textual.binding import Binding
from textual.widgets import Label
from textual import events


class ConfirmationScreen(ModalScreen[bool]):
    """Screen with a dialog to confirm deletion."""

    def __init__(self, count: int) -> None:
        self.count = count
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(
                f"Are you sure you want to delete {self.count} file(s)?",
                id="question",
            ),
            Button("Delete", variant="error", id="delete"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            self.dismiss(True)
        else:
            self.dismiss(False)


class QuitScreen(ModalScreen[bool]):
    """Screen with a dialog to confirm quitting."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.dismiss(True)
        else:
            self.dismiss(False)


class RemoveDesktopIniApp(App):
    """A Textual app to find and remove desktop.ini files."""

    CSS_PATH = "remove_desktop_ini.css"
    BINDINGS = [
        Binding(key="q", action="request_quit", description="Quit"),
        Binding(
            key="ctrl+d",
            action="delete_selected",
            description="Delete Selected",
        ),
    ]

    def __init__(self):
        super().__init__()
        self.scan_counter = 0

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Vertical(
            Input(
                placeholder="Enter path or drag-and-drop a folder here",
                id="path_input",
            ),
            Button("Scan for desktop.ini files", variant="primary", id="scan"),
            ScrollableContainer(id="results"),
        )

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.query_one("#path_input").focus()

    def on_paste(self, event: events.Paste) -> None:
        """Handle paste events, e.g., from drag-and-drop."""
        input_widget = self.query_one("#path_input")
        pasted_path = event.text.strip().strip('"')
        if os.path.isdir(pasted_path):
            input_widget.value = pasted_path
            self.scan_directory()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "scan":
            self.scan_directory()

    def scan_directory(self):
        """Scans the directory specified in the Input for desktop.ini files."""
        self.scan_counter += 1
        path_str = self.query_one("#path_input").value
        results_container = self.query_one("#results")

        results_container.remove_children()

        if not path_str or not os.path.isdir(path_str):
            self.notify(
                "Please enter a valid directory path.",
                title="Error",
                severity="error",
            )
            return

        try:
            search_path = Path(path_str)
            found_files = []
            for root, _, files in os.walk(search_path):
                for file in files:
                    if file.lower() == "desktop.ini":
                        found_files.append(os.path.join(root, file))

            if not found_files:
                self.notify("No desktop.ini files found.")
                return

            for file_path in sorted(found_files):
                safe_id = (
                    f"scan-{self.scan_counter}-cb-"
                    + base64.urlsafe_b64encode(file_path.encode("utf-8"))
                    .decode("ascii")
                    .rstrip("=")
                )
                checkbox = Checkbox(file_path, id=safe_id)
                checkbox.file_path = file_path  # Store the real path here
                results_container.mount(checkbox)
        except Exception as e:
            self.notify(
                f"Error scanning directory: {e}",
                title="Error",
                severity="error",
            )

    def action_request_quit(self) -> None:
        """Action to display the quit confirmation screen."""
        self.push_screen(QuitScreen(), self._quit_callback)

    async def _quit_callback(self, confirmed: bool):
        if confirmed:
            self.exit()

    def get_selected_files(self) -> list[str]:
        """Get the paths of the selected files."""
        return [
            cb.file_path
            for cb in self.query("Checkbox")
            if cb.value and hasattr(cb, "file_path")
        ]

    def action_delete_selected(self) -> None:
        """Action to delete selected files."""
        selected_files = self.get_selected_files()
        if not selected_files:
            self.notify(
                "No files selected for deletion.",
                title="Warning",
                severity="warning",
            )
            return

        def delete_confirmed(confirmed: bool):
            if confirmed:
                deleted_count = 0
                error_count = 0
                for file_path in selected_files:
                    try:
                        os.remove(file_path)
                        for checkbox in self.query("Checkbox"):
                            if (
                                hasattr(checkbox, "file_path")
                                and checkbox.file_path == file_path
                            ):
                                checkbox.remove()
                                break
                        deleted_count += 1
                    except Exception as e:
                        self.notify(
                            f"Error deleting {file_path}: {e}",
                            title="Error",
                            severity="error",
                        )
                        error_count += 1

                if deleted_count > 0:
                    self.notify(
                        f"Successfully deleted {deleted_count} file(s)."
                    )
                if error_count > 0:
                    self.notify(f"Failed to delete {error_count} file(s).")

        self.push_screen(
            ConfirmationScreen(len(selected_files)), delete_confirmed
        )



if __name__ == "__main__":
    app = RemoveDesktopIniApp()
    app.run()
