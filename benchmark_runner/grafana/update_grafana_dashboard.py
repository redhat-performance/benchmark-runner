
from benchmark_runner.common.grafana.grafana_operations import GrafanaOperations
from benchmark_runner.main.environment_variables import environment_variables

# Update grafana perf dashboard
environment_variables_dict = environment_variables.environment_variables_dict
grafana_operations = GrafanaOperations(grafana_url=environment_variables_dict.get('grafana_url', ''),
                                       grafana_api_key=environment_variables_dict.get('grafana_api_key', ''),
                                       grafana_json_path=environment_variables_dict.get('grafana_json_path', ''),
                                       grafana_folder_name=environment_variables_dict.get('grafana_folder_name', ''))
# for debug: grafana_operations.fetch_all_dashboards()
grafana_operations.read_dashboard_json()
grafana_operations.increment_dashboard_version()
grafana_operations.override_dashboard()
