import time

from uuid import uuid4
from datetime import timedelta

from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from tests.integration.benchmark_runner.test_environment_variables import *

TEST_INDEX_NAME = 'benchmark-runner-test'
WAIT = 3


def upload_data(elastic: ElasticSearchOperations):
    """
    This method uploads 1 document data into elasticsearch
    @return: uuid of upload document
    """
    uuid = str(uuid4())
    data = {'tool': 'benchmark-runner', 'uuid': uuid}
    elastic.upload_to_elasticsearch(index=TEST_INDEX_NAME, id=uuid, data=data)
    return uuid


def test_get_upload_update_elasticsearch():
    """
    This method tests get/upload/update elasticsearch
    @return:
    """
    if test_environment_variable['elasticsearch']:
        elastic = ElasticSearchOperations(es_host=test_environment_variable.get('elasticsearch', ''),
                                          es_port=test_environment_variable.get('elasticsearch_port', ''),
                                          es_user=test_environment_variable.get('elasticsearch_user', ''),
                                          es_password=test_environment_variable.get('elasticsearch_password', ''))
        uuid = upload_data(elastic=elastic)
        assert elastic.verify_elasticsearch_data_uploaded(index=TEST_INDEX_NAME, uuid=uuid)
        id = elastic.verify_elasticsearch_data_uploaded(index=TEST_INDEX_NAME, uuid=uuid)
        elastic.update_elasticsearch_index(index=TEST_INDEX_NAME, id=id[0], metadata={'ocp_version': '4.8.3'})
        result = elastic.get_elasticsearch_index_by_id(index=TEST_INDEX_NAME, id=id[0])
        assert result['_source']['uuid'] == uuid
        assert result['_source']['ocp_version'] == '4.8.3'
        elastic.delete_elasticsearch_index_by_id(index=TEST_INDEX_NAME, id=id[0])


def test_get_delete_ids_elasticsearch_last_day():
    """
    This method gets id in last day and delete it
    @return:
    """
    elastic = ElasticSearchOperations(es_host=test_environment_variable.get('elasticsearch', ''),
                                      es_port=test_environment_variable.get('elasticsearch_port', ''),
                                      es_user=test_environment_variable.get('elasticsearch_user', ''),
                                      es_password=test_environment_variable.get('elasticsearch_password', ''))
    # upload data
    uuid = upload_data(elastic=elastic)
    elastic.verify_elasticsearch_data_uploaded(index=TEST_INDEX_NAME, uuid=uuid)
    # verify data was uploaded to Elasticsearch
    current_timestamp = datetime.datetime.now()
    day_before_timestamp = current_timestamp - timedelta(days=1)
    assert len(elastic.get_index_ids_between_dates(index=TEST_INDEX_NAME, start_datetime=day_before_timestamp, end_datetime=current_timestamp)) >= 1
    # cleanup elastic
    elastic.delete_index_ids_between_dates(index=TEST_INDEX_NAME, start_datetime=day_before_timestamp, end_datetime=current_timestamp)
    time.sleep(WAIT)
    # verify data was deleted
    assert len(elastic.get_index_ids_between_dates(index=TEST_INDEX_NAME, start_datetime=day_before_timestamp, end_datetime=current_timestamp)) == 0


def test_get_all_indexes():
    """
    This method gets all indexes
    @return:
    """
    elastic = ElasticSearchOperations(es_host=test_environment_variable.get('elasticsearch', ''),
                                      es_port=test_environment_variable.get('elasticsearch_port', ''),
                                      es_user=test_environment_variable.get('elasticsearch_user', ''),
                                      es_password=test_environment_variable.get('elasticsearch_password', ''))
    assert len(elastic.get_all_indexes()) > 1
