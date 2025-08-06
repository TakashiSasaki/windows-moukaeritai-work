import tempfile
import shutil
from pathlib import Path
import csv
import pytest

# Note: Poetry automatically adjusts the path so we can import the module.
from filelist_mcp_server.catalog import create_catalog
from filelist_mcp_server.exceptions import OutputFileExistsError


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files and clean up afterwards."""
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(d)


def test_create_catalog_success(temp_dir):
    """Test successful creation of a catalog file for a directory with files."""
    # Setup: Create a directory structure with some files
    source_dir = temp_dir / "source"
    output_file = temp_dir / "catalog.tsv"

    (source_dir / "subdir").mkdir(parents=True, exist_ok=True)
    (source_dir / "file1.txt").write_text("hello")
    (source_dir / "subdir" / "file2.log").write_text("world log")

    # Execute the function to be tested
    create_catalog(str(source_dir), str(output_file))

    # Verify the result
    assert output_file.exists()
    with open(output_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)

        # Verify header
        assert rows[0] == ["Filename", "Size", "Date Modified", "Date Created"]

        # Verify content (order is not guaranteed, so check presence)
        # We check the names and sizes, as timestamps can be tricky.

        # Strip paths for stable comparison
        file_data = {Path(row[0]).name: row[1] for row in rows[1:]}

        assert "file1.txt" in file_data
        assert file_data["file1.txt"] == str(len("hello"))

        assert "file2.log" in file_data
        assert file_data["file2.log"] == str(len("world log"))

        # Verify total row count
        assert len(rows) == 3  # 1 header + 2 files


def test_create_catalog_output_exists(temp_dir):
    """Test that an OutputFileExistsError is raised if the output file already exists."""
    source_dir = temp_dir / "source"
    source_dir.mkdir()
    output_file = temp_dir / "catalog.tsv"
    output_file.touch()  # Pre-create the output file

    with pytest.raises(OutputFileExistsError):
        create_catalog(str(source_dir), str(output_file))


def test_create_catalog_empty_directory(temp_dir):
    """Test that cataloging an empty directory results in a file with only a header."""
    source_dir = temp_dir / "source"
    source_dir.mkdir()
    output_file = temp_dir / "catalog.tsv"

    create_catalog(str(source_dir), str(output_file))

    assert output_file.exists()
    with open(output_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        rows = list(reader)
        assert len(rows) == 1  # Only the header row should exist
        assert rows[0] == ["Filename", "Size", "Date Modified", "Date Created"]


def test_create_catalog_source_not_found(temp_dir):
    """Test that a FileNotFoundError is raised if the source directory does not exist."""
    non_existent_dir = temp_dir / "non_existent"
    output_file = temp_dir / "catalog.tsv"

    with pytest.raises(FileNotFoundError):
        create_catalog(str(non_existent_dir), str(output_file))
