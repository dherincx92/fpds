"""
Outputs FPDS data into partitioned-sized JSON gzip files.

author: derek663@gmail.com
last_updated: 12/14/2025
"""

import gzip
import json
from pathlib import Path
from typing import AsyncGenerator
from uuid import uuid4

from fpds.core import FPDS_ENTRY


class FPDSChunkWriter:
    """Chunks FPDS request data into JSON gzip files.

    Attributes
    ----------
    output_dir: `Path`
        Output directory.
    max_chunk_size_mb: `int`
        The maximum size of each outputted data file (uncompressed).
    """

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
        """Calculates the size of an FPDS entry record."""
        entry_json = json.dumps(entry)
        return len(entry_json.encode("utf-8"))

    async def chunkify(self, entries: AsyncGenerator[FPDS_ENTRY, None]) -> None:
        """Chunkifies FPDS entries into JSON gzip files of :max_chunk_size_mb: size."""
        chunk: list[FPDS_ENTRY] = []
        current_size = 0

        async for entry in entries:
            size = self.record_size(entry)

            if current_size + size > self.max_bytes and chunk:
                self.flush(chunk)
                chunk = [entry]
                current_size = size
            else:
                chunk.append(entry)
                current_size += size

        if chunk:
            self.flush(chunk)

    def flush(self, chunk_buffer: list[FPDS_ENTRY]) -> None:
        file_path = self.output_dir / f"{uuid4()}.json.gz"
        with gzip.open(file_path, "wt", encoding="utf-8") as gz_file:
            json.dump(chunk_buffer, gz_file)
