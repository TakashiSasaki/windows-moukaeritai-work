class CatalogError(Exception):
    """Base exception for cataloging errors."""
    pass

class OutputFileExistsError(CatalogError):
    """Raised when the output file already exists."""
    def __init__(self, filepath):
        self.filepath = filepath
        super().__init__(f"Output file already exists: {filepath}")
