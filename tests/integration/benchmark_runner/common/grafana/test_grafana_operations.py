
from benchmark_runner.common.grafana.grafana_operations import GrafanaOperations
from tests.integration.benchmark_runner.test_environment_variables import *


def test_fetch_all_dashboards():
    """
    This method fetched all grafana dashboards
    @return:
    """
    if test_environment_variable.get('grafana_url'):
        grafana_operations = GrafanaOperations(grafana_url=test_environment_variable.get('grafana_url', ''),
                                               grafana_api_key=test_environment_variable.get('grafana_api_key', ''),
                                               grafana_json_path=test_environment_variable.get('grafana_json_path', ''),
                                               grafana_folder_name=test_environment_variable.get('grafana_folder_name', ''))
        all_dashboards = grafana_operations.fetch_all_dashboards()
        assert all_dashboards
    else:
        raise Exception('incorrect grafana url')
