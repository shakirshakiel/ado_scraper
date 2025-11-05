import os
from pathlib import Path
from typing import Dict

import exiftool


class FileUtils:
    @staticmethod
    def get_file_metadata(file_path: str) -> Dict:
        metadata = {
            "file_system": {},
            "embedded": {},
        }

        if not os.path.exists(file_path):
            return metadata

        stat = os.stat(file_path)
        metadata["file_system"] = {
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_time": stat.st_ctime,
            "modified_time": stat.st_mtime,
            "absolute_path": os.path.abspath(file_path),
            "file_extension": Path(file_path).suffix.lower(),
            "file_name": os.path.basename(file_path),
        }

        try:
            metadata["embedded"] = exiftool.ExifToolHelper().get_metadata(file_path)[0]
        except Exception as e:
            print(f"Error extracting metadata for {file_path}: {e}")
            metadata["embedded"]["extraction_error"] = str(e)

        return metadata
