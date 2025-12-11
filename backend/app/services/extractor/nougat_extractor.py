
import subprocess
from pathlib import Path
from .base import BaseExtractor
import anyio
from typing import Dict, Any
import os

class NougatExtractor(BaseExtractor):
    """
    Extracts content using the external Nougat command line tool (CLI).
    Wraps the synchronous CLI call to run asynchronously.
    """

    async def extract(self, file_path: str, subject_name: str = None) -> Dict[str, Any]:
        output_dir = Path(file_path).parent
        
        def _sync_nougat_run():
            try:
                print(f"Executing Nougat CLI on {file_path}")
                subprocess.run([
                    "nougat",
                    file_path,
                    "--output", str(output_dir) 
                ], check=True, capture_output=True, text=True)

                input_stem = Path(file_path).stem
                final_md_path = output_dir / f"{input_stem}.mmd"
                
                if not final_md_path.exists():
                     raise FileNotFoundError(f"Output not found at {final_md_path}")
                
                markdown_content = final_md_path.read_text(encoding='utf-8')
                os.remove(final_md_path)

                return {
                    "raw_text": markdown_content,
                    "markdown": markdown_content,
                    "meta": { "source": "nougat_cli" }
                }
            except Exception as e:
                print(f"FATAL ERROR during Nougat process: {e}")
                return {
                    "raw_text": "",
                    "markdown": f"## Extraction Error\n\n{str(e)}",
                    "meta": { "source": "nougat_cli", "error": str(e) }
                }

        return await anyio.to_thread.run_sync(_sync_nougat_run)