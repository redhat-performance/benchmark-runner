
import os
import pandas as pd
from typeguard import typechecked

# display bokeh
from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file
from bokeh.models import HoverTool, Label, ColumnDataSource, LabelSet, Circle, NumeralTickFormatter


from benchmark_runner.jupyterlab.templates.logs_operations.logs_operations import LogsOperations
from benchmark_runner.jupyterlab.templates.analyze_workloads.visualize_workload_operations import VisualizeWorkloadOperations


class AnalyzeUperfLogs(VisualizeWorkloadOperations):
    """
    This class analyzes Uperf logs
    """

    def __init__(self, s3_logs_url: str):
        super().__init__()
        self.__workload = 'uperf'
        self.s3_logs_url = s3_logs_url
        self.__logs_operations = LogsOperations(s3_logs_url=self.s3_logs_url)

    def get_uperf_log_file(self):
        """
        This method returns uperf log file
        @return: uperf log file
        """
        workload_dir = self.__logs_operations.get_workload_dir()
        workload_files_names = [file for file in os.listdir(workload_dir) if
                                file.startswith(f'{self.__workload}-client')]
        workload_log_file = os.path.join(workload_dir, workload_files_names[0])
        return workload_log_file

    @typechecked
    def extract_uperf_result(self, workload_log_file: str):
        """
        This method extracts uperf result
        @return: uperf result
        """
        latency = 'uperf: 95%ile Latency(ms) :'
        bytes = 'Average byte : '
        iops = 'Average ops :'
        GB = 1000000000
        latency_list = []
        byte_list = []
        iops_list = []
        uperf_result = {}
        with open(workload_log_file, 'r') as file:
            for line in file:
                if latency in line:
                    latency_list.append(float(line.split()[-1]))
                if bytes in line:
                    byte_list.append(float(line.split()[-1]))
                if iops in line:
                    iops_list.append(float(line.split()[-1]))
        avg_latency = sum(latency_list) / len(latency_list)
        uperf_result['Latency'] = round(avg_latency, 2)
        avg_bytes = sum(byte_list) / len(byte_list)
        uperf_result['Throughput'] = round(avg_bytes / GB, 2)
        avg_iops = sum(iops_list) / len(iops_list)
        # uperf_result['IOPS'] = round(avg_iops,2)
        return uperf_result

    @typechecked
    def display_uperf_result(self, uperf_result: dict, workload_log_file: str):
        """
        This method displays uperf result
        @return:
        """
        # Configure Bokeh to display plots in the notebook
        output_notebook()

        # Create a DataFrame from the dictionary
        df = pd.DataFrame.from_dict(uperf_result, orient='index', columns=['Value'])

        # Round the values to 2 decimal places
        df['Value'] = df['Value'].round(2)

        # Convert the index to a list of strings
        df['Metric'] = df.index.tolist()

        # Create a Bokeh figure
        p = figure(x_range=df['Metric'].tolist(), width=VisualizeWorkloadOperations.WIDTH, title=workload_log_file.split('/')[-1], y_axis_label='Value')

        # Add vertical bars to the figure
        bars = p.vbar(x=df['Metric'], top=df['Value'], width=0.5)

        # Add labels to the bars
        labels = [f"{val:.2f}" for val in df['Value']]
        p.text(x=df['Metric'], y=df['Value'], text=labels, text_baseline="bottom", text_align="center",
               text_font_size='10pt', text_color='black')

        # Add hover tool with tooltips
        hover = HoverTool(tooltips=[('Metric', '@x'), ('Value', '@top{0.00}')], renderers=[bars])
        p.add_tools(hover)

        # Specify the output file
        output_file(os.path.join(f"{workload_log_file.split('.')[0]}.html"))

        # Display the graph
        show(p)

    def compare_results(self, result1: dict, result2: dict, legend_label1: str, legend_label2: str, block_size: str):
        """
        This method compare between 2 uperf results
        @param result1:
        @param result2:
        @param legend_label1:
        @param legend_label2:
        @param block_size: 64, 1024, 8192
        @return:
        """
        self.compare_run_results(result1=result1, result2=result2, legend_label1=legend_label1,
                                                         legend_label2=legend_label2,
                                                         title=f'Uperf block size {block_size}',
                                                         x_axis_label='Metric', y_axis_label='Rate')
