import logging
import os
from pathlib import Path
from typing import Dict

import exiftool

logger = logging.getLogger(__name__)


class FileUtils:
    @staticmethod
    def get_file_metadata(file_path: str) -> Dict:
        logger.debug(f"Extracting metadata for file: {file_path}")
        metadata = {
            "file_system": {},
            "embedded": {},
        }

        if not os.path.exists(file_path):
            logger.warning(f"File does not exist: {file_path}")
            return metadata

        try:
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
            logger.debug(
                f"File system metadata extracted: {metadata['file_system']['file_name']} "
                f"({metadata['file_system']['size_mb']} MB)"
            )
        except OSError as e:
            logger.error(f"Failed to get file system metadata for {file_path}: {e}", exc_info=True)
            metadata["file_system"]["error"] = str(e)

        try:
            logger.debug(f"Extracting embedded metadata using exiftool for {file_path}")
            metadata["embedded"] = exiftool.ExifToolHelper().get_metadata(file_path)[0]
            logger.debug("Successfully extracted embedded metadata")
        except Exception as e:
            logger.warning(f"Error extracting embedded metadata for {file_path}: {e}")
            metadata["embedded"]["extraction_error"] = str(e)

        return metadata
