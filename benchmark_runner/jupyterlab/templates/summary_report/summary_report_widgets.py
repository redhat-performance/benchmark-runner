
import os
import re
import logging
import pandas as pd
from datetime import datetime, timedelta, timezone
import ipywidgets as widgets
from IPython.display import display, HTML
from typeguard import typechecked

from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.jupyterlab.templates.summary_report.summary_report_operations import SummaryReportOperations

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummaryReportWidgets:
    """ This class is analyzing workload data and visualization """

    NETWORK_SPEED = os.getenv('network_speed')
    GRAFANA_URL = os.getenv('grafana_url')
    FETCH_OCP_VERSIONS_DAYS = int(os.getenv('fetch_ocp_versions_days'))
    FILTER_KIND = os.getenv('filter_kind')
    # take 1 day extra for end time
    DEFAULT_END_DATE = datetime.combine(datetime.now().date(), datetime.max.time())
    DEFAULT_START_DATE = datetime.combine(DEFAULT_END_DATE - timedelta(days=FETCH_OCP_VERSIONS_DAYS),
                                          datetime.min.time())
    STORAGE_TYPES = {'hammerdb': 'ODF', 'hammerdb_lso': 'LSO', 'uperf': 'Ephemeral', 'vdbench': 'ODF', 'vdbench_scale': 'ODF', 'bootstorm': 'Ephemeral', 'windows': 'ODF (virtio)'}
    compared_ocp_versions = None

    def __init__(self, elasticsearch: ElasticSearchOperations):
        self.elasticsearch = elasticsearch
        self.summary_report = SummaryReportOperations(self.elasticsearch)

    @typechecked()
    def set_fetch_ocp_version_days(self, num_fetch_days: int = FETCH_OCP_VERSIONS_DAYS):
        """
        This method updates the number of fetch days, also updates DEFAULT_START_DATE
        @param num_fetch_days:
        @return:
        """
        self.FETCH_OCP_VERSIONS_DAYS = num_fetch_days
        self.DEFAULT_START_DATE = datetime.combine(self.DEFAULT_END_DATE - timedelta(days=self.FETCH_OCP_VERSIONS_DAYS),
                                              datetime.min.time())

    @staticmethod
    def get_compared_ocp_versions():
        """
        This method returns changed global compared_ocp_versions
        @return:
        """
        try:
            return compared_ocp_versions[::-1]
        except NameError:
            # Handle the case when compared_ocp_versions is not defined
            return None

    def version_key(self, version):
        """
        This method splits the version string into parts and returns a tuple for proper comparison
        @param version:
        @return:
        """
        # 1. Split into base version and suffix
        # Example: '4.21.0-rc.2' -> base='4.21.0', suffix='rc.2'
        if '-' in version:
            base, suffix = version.split('-', 1)
        else:
            base, suffix = version, 'ga'  # GA (General Availability) is the highest

        # 2. Assign weights to suffixes (higher is newer)
        suffix_weights = {'ga': 3, 'rc': 2, 'ec': 1}

        # Determine weight and build number
        weight = 0
        build_num = 0
        for s_type, s_weight in suffix_weights.items():
            if s_type in suffix:
                weight = s_weight
                # Extract build number (e.g., '2' from 'rc.2')
                match = re.search(r'\d+', suffix)
                build_num = int(match.group()) if match else 0
                break

        # 3. Convert base version to integers
        numeric_parts = [int(p) for p in base.split('.')]

        # 4. Return a tuple for proper comparison: (4, 21, 0, weight, build_num)
        return (*numeric_parts, weight, build_num)

    def get_ocp_distinct_list(self):
        """
        This method returns distinct list
        @return:
        """
        entries = self.elasticsearch.get_index_data_between_dates(index=f'ci-status',
                                                                  start_datetime=self.DEFAULT_START_DATE,
                                                                  end_datetime=self.DEFAULT_END_DATE)
        ocp_versions_list = [entry.get('_source').get('ocp_version') for entry in entries if
                             entry.get('_source').get('ocp_version') not in [None, 0]]
        distinct_ocp_versions = set(ocp_versions_list)
        ocp_versions_list = sorted(list(distinct_ocp_versions), key=self.version_key, reverse=True)
        return ocp_versions_list

    def get_two_last_major_versions(self):
        """
        This method returns last two major versions
        """
        versions = self.get_ocp_distinct_list()
        # Find the latest version
        latest_version = versions[0]

        # Calculate the version_before
        version_before = f"{latest_version.split('.')[0]}.{str(int(latest_version.split('.')[1]) - 1)}"

        # Filter versions that start with version_before
        matching_versions = [version for version in versions if version.startswith(version_before)]

        # Find the maximum minor version among the matching versions
        max_minor_version = max(
            [int(''.join(filter(str.isdigit, version.split('.')[2]))) for version in matching_versions],
            default=None
        )
        latest_version_before = f"{version_before}.{max_minor_version}" if max_minor_version is not None else version_before
        if self.get_compared_ocp_versions():
            return self.get_compared_ocp_versions()
        else:
            return (latest_version_before, latest_version)

    def choose_ocp_versions(self):
        """
        This method returns ocp versions widget
        @return:
        """

        # Create a prompt and a list widget
        ocp_version_widget = widgets.SelectMultiple(
            options=self.get_ocp_distinct_list(),
            disabled=False,
            layout=widgets.Layout(height='300px')  # Adjust the height here
        )

        # Initialize the compared_ocp_versions list
        initial_compared_ocp_versions = []
        # Set the default selected values in the widget
        ocp_version_widget.value = self.get_two_last_major_versions()
        compared_ocp_versions = self.get_two_last_major_versions()
        # Display the prompt and the widget
        display(ocp_version_widget)

        # Function to get selected values and update compared_ocp_versions
        def get_selected_versions(change):
            selected_versions = ocp_version_widget.value
            global compared_ocp_versions
            compared_ocp_versions = selected_versions

        # Attach the function to the widget's change event
        ocp_version_widget.observe(get_selected_versions, names='value')

    def get_workload_filtered_data(self, workload: str, filter_field: dict = None):
        """
        This method gets workload filtered data
        Located in this class for get_compared_ocp_versions
        @return:
        """
        entries = self.summary_report.get_workload_data(index=f'{workload}-results', start_datetime=self.DEFAULT_START_DATE,
                                                             end_datetime=self.DEFAULT_END_DATE)
        filter_df = self.summary_report.filter_data(entries=entries,
                                                    compared_ocp_versions=self.get_two_last_major_versions(),
                                                    kind=self.FILTER_KIND,
                                                    filter_field=filter_field)
        return filter_df

    def calc_median_geometric_mean_df(self, workload: str, filter_df: pd.DataFrame):
        """
        This method calculates median geometric mean
        @param workload:
        @param filter_df:
        @return:
        """
        return self.summary_report.calc_median_geometric_mean_df(workload=workload, df=filter_df)

    @typechecked
    def get_filtered_df(self, workload: str):
        """
        This method returns filtered dataframe between different OpenShift versions
        @return:
        """
        # Get workload filtered data
        if workload == 'hammerdb':
            filtered_df = self.get_workload_filtered_data(workload=workload, filter_field={'storage_type': 'odf'})
        elif workload == 'hammerdb_lso':
            filtered_df = self.get_workload_filtered_data(workload='hammerdb', filter_field={'storage_type': 'lso'})
        elif workload == 'vdbench':
            filtered_df = self.get_workload_filtered_data(workload=workload, filter_field={'scale': None})
        elif workload == 'vdbench_scale':
            # 'vdbench' index
            filtered_df = self.get_workload_filtered_data(workload='vdbench', filter_field={'scale': 6})
        # uperf, bootstorm
        else:
            filtered_df = self.get_workload_filtered_data(workload=workload)
        return filtered_df

    @typechecked
    def analyze_workload(self, workload: str):
        """
        This method analyzes workload metrics between different OpenShift versions
        @return:
        """
        median_geometric_mean_df = self.calc_median_geometric_mean_df(workload, self.get_filtered_df(workload))
        v1, v2 = self.get_two_last_major_versions()
        median_geometric_mean_df.rename(columns={'previous_val': v1, 'geometric_mean': v2, 'result': self.get_two_last_major_versions()}, inplace=True)
        return median_geometric_mean_df

    def analyze_all_workload(self, workloads: list = ['hammerdb', 'hammerdb_lso', 'uperf', 'vdbench', 'vdbench_scale', 'bootstorm', 'windows']):
        """
        This method analyzes all the workloads
        @param workloads:
        @return:
        """
        result_df = None
        for workload in workloads:
            median_geometric_mean_df = self.analyze_workload(workload=workload)

            # Add column types before comparison result
            median_geometric_mean_df.insert(len(median_geometric_mean_df.columns) - 1, 'storage type',
                                            median_geometric_mean_df['workload'].map(self.STORAGE_TYPES))

            result_df = pd.concat([result_df, median_geometric_mean_df], ignore_index=True)
        # change workloads names
        result_df.loc[result_df['workload'] == 'hammerdb_lso', 'workload'] = 'hammerdb'
        result_df.loc[result_df['workload'] == 'windows', 'workload'] = 'bootstorm'

        # Reorder columns to put vm_os_version after metric
        cols = list(result_df.columns)
        if 'vm_os_version' in cols:
            cols.insert(cols.index('metric') + 1, cols.pop(cols.index('vm_os_version')))
            result_df = result_df[cols]

        return result_df

    @staticmethod
    def color_percentage_values(val):
        """
        This method defines a function for coloring percentage values
        @param val:
        @return:
        """
        if pd.notna(val) and isinstance(val, (int, float)):
            if val < -50:
                color = 'red'
            elif val < -10:
                color = 'orange'
            elif val < 0:
                color = 'black'
            else:
                color = 'green'

            return f'color: {color}; text-align: center;'
        else:
            return ''  # Handle NaN values or non-numeric values

    def display_df(self, df: pd.DataFrame):
        """
        This method displays a style df with a colors: red/green to positive/negative results
        @return:
        """
        # Identify the OCP version columns to hide
        versions_to_hide = list(self.get_two_last_major_versions())

        # Convert the last column to numeric values (including handling non-numeric values)
        last_column_name = df.columns[-1]
        df[last_column_name] = pd.to_numeric(df[last_column_name], errors='coerce')

        # align all values to the left and hide the version columns
        styled_df = df.style.hide(versions_to_hide, axis='columns').set_table_styles([
            {'selector': 'th:not(:last-child)', 'props': [('text-align', 'left')]},
            {'selector': 'td:not(:last-child)', 'props': [('text-align', 'left')]}
        ])
        # add % to last column values
        styled_df = styled_df.format({last_column_name: "{}%"})
        # add color to positive/negative
        styled_df = styled_df.map(self.color_percentage_values)
        # html
        network_speed = f'<div><span style="color: black; font-weight: bold;"> Network Speed: </span><span style="color: blue;">{self.NETWORK_SPEED}</span></div>'
        grafana_url = f'<div><span style="color: black; font-weight: bold;">** For more details Grafana url:</span> <a href="{self.GRAFANA_URL}" style="color: blue;" target="_blank">{self.GRAFANA_URL}</a></div>'
        # Display the HTML
        display(HTML(styled_df._repr_html_()))
        display(HTML(network_speed))
        display(HTML(grafana_url))

    def get_comparison_details(self):
        """
        This method returns comparison details versions, dates, uuid
        @return:
        """
        details_df = self.summary_report.extract_comparison_details(self.get_filtered_df(workload='hammerdb'))

        # Set display options to show all values without truncation
        pd.set_option('display.max_colwidth', None)

        # Use HTML and CSS to style the DataFrame for left alignment
        style_html = """
        <style>
        th, td {
            text-align: left !important;
        }
        </style>
        """

        # Display the HTML-styled DataFrame
        display(HTML(style_html + details_df.to_html(index=False)))

    def upload_report_to_elasticsearch(self, df: pd.DataFrame, index_name: str = "summary-report"):
        """
        This method uploads the summary report to Elasticsearch.
        It uses a unique ID per metric/version to ensure that re-running the report
        for the same OCP version overrides the previous data.
        """
        # 1. Get the latest version from the comparison
        _, latest_v = self.get_two_last_major_versions()

        # 2. Convert DataFrame to records
        records = df.to_dict(orient='records')

        for record in records:
            # 3. Create a stable Metric ID (independent of version, but includes OS)
            # Example: "hammerdb_tpm_mssql_centos-stream9_odf"
            clean_metric = str(record['metric']).lower().replace(" ", "_").replace("(", "").replace(")", "")
            vm_os = str(record.get('vm_os_version', '')).lower().replace(" ", "_")
            metric_id = f"{record['workload']}_{clean_metric}_{vm_os}_{str(record['storage type']).lower()}"

            # 4. Create a unique Document ID (specific to this version run)
            # Example: "4.21.0-rc.2_hammerdb_tpm_mssql_centos-stream9_odf"
            doc_id = f"{latest_v}_{metric_id}"

            # 5. Prepare the AI-friendly document
            upload_data = {
                "ocp_version": latest_v,
                "metric_id": metric_id,  # Perfect for fast comparison queries
                "workload": record['workload'],
                "metric": record['metric'],
                "vm_os_version": record.get('vm_os_version'),
                "storage_type": record['storage type'],
                "value": record[latest_v],
                "diff_pct": record.get('Diff %', 0),
                "status": "improvement" if record.get('Diff %', 0) > 0 else "degradation" if record.get('Diff %', 0) < 0 else "stable",
                "timestamp": datetime.now(timezone.utc)
            }

            # 6. Upload with the unique ID to ensure OVERRIDE
            try:
                self.elasticsearch.upload_to_elasticsearch(
                    index=index_name,
                    data=upload_data,
                    id=doc_id
                )
                logger.info(f"Successfully synced {record['workload']} to {index_name} for version {latest_v}")
            except Exception as e:
                logger.error(f"Failed to upload {doc_id} to {index_name}: {e}")
