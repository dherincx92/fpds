"""
Outputs FPDS data into partitioned-sized JSON gzip files.

author: derek663@gmail.com
last_updated: 12/14/2025
"""

import gzip
import json
from pathlib import Path
from typing import List
from uuid import uuid4

from fpds.core import FPDS_ENTRY

class fpdsChunkWriter:
    def __init__(
        self,
        output_dir: Path,
        max_chunk_size_mb: int,
    ) -> None:
        self.output_dir = output_dir
        self.max_bytes = max_chunk_size_mb * 1_048_576
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def record_size(entry: FPDS_ENTRY) -> int:
        entry_json = json.dumps(entry)
        return len(entry_json.encode("utf-8"))

    async def chunkify(self, entries):
        file_paths: list[Path] = []
        chunk: List[FPDS_ENTRY] = []
        current_size = 0

        async for entry in entries:
            size = self.record_size(entry)

            if current_size + size > self.max_bytes and chunk:
                file_paths.append(self.flush(chunk))
                chunk = [entry]
                current_size = size
            else:
                chunk.append(entry)
                current_size += size

        if chunk:
            file_paths.append(self.flush(chunk))

        return file_paths


    def flush(self, chunk_buffer: list[FPDS_ENTRY]) -> Path:
        file_path = self.output_dir / f"{uuid4()}.json.gz"
        with gzip.open(file_path, "wt", encoding="utf-8") as gz_file:
            json.dump(chunk_buffer, gz_file)
