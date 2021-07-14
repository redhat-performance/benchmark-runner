
import pandas as pd


class AnalyzeData:
    """
    This class analyzing input data using pandas
    """
    def __init__(self, input_data_path):
        self.__input_data_path = input_data_path
        self._runs_list = []

    def analyze_vdbench_csv_data(self):
        """
        This method read input vdbench CSV data into pandas dataframe
        :return: list of dataframes, first one is the average results
        """
        run_dict = {}
        run_metrics_dict = {}
        df = pd.read_csv(self.__input_data_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%Y-%H:%M:%S-PDT')
        df.rename(columns={"timestamp": "time"})
        df_groupbyrun = df.groupby(df.columns[2]).mean()
        # df filter out all run that start with the letter 'f'
        df_run_avg = df_groupbyrun[~df_groupbyrun.index.str.startswith('f')]
        self._runs_list = df_run_avg.index.to_list()
        df_run_avg = df_run_avg.round(2)
        df_run_avg = df_run_avg.fillna(0)
        avg_run_dict = df_run_avg.to_dict(orient='index')

        # create run df dict by selected run name
        for run_name in self._runs_list:
            df_run = df[df.iloc[:, 2] == run_name].round(2)
            df_run = df_run.fillna(0)
            run_dict[run_name] = df_run.to_dict()

        # filter highlight metrics
        for run in self._runs_list:
            run_metrics_dict[run + '_cpu_used'] = run_dict[run]['cpu_used']

        return avg_run_dict, run_metrics_dict

    @property
    def runs_list(self):
        """
        This method return runs list
        :return:
        """
        return self._runs_list
