"""A Textual application to find and remove desktop.ini files.

This application provides a terminal user interface (TUI) for scanning a specified directory
(or its parent if a file is dropped) for 'desktop.ini' files, allowing users to select and
delete them. It supports keyboard navigation, select all/none functionality, and confirmation
dialogs for safe operation.
"""

from pathlib import Path
import os
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Input, Button, SelectionList
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


class UsageScreen(ModalScreen[None]):
    """Screen with usage information."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(
                """Usage:

- Drag and drop a folder or file onto the input field to scan.
- Use arrow keys to navigate the file list.
- Press Space to select/deselect files.
- Ctrl+A: Select All
- Ctrl+N: Select None
- Ctrl+D: Delete Selected
- Q: Quit
- ?: Show this usage screen
""",
                id="usage_text",
            ),
            Button("Close", variant="primary", id="close_usage"),
            id="usage_dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_usage":
            self.dismiss()


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
        Binding(key="ctrl+a", action="select_all", description="Select All"),
        Binding(key="ctrl+n", action="select_none", description="Select None"),
        Binding(key="?", action="show_usage", description="Show Usage"),
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
            Horizontal(
                Button("Scan for desktop.ini files", variant="primary", id="scan"),
                Button("Select All", id="select_all"),
                Button("Select None", id="select_none"),
            ),
            SelectionList[str](id="results"),
            id="main_content",
        )

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.query_one("#path_input").focus()
        self.app.command_palette.register_command(
            self, "Show Current Directory", self.action_show_current_directory
        )

    def on_paste(self, event: events.Paste) -> None:
        """Handle paste events, e.g., from drag-and-drop."""
        input_widget = self.query_one("#path_input")
        pasted_path = event.text.strip().strip('"')

        if os.path.isfile(pasted_path):
            pasted_path = os.path.dirname(pasted_path)
            input_widget.value = pasted_path
            self.scan_directory()
        elif os.path.isdir(pasted_path):
            input_widget.value = pasted_path
            self.scan_directory()
        else:
            self.notify("Invalid path. Please drag-and-drop a folder or file.",
                        title="Error", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "scan":
            self.scan_directory()
        elif event.button.id == "select_all":
            self.action_select_all()
        elif event.button.id == "select_none":
            self.action_select_none()

    def scan_directory(self):
        """Scans the directory specified in the Input for desktop.ini files."""
        self.scan_counter += 1
        path_str = self.query_one("#path_input").value
        selection_list = self.query_one("#results", SelectionList)

        selection_list.clear_options()

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

            options = []
            for file_path in sorted(found_files):
                options.append((file_path, file_path))

            selection_list.add_options(options)
            selection_list.focus()

        except Exception as e:
            self.notify(
                f"Error scanning directory: {e}",
                title="Error",
                severity="error",
            )

    def action_request_quit(self) -> None:
        """Action to display the quit confirmation screen."""
        self.push_screen(QuitScreen(), self._quit_callback)

    def action_show_usage(self) -> None:
        """Action to display the usage screen."""
        self.push_screen(UsageScreen())

    async def _quit_callback(self, confirmed: bool):
        if confirmed:
            self.exit()

    def action_select_all(self) -> None:
        """Selects all items in the list."""
        selection_list = self.query_one("#results", SelectionList)
        selection_list.select_all()

    def action_select_none(self) -> None:
        """Deselects all items in the list."""
        selection_list = self.query_one("#results", SelectionList)
        selection_list.deselect_all()

    def get_selected_files(self) -> list[str]:
        """Get the paths of the selected files."""
        selection_list = self.query_one("#results", SelectionList)
        return selection_list.selected

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
                        deleted_count += 1
                    except Exception as e:
                        self.notify(
                            f"Error deleting {file_path}: {e}",
                            title="Error",
                            severity="error",
                        )
                        error_count += 1

                # After deletion, refresh the list to remove deleted items
                self.scan_directory()

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
