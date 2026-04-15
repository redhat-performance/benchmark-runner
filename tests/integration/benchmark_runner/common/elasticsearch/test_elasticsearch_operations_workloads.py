
from uuid import uuid4

import pytest

from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from tests.integration.benchmark_runner.test_environment_variables import *

ES_TEST_INDEX = 'stressng-test-ci-results'


def test_verify_elasticsearch_data_uploaded_stressng_pod():
    """
    This method uploads stressng results to Elasticsearch and verifies the data was uploaded correctly.
    """
    if not test_environment_variable.get('elasticsearch'):
        pytest.skip('Elasticsearch not configured')

    test_uuid = str(uuid4())

    es = ElasticSearchOperations(
        es_host=test_environment_variable.get('elasticsearch', ''),
        es_port=test_environment_variable.get('elasticsearch_port', ''),
        es_user=test_environment_variable.get('elasticsearch_user', ''),
        es_password=test_environment_variable.get('elasticsearch_password', '')
    )

    try:
        data = {
            'uuid': test_uuid,
            'workload': 'stressng',
            'kind': 'pod',
            'run_status': 'complete',
            'cpu_bogomips': 1000,
            'vm_bogomips': 2000,
        }
        es.upload_to_elasticsearch(index=ES_TEST_INDEX, data=data)

        ids = es.verify_elasticsearch_data_uploaded(index=ES_TEST_INDEX, uuid=test_uuid)
        assert ids, f'Data with uuid={test_uuid} was not found in Elasticsearch'

        result = es.get_elasticsearch_index_by_id(index=ES_TEST_INDEX, id=ids[0])
        assert result['_source']['uuid'] == test_uuid
        assert result['_source']['workload'] == 'stressng'
        assert result['_source']['run_status'] == 'complete'

        es.delete_elasticsearch_index_by_id(index=ES_TEST_INDEX, id=ids[0])

    except ElasticSearchDataNotUploaded as err:
        raise err
