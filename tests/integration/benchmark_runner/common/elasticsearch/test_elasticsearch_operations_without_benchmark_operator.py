
# Tests that are not required benchmark-operator pod
from uuid import uuid4

from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from tests.integration.benchmark_runner.test_environment_variables import *


def test_get_upload_update_elasticsearch():
    """
    This method test get upload and update elasticsearch
    @return:
    """
    if test_environment_variable['elasticsearch']:
        uuid = str(uuid4())
        # verify that data upload to elastic search
        es = ElasticSearchOperations(es_host=test_environment_variable.get('elasticsearch', ''), es_port=test_environment_variable.get('elasticsearch_port', ''), es_user=test_environment_variable.get('elasticsearch_user', ''), es_password=test_environment_variable.get('elasticsearch_password', ''))
        data = {'tool': 'benchmark-runner', 'uuid': uuid}
        es.upload_to_elasticsearch(index='benchmark-runner-test', data=data)
        assert es.verify_elasticsearch_data_uploaded(index='benchmark-runner-test', uuid=uuid)
        id = es.verify_elasticsearch_data_uploaded(index='benchmark-runner-test', uuid=uuid)
        es.update_elasticsearch_index(index='benchmark-runner-test', id=id[0], metadata={'ocp_version': '4.8.3'})
        result = es.get_elasticsearch_index_by_id(index='benchmark-runner-test', id=id[0])
        assert result['_source']['uuid'] == uuid
        assert result['_source']['ocp_version'] == '4.8.3'
