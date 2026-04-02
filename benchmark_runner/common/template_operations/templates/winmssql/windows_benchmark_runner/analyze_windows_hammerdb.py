import os
import re
import json
import logging
from pathlib import Path

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalyzeWindowsHammerDB():
    def __init__(self):
        pass

    def get_json_files(self, hammerdb_results_path: str) -> list[str]:
        """
        Returns a list of full paths of all .json files in the specified directory.
        Args:
            hammerdb_results_path (str): Path to the directory.
        Returns:
            list[str]: List of full paths to JSON files in the directory.
        """
        path = Path(hammerdb_results_path)
        return [str(file) for file in path.iterdir() if file.is_file() and file.suffix == '.json']

    def get_tpm_per_worker(self, json_files):
        """
        Extract the average TPM per worker from a list of JSON files.
        Args:
            json_files (list[str]): List of JSON file paths containing HammerDB results.
        Returns:
            dict[int, int]: Dictionary mapping worker ID to its average TPM (rounded to int).
        """
        results = {}  # worker_id -> list of TPM values
        for json_file in json_files:
            logger.info(f"Analyzing: {json_file}")
            try:
                # Extract worker ID using regex instead of split
                match = re.search(r'_([0-9]+)vu_', json_file)
                if not match:
                    raise ValueError(f"Cannot extract worker ID from filename: {json_file}")
                current_worker = int(match.group(1))

                current_avg_tpm = self.extract_avg_tpm(json_file)

                if current_worker not in results:
                    results[current_worker] = []
                results[current_worker].append(current_avg_tpm)

            except Exception as e:
                logger.error(f"Skipping file due to error: {json_file} -> {e}")

        # Convert lists to average TPM per worker (same format as before: int values)
        return {
            worker: int(round(sum(tpms) / len(tpms))) if tpms else 0
            for worker, tpms in results.items()
        }

    def extract_avg_tpm(self, json_file):
        """
        Extract the average TPM value from a single JSON file.
        Handles Windows and Linux line endings and different encodings.
        Args:
            json_file (str): Path to the JSON file containing HammerDB results.
        Returns:
            float: Average TPM value found in the file.
        """
        # Detect possible encoding
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            # Try UTF-16 (common on Windows)
            with open(json_file, "r", encoding="utf-16") as f:
                text = f.read()

        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Regex to extract the JSON block of MSSQLServer tpm
        pattern = r'{"MSSQLServer tpm":\s*\{.*?\}\s*}'
        match = re.search(pattern, text, re.DOTALL)

        if not match:
            logger.error(f"Could not find MSSQLServer tpm JSON block in file: {json_file}")
            logger.error(text[:500])
            raise ValueError("Could not find MSSQLServer tpm JSON block")

        json_str = match.group(0)

        # Parse JSON
        data = json.loads(json_str)
        tpm_dict = data["MSSQLServer tpm"]

        # Convert values to integers
        tpm_values = [int(v) for v in tpm_dict.values() if int(v) > 0]
        if not tpm_values:
            return 0
        return sum(tpm_values) / len(tpm_values)

    def hammerdb_results_for_elasticsearch(self, hammerdb_results: dict, output_file: str) -> list[dict]:
        """
        Prepare HammerDB results in a format suitable for Elasticsearch
        and write them to a JSON file.

        Args:
            hammerdb_results (dict): Dictionary of worker_id -> average TPM
            output_file (str): Path to output JSON file (default: hammerdb_result.json)

        Returns:
            list[dict]: List of results in {"current_worker": id, "tpm": value} format
        """
        sorted_results = [
            {"current_worker": k, "tpm": v}
            for k, v in sorted(hammerdb_results.items())
        ]

        output_path = Path(output_file)
        if output_path.exists():
            logger.info(f"Overwriting existing file: {output_path.resolve()}")

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(sorted_results, f, indent=4)

        logger.info(f"HammerDB results written to {output_path.resolve()}")
        return sorted_results


if __name__ == "__main__":
    hammerdb_results_path = os.path.join(Path.cwd().parent, 'results')
    analyze_db = AnalyzeWindowsHammerDB()
    json_files = analyze_db.get_json_files(hammerdb_results_path=hammerdb_results_path)
    hammerdb_results = analyze_db.get_tpm_per_worker(json_files)
    hammerdb_results_list = analyze_db.hammerdb_results_for_elasticsearch(hammerdb_results, output_file=os.path.join(hammerdb_results_path,'hammerdb_result.json'))
    logger.info(hammerdb_results_list)
