
import logging
import pandas as pd
from functools import reduce
from datetime import datetime
from typeguard import typechecked
from benchmark_runner.common.elasticsearch.elasticsearch_operations import ElasticSearchOperations

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummaryReportOperations:
    """ This class is filtering data, aggregate data per workload and calculate geometric mean per run"""
    GB = 1_000_000_000
    MILLISECONDS = 1000
    HAMMERDB_METRIC = 'TPM'
    UPERF_THROUGHPUT_METRIC = 'Throughput'
    UPERF_LATENCY_METRIC = 'Latency'
    VDBENCH_LATENCY_METRIC = 'Latency'
    VDBENCH_IOPS_METRIC = 'Iops'
    BOOTSTORM_FEDORA = 'fedora37'
    BOOTSTORM_WINDOWS = ['windows10', 'windows11', 'windows_server_2019', 'windows_server_2022']
    BOOTSTORM_FEDORA_METRIC = '240 VMs run time'
    BOOTSTORM_WINDOWS_METRIC = '111 VMs run time'

    def __init__(self, elasticsearch: ElasticSearchOperations):
        self.elasticsearch = elasticsearch
        self.geometric_mean_data = None
        self.geometric_mean_data_throughput = None
        self.geometric_mean_data_iops = None
        self.geometric_mean_data_latency = None
        self.bootstorm_df = None
        self.median_indices = None
        self.geometric_mean_df = None

    @typechecked
    def get_workload_data(self, start_datetime: datetime, end_datetime: datetime, index: str ='ci-status'):
        """
        @return: fetching workload data from elasticsearch
        """

        return self.elasticsearch.get_index_data_between_dates(index=index, start_datetime=start_datetime, end_datetime=end_datetime)

    @typechecked
    def filter_data(self, entries: list, compared_ocp_versions: tuple, kind: str, filter_field: dict = None):
        """
        This method filters elastic search data by filter fields
        @param entries:
        @param compared_ocp_versions:
        @param kind:
        @param filter_field:
        @return:
        """
        filter_data = [
            entry.get('_source') for entry in entries
            if (
                    entry.get('_source').get('ocp_version') in compared_ocp_versions and
                    entry.get('_source').get('kind') == kind and
                    (filter_field is None or entry.get('_source').get(
                        list(filter_field.keys())[0]) == list(filter_field.values())[0])
            )
        ]
        return pd.DataFrame(filter_data)

    @staticmethod
    def __geometric_mean(values: list):
        """
        This method calculates geometric means for input values
        @param values:
        @return: values geometric means
        """
        product = reduce(lambda x, y: x * y, values)
        mean = pow(product, 1 / len(values))
        return round(mean, 3)

    @staticmethod
    def __get_median(values: dict):
        """
        This method returns the median result
        @param values: all median values
        @return: return median result
        """
        median_result = (values['geometric_mean'] - values['geometric_mean'].median()).abs().idxmin()
        return pd.Series({'median_result': median_result})

    def __update_geometric_mean_data(self, subset: pd.DataFrame, unique_uuid: str):
        """
        This method updates geometric mean data
        @param subset: aggregate data by uuid - each uuid represent a run
        @param unique_uuid:
        @return:
        """
        self.geometric_mean_data['uuid'].append(unique_uuid)
        self.geometric_mean_data['ocp_version'].append(subset['ocp_version'].iloc[0])
        self.geometric_mean_data['cnv_version'].append(subset['cnv_version'].iloc[0])
        self.geometric_mean_data['odf_version'].append(subset['odf_version'].iloc[0])

    @typechecked()
    def update_hammerdb_data(self, subset: pd.DataFrame, unique_uuid: str):
        """
        This method updates hammerdb data
        @param subset: aggregate data by uuid - each uuid represent a run
        @param unique_uuid:
        @return:
        """
        logger.info(subset[['workload', 'db_type', 'ocp_version', 'current_worker', 'tpm']])
        geometric_mean_result = self.__geometric_mean(subset['tpm'].tolist())
        # Get uuid, ocp_version, cnv_version, odf_version, geometric_mean and append data to result DataFrame
        self.__update_geometric_mean_data(subset, unique_uuid)
        self.geometric_mean_data['geometric_mean'].append(geometric_mean_result)
        self.geometric_mean_data['db_type'].append(subset['db_type'].iloc[0])

    @typechecked()
    def update_uperf_data(self, subset: pd.DataFrame, unique_uuid: str):
        """
        This method updates uperf data
        @param subset: aggregate data by uuid - each uuid represent a run
        @param unique_uuid:
        @return:
        """
        logger.info(
            f"{subset[['workload', 'read_message_size', 'num_threads', 'test_type', 'ocp_version', 'norm_ltcy']]}")
        # Calculate latency and throughput
        average_latency_df = subset.groupby(
            ['uuid', 'ocp_version', 'cnv_version', 'odf_version', 'read_message_size', 'num_threads',
             'test_type'])['norm_ltcy'].mean().reset_index()
        average_latency_df = average_latency_df[average_latency_df['test_type'] == 'rr']
        average_throughput_df = subset.groupby(
            ['uuid', 'ocp_version', 'cnv_version', 'odf_version', 'read_message_size', 'num_threads',
             'test_type'])['norm_byte'].mean().reset_index()
        average_throughput_df = average_throughput_df[average_throughput_df['test_type'] == 'stream']
        average_throughput_df['norm_byte'] = (average_throughput_df['norm_byte'] * 8) / self.GB
        # logger.info(f"Displaying average_latency_df:\n{average_latency_df}")
        # logger.info(f"Displaying average_throughput_df:\n{average_throughput_df}")
        # Calculate geometric mean
        geo_mean_latency = self.__geometric_mean(average_latency_df['norm_ltcy'])
        geo_mean_throughput = self.__geometric_mean(average_throughput_df['norm_byte'])
        self.__update_geometric_mean_data(subset, unique_uuid)
        self.geometric_mean_data_throughput.update(self.geometric_mean_data)
        self.geometric_mean_data_throughput['geometric_mean'].append(geo_mean_throughput)
        self.geometric_mean_data_latency.update(self.geometric_mean_data)
        self.geometric_mean_data_latency['geometric_mean'].append(geo_mean_latency)

    @typechecked()
    def update_vdbench_data(self, subset: pd.DataFrame, unique_uuid: str):
        """
        This method updates vdbench data
        @param subset: aggregate data by uuid - each uuid represent a run
        @param unique_uuid:
        @return:
        """
        # Calculate iops and latency
        average_latency_df = \
            subset.groupby(['uuid', 'ocp_version', 'cnv_version', 'odf_version', 'Run', 'Threads'])[
                'Resp'].mean().reset_index()
        average_iops_df = \
            subset.groupby(['uuid', 'ocp_version', 'cnv_version', 'odf_version', 'Run', 'Threads'])[
                'Rate'].mean().reset_index()

        geo_mean_latency = self.__geometric_mean(average_latency_df['Resp'])
        geo_mean_iops = self.__geometric_mean(average_iops_df['Rate'])

        logger.info('geo_mean_latency', geo_mean_latency)
        logger.info('geo_mean_iops', geo_mean_iops)
        self.__update_geometric_mean_data(subset, unique_uuid)
        self.geometric_mean_data_iops.update(self.geometric_mean_data)
        self.geometric_mean_data_iops['geometric_mean'].append(geo_mean_iops)
        self.geometric_mean_data_latency.update(self.geometric_mean_data)
        self.geometric_mean_data_latency['geometric_mean'].append(geo_mean_latency)

    @typechecked()
    def update_bootstorm_data(self, subset: pd.DataFrame, unique_uuid: str):
        """
        This method updates bootstorm data
        @param subset: aggregate data by uuid - each uuid represent a run
        @param unique_uuid:
        @return:
        """
        # Calculate bootstorm total run time
        self.bootstorm_df = subset.groupby(['vm_os_version', 'uuid', 'ocp_version', 'cnv_version', 'odf_version'])['total_run_time'].mean().reset_index()
        logger.info('geometric_mean_df', self.geometric_mean_df)
        self.__update_geometric_mean_data(subset, unique_uuid)
        self.geometric_mean_data['geometric_mean'].append(self.bootstorm_df['total_run_time'].iloc[0])
        self.geometric_mean_data['metric'].append(self.bootstorm_df['vm_os_version'].iloc[0])

    @typechecked()
    def prepare_workload_dataframe(self, workload: str, df: pd.DataFrame):
        """
        This method prepares workload dataframe
        @param workload:
        @param df
        @return:
        """
        # Create a DataFrame to store results
        # Initialize common structure
        common_structure = {'uuid': [], 'ocp_version': [], 'cnv_version': [], 'odf_version': []}

        if workload in ['hammerdb', 'hammerdb_lso']:
            self.geometric_mean_data = {'workload': workload, **common_structure, 'db_type': [], 'geometric_mean': []}
        elif workload == 'uperf':
            # Filter out values greater than 1000
            df = df[(df['norm_ltcy'] < 1000) & df['norm_ltcy'].notna()]
            self.geometric_mean_data = {**common_structure}
            self.geometric_mean_data_latency = {'workload': workload, **common_structure, 'metric': self.UPERF_LATENCY_METRIC,
                                                'geometric_mean': []}
            self.geometric_mean_data_throughput = {'workload': workload, **common_structure, 'metric': self.UPERF_THROUGHPUT_METRIC,
                                                   'geometric_mean': []}
        elif workload in ['vdbench', 'vdbench_scale']:
            df = df[df['Run'] != 'fillup']
            self.geometric_mean_data = {**common_structure}
            self.geometric_mean_data_iops = {'workload': workload, **common_structure, 'metric': self.VDBENCH_IOPS_METRIC,
                                             'geometric_mean': []}
            self.geometric_mean_data_latency = {'workload': workload, **common_structure, 'metric': self.VDBENCH_LATENCY_METRIC,
                                                'geometric_mean': []}
        elif workload in ['bootstorm', 'windows']:
            self.geometric_mean_data = {'workload': workload, **common_structure, 'metric': [], 'geometric_mean': []}

        return df

    @staticmethod
    def __calc_percentage(df: pd.DataFrame, complementary: bool = False):
        """
        This method calculates percentage difference
        @param df:
        @param complementary: calculates the complementary percentage change, meaning it measures the difference from 100%
        @return:
        """
        # complementary percentage change: e.g. latency
        if complementary:
            df['result'] = df.groupby('metric')['geometric_mean'].transform(lambda x: 1 - ((x - x.shift(1)) / x.shift(1)) * 100)
        else:
            df['result'] = df.groupby('metric')['geometric_mean'].transform(lambda x: ((x - x.shift(1)) / x.shift(1)) * 100)
        df = df.dropna(subset=['result'])
        df.loc[:, 'result'] = df['result'].round(2)
        return df[['workload', 'metric', 'result']]

    def __calc_workload_precentage_diff(self, workload: str, geometric_mean_data: dict, complementary: bool = False, metric: str = None):
        """
        This method calculates the percentage difference for workload dictionary and retrieving_operator_versions pre workload
        @workload:
        @geometric_mean_data: workload data including geometric_mean_data
        @complementary: how to calc the percentage
        @metric: which metric value to retrieve operator versions
        @return:
        """
        geometric_mean_df = pd.DataFrame(geometric_mean_data)
        self.median_indices = geometric_mean_df.groupby(['metric', 'ocp_version']).apply(self.__get_median)
        geometric_mean_df = geometric_mean_df.loc[self.median_indices['median_result']]
        return self.__calc_percentage(geometric_mean_df, complementary)

    def aggregate_hammerdb_dataframe(self, workload):
        """
        This method aggregates hammerdb dataframe and update metric names
        @return:
        """
        # rename db_type to metric to get same columns as other workloads
        self.geometric_mean_data['metric'] = self.geometric_mean_data.pop('db_type')
        self.geometric_mean_df = self.__calc_workload_precentage_diff(workload, self.geometric_mean_data, metric='pg')
        # updates metric names
        replace_dict = {'mariadb': f'{self.HAMMERDB_METRIC} (mariadb)', 'mssql': f'{self.HAMMERDB_METRIC} (mssql)', 'pg': f'{self.HAMMERDB_METRIC} (postgresql)'}
        self.geometric_mean_df['metric'] = self.geometric_mean_df['metric'].replace(replace_dict)

    def aggregate_uperf_dataframe(self, workload):
        """
        This method aggregates uperf dataframe and update metric names
        @return:
        """
        geometric_mean_df_throughput = self.__calc_workload_precentage_diff(workload, self.geometric_mean_data_throughput)
        geometric_mean_df_latency = self.__calc_workload_precentage_diff(workload, self.geometric_mean_data_latency, complementary=True)

        # Concatenate DataFrames along rows (assuming the keys are the same)
        self.geometric_mean_df = pd.concat([geometric_mean_df_throughput, geometric_mean_df_latency], ignore_index=True)

    def aggregate_vdbench_dataframe(self, workload):
        """
        This method aggregates vdbench dataframe and update metric names
        @return:
        """
        geometric_mean_df_iops = self.__calc_workload_precentage_diff(workload, self.geometric_mean_data_iops)
        geometric_mean_df_latency = self.__calc_workload_precentage_diff(workload, self.geometric_mean_data_latency, complementary=True)

        # Concatenate DataFrames along rows (assuming the keys are the same)
        self.geometric_mean_df = pd.concat([geometric_mean_df_iops, geometric_mean_df_latency], ignore_index=True)

    def aggregate_bootstorm_dataframe(self, workload: str):
        """
        This method aggregates bootstorm dataframe and update metric names
        @return:
        """
        self.geometric_mean_df = self.__calc_workload_precentage_diff(workload, self.geometric_mean_data, complementary=True, metric='windows_server_2019')
        # updates metric names
        if workload == 'windows':
            for os in self.BOOTSTORM_WINDOWS:
                self.geometric_mean_df['metric'] = self.geometric_mean_df['metric'].replace({os: f'{self.BOOTSTORM_WINDOWS_METRIC} ({os})'})
        else:
            self.geometric_mean_df['metric'] = self.geometric_mean_df['metric'].replace({f'{self.BOOTSTORM_FEDORA}': f'{self.BOOTSTORM_FEDORA_METRIC} ({self.BOOTSTORM_FEDORA})'})

    @typechecked()
    def aggregate_workload_dataframe(self, workload: str):
        """
        This method aggregates workload dataframe and updates metric values
        @param workload:
        @return:
        """
        if workload in ['hammerdb', 'hammerdb_lso']:
            self.aggregate_hammerdb_dataframe(workload)
        elif workload == 'uperf':
            self.aggregate_uperf_dataframe(workload)
        elif workload in ['vdbench', 'vdbench_scale']:
            self.aggregate_vdbench_dataframe(workload)
        elif workload in ['bootstorm', 'windows']:
            self.aggregate_bootstorm_dataframe(workload)

    @typechecked()
    def calc_median_geometric_mean_df(self, workload: str, df: pd.DataFrame):
        """
        This method calculates the geometric mean per workload from input dataframe
        @param workload:
        @param df:
        @return:
        """

        logger.info('Wait till fetch and analyzing data ...')
        # Convert lists to strings in the 'uuid' column
        df['uuid'] = df['uuid'].apply(
            lambda x: x[0] if isinstance(x, list) and x else x)

        df = self.prepare_workload_dataframe(workload, df)

        # Factorize the 'uuid' column
        labels, uniques = pd.factorize(df['uuid'])

        # Check if labels cover all rows
        if len(labels) != len(df):
            raise ValueError("Factorization did not cover all rows.")

        # Calculate geometric mean for each unique 'uuid'
        for label, unique_uuid in enumerate(uniques):
            # logger.info(f"For each UUID {unique_uuid}:")
            subset = df[labels == label]
            if workload in ['hammerdb', 'hammerdb_lso']:
                # Skip empty columns and skip NaN tpm values
                if not subset.empty and subset['tpm'].notna().all():
                    self.update_hammerdb_data(subset, unique_uuid)
            elif workload == 'uperf':
                if not subset.empty and subset['norm_ltcy'].notna().all() and subset['norm_byte'].notna().all():
                    self.update_uperf_data(subset, unique_uuid)
            elif workload in ['vdbench', 'vdbench_scale']:
                if not subset.empty and subset['Rate'].notna().all() and subset['Resp'].notna().all():
                    self.update_vdbench_data(subset, unique_uuid)
            elif workload in ['bootstorm', 'windows']:
                if not subset.empty and subset['total_run_time'].notna().all():
                    self.update_bootstorm_data(subset, unique_uuid)

        self.aggregate_workload_dataframe(workload)
        return self.geometric_mean_df

    @typechecked()
    def extract_comparison_details(self, df: pd.DataFrame):
        """
        This method returns comparison details ocp_version, odf_version, cnv_nightly_version, sample_dates and uuid
        @return:
        """
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        aggregated_df = df.groupby('date').agg({
            'ocp_version': 'first',
            'odf_version': 'first',
            'cnv_version': 'first',
            'uuid': 'first'
        }).reset_index()

        aggregated_df = aggregated_df[['date', 'ocp_version', 'odf_version', 'cnv_version', 'uuid']]
        # Group by 'ocp_version' and aggregate every column with distinct values
        grouped_df = aggregated_df.groupby('ocp_version', as_index=False).agg(lambda x: list(set(x.explode())))

        grouped_df = grouped_df.rename(columns={'cnv_version': 'cnv_nightly_version'})
        grouped_df = grouped_df.rename(columns={'date': 'sample_dates'})

        return grouped_df[['ocp_version', 'odf_version', 'cnv_nightly_version', 'sample_dates', 'uuid']]
