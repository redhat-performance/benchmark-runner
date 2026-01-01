
import os
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from dotenv import load_dotenv
from pathlib import Path

from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations, ElasticSearchDataNotUploaded

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ElasticSearchUploader(object):
    def __init__(self):
        load_dotenv()  # loads .env in current directory
        self._es_host = os.getenv("ElasticSearch_HOST", '')
        self._es_port = os.getenv("ElasticSearch_Port", '')
        self._es_index = os.getenv("ElasticSearch_Index")
        self._hammerdb_metadata_str = os.getenv("HammerDB_Metadata", "{}")
        self._hammerdb_metadata = json.loads(self._hammerdb_metadata_str)
        self._hammerdb_results_file = os.path.join(Path.cwd().parent,'results','hammerdb_result.json')
        if self._es_host:
            self._elasticsearch = ElasticSearchOperations(es_host=self._es_host,es_port=self._es_port)


    def read_hammerdb_results(self, json_file: str) -> list[dict]:
        """
        Read HammerDB results JSON file and return it as a list of dictionaries.
        Handles Windows UTF-16 / UTF-8 BOM and ensures integers for 'current_worker' and 'tpm'.

        Args:
            json_file (str): Path to hammerdb_result.json

        Returns:
            list[dict]: List of HammerDB results with keys 'current_worker' and 'tpm'
        """
        try:
            # Try reading as UTF-8 and strip BOM if present
            with open(json_file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except UnicodeDecodeError:
            # Fallback to UTF-16 (common on Windows)
            with open(json_file, "r", encoding="utf-16") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error(f"File not found: {json_file}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {json_file}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error reading {json_file}: {e}")
            return []

        # Normalize data
        results_list = []
        for item in data:
            try:
                results_list.append({
                    "current_worker": int(item["current_worker"]),
                    "tpm": int(item["tpm"])
                })
            except Exception as e:
                logger.warning(f"Skipping invalid item in JSON: {item} -> {e}")

        return results_list

    def enrich_hammerdb_result(self, hammerdb_results: list[dict]) -> list[dict]:
        """
        Enrich HammerDB results with metadata before sending to Elasticsearch.
        """
        for row in hammerdb_results:  # iterate over the passed list
            row.update(self._hammerdb_metadata)  # add hammerdb metadata to each row
        return hammerdb_results

    def upload_to_elasticsearch(self, index: str, data: dict) -> list[str]:
        """
        Upload HammerDB results to Elasticsearch and return list of uuids
        """
        try:
            uuids = []
            for row in data:
                # Update row with uuid
                uuid = str(uuid4())
                data.update({'uuid': uuid, 'status': 'Succeeded'})
                response = self._elasticsearch.upload_to_elasticsearch(index=index, data=data, timestamp=datetime.now(timezone.utc)-timedelta(hours=8))
                uuids.append(uuid)
            # Log success
            logger.info(f"Uploaded to Elasticsearch index '{index}', response: {response}")
            return uuids
        except Exception as e:
            logger.error(f"Failed to upload data to Elasticsearch index '{index}': {e}")
            raise

    def verify_data_upload_into_elasticsearch(self, index: str, expected_uuids_list: list) -> bool:
        """
        Verify that data is uploaded into Elasticsearch by verify the existing of uuids
        """
        current_datetime = datetime.now(timezone.utc)
        end_datetime = current_datetime + timedelta(hours=12)
        start_datetime = current_datetime - timedelta(hours=12)
        ids = self._elasticsearch.get_index_ids_between_dates(index=index, start_datetime=start_datetime,end_datetime=end_datetime)
        actual_ids_uuids = self._elasticsearch.get_uuid_for_ids(index=index, ids=ids)
        actual_uuids_list = list(actual_ids_uuids.values())
        all_present = set(expected_uuids_list).issubset(actual_uuids_list)
        if all_present:
            logger.info("Data uploaded to Elasticsearch")
            return True
        else:
            logger.info("Data is not uploaded to Elasticsearch")
            raise ElasticSearchDataNotUploaded

if __name__ == "__main__":
    es_uploader = ElasticSearchUploader()
    if es_uploader._es_host:
        hammerdb_results = es_uploader.read_hammerdb_results(json_file=es_uploader._hammerdb_results_file)
        hammerdb_results = es_uploader.enrich_hammerdb_result(hammerdb_results)
        logger.info(hammerdb_results)
        expected_uuids = es_uploader.upload_to_elasticsearch(index=es_uploader._es_index, data=hammerdb_results)
        logger.info("Wait 60 seconds for the data to be documented")
        time.sleep(60)
        es_uploader.verify_data_upload_into_elasticsearch(index=es_uploader._es_index, expected_uuids_list=expected_uuids)
    else:
        logger.info("HammerDB results not uploaded to Elasticsearch, configure host in .env file")
