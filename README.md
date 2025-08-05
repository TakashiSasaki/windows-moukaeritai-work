# remove-desktop-ini

A Textual TUI (Terminal User Interface) application designed to help Windows users find and remove unwanted `desktop.ini` files.

## Purpose

`desktop.ini` files are hidden system files that Windows uses to store customization settings for folders. While generally harmless, they can sometimes be generated unexpectedly or become a nuisance, especially when dealing with many folders or when these files are not desired. This application provides a convenient way to scan for and selectively delete these files from your system.

## Features

-   **Intuitive TUI:** A clean and interactive terminal user interface built with the Textual framework.
-   **Directory Scanning:** Scan any specified directory (and its subdirectories) for `desktop.ini` files.
-   **Drag-and-Drop Support:** Easily specify the target directory by dragging and dropping a folder or even a file (its parent directory will be used) directly into the input field.
-   **Selectable List:** Displays found `desktop.ini` files in a scrollable list.
-   **Keyboard Navigation:** Navigate the file list using arrow keys and select/deselect files with the Spacebar.
-   **Batch Selection:** "Select All" (`Ctrl+A`) and "Select None" (`Ctrl+N`) buttons/shortcuts for efficient management.
-   **Safe Deletion:** Delete selected files with a confirmation prompt to prevent accidental data loss.
-   **Usage Information:** Press `?` to display a quick usage guide within the application.

## Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/your-username/remove-desktop-ini.git
    cd remove-desktop-ini
    ```

2.  **Install Textual:**
    This application requires the `textual` library. You can install it using pip:
    ```bash
    pip install textual
    ```

## How to Run

Navigate to the application's directory in your terminal and run the Python script:

```bash
python remove_desktop_ini.py
```

## How to Use

1.  **Specify Directory:**
    *   **Type:** Manually type the path to the directory you want to scan into the input field.
    *   **Drag-and-Drop:** Drag a folder or a file from your file explorer directly onto your terminal window where the application is running. The path will automatically populate the input field.

2.  **Scan:** Click the "Scan for desktop.ini files" button or press `Enter` (after typing a path) to start the scan.

3.  **Select Files:**
    *   Use the **Arrow Keys** (Up/Down) to navigate the list of found `desktop.ini` files.
    *   Press the **Spacebar** to select or deselect individual files.
    *   Click the "Select All" button or press `Ctrl+A` to select all files in the list.
    *   Click the "Select None" button or press `Ctrl+N` to deselect all files.

4.  **Delete Selected:** Click the "Delete Selected" button or press `Ctrl+D` to delete all currently selected `desktop.ini` files. A confirmation dialog will appear.

5.  **Quit:** Press `Q` to quit the application. A confirmation dialog will appear.

6.  **Usage Guide:** Press `?` at any time to display a quick usage guide within the application.
