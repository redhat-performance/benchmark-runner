
import json
from datetime import datetime, timedelta

from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations


class UpdateGrafanaLatestValueMappings:
    """
    This class updates grafana dashboard with last value mappings from ElasticSearch
    """
    # Prevent error messages from being saved instead of versions in case of a connection issue
    MAX_VERSION_LEN = 20
    LAST_ES_FETCH_DAYS = 30

    def __init__(self, main_libsonnet_path: str):
        # Stamp start/ end value mapping for extract value mapping
        self.start_value_mapping = "//START_VALUE_MAPPING_227"
        self.end_value_mapping = "//END_VALUE_MAPPING_227"
        self._environment_variables_dict = environment_variables.environment_variables_dict
        self.elasticsearch = ElasticSearchOperations(es_host=self._environment_variables_dict.get('elasticsearch', ''),
                                                     es_port=self._environment_variables_dict.get('elasticsearch_port', ''),
                                                     es_user=self._environment_variables_dict.get('elasticsearch_user', ''),
                                                     es_password=self._environment_variables_dict.get('elasticsearch_password', ''))
        self.main_libsonnet_path = main_libsonnet_path
        self.value_mappings = self.get_value_mappings()

    @staticmethod
    def _normalize_version_for_grafana(version: str) -> str:
        """
        Normalizes a version string for Grafana, then strips all non-digit characters.

        Examples:
            '4.14.0-ec.2' -> '414002'
            '4.15.0-rc.3' -> '415013'
            '4.15.5' -> '4155'

        Returns:
            A normalized numeric string, replacing '-ec.' with '0' and '-rc.' with '1' if present;
            otherwise returns the version string with all non-digit characters removed.
        """
        qualifiers = {'-ec.': '0', '-rc.': '1'}
        for qualifier, replacement in qualifiers.items():
            if qualifier in version:
                replaced = version.replace(qualifier, replacement)
                digits_only = ''.join(c for c in replaced if c.isdigit())
                return digits_only

        # No qualifier found; return only digits from the original version
        return ''.join(c for c in version if c.isdigit())

    def get_last_elasticsearch_versions(self, last_es_fetch_days=LAST_ES_FETCH_DAYS):
        """
        This method fetches new versions from ElasticSearch
        :param last_es_fetch_days: default fetch 30 days
        :return:
        """
        new_versions = {}
        current_datetime = datetime.now()
        start_datetime = current_datetime - timedelta(days=last_es_fetch_days)

        ids = self.elasticsearch.get_index_ids_between_dates(index='ci-status', start_datetime=start_datetime,
                                                             end_datetime=current_datetime)

        display_versions = ['ocp_version', 'cnv_version', 'kata_version', 'kata_rpm_version', 'odf_version']
        for id in ids:
            data = self.elasticsearch.get_elasticsearch_index_by_id(index='ci-status', id=id)
            for resource, version in data['_source'].items():
                if resource in display_versions and version not in new_versions.values() and len(version) < self.MAX_VERSION_LEN:
                    # Normalize version for Grafana panel if it contains non-digit characters
                    normalized = self._normalize_version_for_grafana(version)
                    new_versions[normalized] = version

        return new_versions

    def get_value_mappings(self):
        """
        This method gets value mappings from main.libsonnet
        :return:
        """
        # Initialize a flag to indicate whether the lines are within the desired range
        within_range = False
        mapping_lines = []

        # Read the content of the file and store lines between start and end patterns in a list
        with open(self.main_libsonnet_path, 'r') as file:
            for line in file:
                if self.start_value_mapping in line.strip():
                    within_range = True
                    continue  # Skip storing the start line
                elif self.end_value_mapping in line.strip():
                    within_range = False
                    continue  # Skip storing the end line
                if within_range:
                    mapping_lines.append(line.strip())

        # Join the lines to create the final string
        content_string = ''.join(mapping_lines)

        # Convert the string into a dictionary using json.loads()
        return json.loads(content_string)

    def update_value_mappings_last_versions(self, last_versions: dict):
        """
        This method updated value mapping with last versions
        :param last_versions:
        :return:
        """
        # Sort the dictionary by "index" values and convert it to a list of tuples
        sorted_mapping = sorted(self.value_mappings.items(), key=lambda x: x[1]['index'])
        # Get the maximum index value and the corresponding key
        max_index, max_key = sorted_mapping[-1][1]['index'], sorted_mapping[-1][0]

        num = 1
        for version_key, version in last_versions.items():
            if not self.value_mappings.get(version_key) or self.value_mappings[version_key]['text'] != version:
                # Normalize version for Grafana panel
                normalized = self._normalize_version_for_grafana(version)
                self.value_mappings[normalized] = {"index": int(max_index) + num, "text": version}
                num += 1

    def update_main_libsonnet(self):
        """
        This method updated last versions in main.libsonnet
        :return:
        """
        # Read the content of the file and store it in a list
        with open(self.main_libsonnet_path, 'r') as file:
            lines = file.readlines()
        # Find the indices of the lines between start and end
        start_index = None
        end_index = None
        for i, line in enumerate(lines):
            if self.start_value_mapping in line:
                start_index = i
            elif self.end_value_mapping in line:
                end_index = i

        # Replace the lines between start and end with the dictionary
        if start_index is not None and end_index is not None:
            lines[start_index + 1:end_index] = [f'\t\t\t\t {json.dumps(self.value_mappings, indent=None)} \n']

        # Write the modified content back to the file
        with open(self.main_libsonnet_path, 'w') as file:
            file.writelines(lines)
