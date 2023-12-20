
import pandas as pd
from datetime import datetime, timedelta
import ipywidgets as widgets
from IPython.display import display, HTML
from typeguard import typechecked

from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations
from benchmark_runner.jupyterlab.templates.summary_report.summary_report_operations import SummaryReportOperations


class SummaryReportWidgets:
    """ This class is analyzing workload data and visualization """

    FILTER_KIND = 'vm'
    FETCH_OCP_VERSIONS_DAYS = 365
    DEFAULT_END_DATE = datetime.combine(datetime.now().date(), datetime.min.time())
    DEFAULT_START_DATE = datetime.combine(DEFAULT_END_DATE - timedelta(days=FETCH_OCP_VERSIONS_DAYS),
                                          datetime.min.time())

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
        ocp_versions_list = sorted(list(distinct_ocp_versions), reverse=True)
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
    def analyze_workload(self, workload: str):
        """
        This method analyzes workload metrics between different OpenShift versions
        @return:
        """
        # Get workload filtered data
        if workload == 'hammerdb':
            filtered_df = self.get_workload_filtered_data(workload=workload, filter_field={'storage_type': 'odf'})
        elif workload == 'vdbench':
            filtered_df = self.get_workload_filtered_data(workload=workload, filter_field={'scale': None})
        elif workload == 'vdbench_scale':
            # 'vdbench' index
            filtered_df = self.get_workload_filtered_data(workload='vdbench', filter_field={'scale': 6})
        # uperf, bootstorm
        else:
            filtered_df = self.get_workload_filtered_data(workload=workload)
        median_geometric_mean_df = self.calc_median_geometric_mean_df(workload, filtered_df)
        median_geometric_mean_df.rename(columns={'result': self.get_two_last_major_versions()}, inplace=True)

        return median_geometric_mean_df

    def analyze_all_workload(self, workloads: list = ['hammerdb', 'uperf', 'vdbench', 'vdbench_scale', 'bootstorm', 'windows']):
        """
        This method analyzes all the workloads
        @param workloads:
        @return:
        """
        result_df = None
        for workload in workloads:
            median_geometric_mean_df = self.analyze_workload(workload=workload)
            result_df = pd.concat([result_df, median_geometric_mean_df], ignore_index=True)
        return result_df

    @staticmethod
    def color_negative_red(val):
        """
        This method defines a function for coloring negative values red and positive values green
        @param val:
        @return:
        """
        if pd.notna(val) and isinstance(val, (int, float)):
            color = 'red' if val < 0 else 'green'
            return f'color: {color}; text-align: center;'
        else:
            return ''  # Handle NaN values or non-numeric values

    def display_df(self, df: pd.DataFrame):
        """
        This method displays a style df with a colors: red/green to positive/negative results
        @return:
        """
        # Convert the last column to numeric values (including handling non-numeric values)
        last_column_name = df.columns[-1]
        df[last_column_name] = pd.to_numeric(df[last_column_name], errors='coerce')

        grafana_url = "http://cloud-governance-stage.rdu2.scalelab.redhat.com:3000/"
        df['Grafana URL [VPN ON]'] = f'<a href="{grafana_url}" target="_blank">{grafana_url}</a>'

        # align all values to the left
        styled_df = df.style.set_table_styles([
            {'selector': 'th:not(:last-child)', 'props': [('text-align', 'left')]},
            {'selector': 'td:not(:last-child)', 'props': [('text-align', 'left')]}
        ])
        # add % to last column values
        styled_df = styled_df.format({last_column_name: "{}%"})
        # add color to positive/negative
        styled_df = styled_df.map(self.color_negative_red)
        # HTML code to style the text
        html_code = '<div style="color: blue; font-weight: bold;">OCP Comparison results:</div>'

        # Display the HTML code
        display(HTML(html_code))
        display(HTML(styled_df._repr_html_()))

    def get_operators_versions(self):
        """
        This method returns operator versions
        @return:
        """
        # HTML code to style the text
        html_code = '<div style="color: blue; font-weight: bold;">Operators versions:</div>'

        # Display the HTML code
        display(HTML(html_code))
        return self.summary_report.get_operator_versions()
