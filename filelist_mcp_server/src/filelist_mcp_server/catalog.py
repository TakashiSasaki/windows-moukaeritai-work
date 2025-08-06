import os
import csv
import datetime
from pathlib import Path

from .exceptions import OutputFileExistsError

def _walk_directory(target_path: Path):
    """
    Walks a directory and yields information for each file.

    Args:
        target_path: The path to the directory to walk.

    Yields:
        A tuple containing (full_path, size, modified_time, created_time).
    """
    for root, _, files in os.walk(target_path):
        for filename in files:
            filepath = Path(root) / filename
            try:
                stat = filepath.stat()
                # On Windows, st_ctime is the creation time.
                created_time = datetime.datetime.fromtimestamp(stat.st_ctime)
                modified_time = datetime.datetime.fromtimestamp(stat.st_mtime)
                size = stat.st_size
                yield str(filepath.resolve()), size, created_time, modified_time
            except OSError:
                # Ignore files that can't be accessed (e.g. permission errors)
                continue

def _write_efu_file(file_info_generator, output_path: Path):
    """
    Writes file information to a TSV file in EFU format.

    Args:
        file_info_generator: A generator that yields file information tuples.
        output_path: The path to the output TSV file.
    """
    header = ["Filename", "Size", "Date Modified", "Date Created"]
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        for filepath, size, created_time, modified_time in file_info_generator:
            writer.writerow([
                filepath,
                size,
                modified_time.isoformat(),
                created_time.isoformat()
            ])

def create_catalog(target_dir: str, output_file: str):
    """
    Creates a catalog of files in a directory and saves it as a TSV file.

    Args:
        target_dir: The directory to catalog.
        output_file: The path to the output TSV file.

    Raises:
        OutputFileExistsError: If the output file already exists.
        FileNotFoundError: If the target directory does not exist.
    """
    target_path = Path(target_dir)
    output_path = Path(output_file)

    if not target_path.is_dir():
        raise FileNotFoundError(f"Target directory not found: {target_dir}")

    # To prevent accidental overwrites, check for existence before any processing.
    # The check is performed here to catch the error early.
    if output_path.exists():
        raise OutputFileExistsError(str(output_path))

    file_info_gen = _walk_directory(target_path)
    _write_efu_file(file_info_gen, output_path)
