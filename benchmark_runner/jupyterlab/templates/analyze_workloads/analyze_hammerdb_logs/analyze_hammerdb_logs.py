
import os
from typeguard import typechecked

# display bokeh
from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file
from bokeh.models import HoverTool, Label, ColumnDataSource, LabelSet, Circle, NumeralTickFormatter


from benchmark_runner.jupyterlab.templates.logs_operations.logs_operations import LogsOperations
from benchmark_runner.jupyterlab.templates.analyze_workloads.visualize_workload_operations import VisualizeWorkloadOperations


class AnalyzeHammerdbLogs(VisualizeWorkloadOperations):
    """
    This class analyzes Hammerdb logs
    """

    def __init__(self, s3_logs_url: str):
        super().__init__()
        self.__workload = 'hammerdb'
        self.s3_logs_url = s3_logs_url
        self.__logs_operations = LogsOperations(s3_logs_url=self.s3_logs_url)

    def get_hammerdb_log_file(self):
        """
        This method returns hammerdb log file
        @return: hammerdb log file
        """
        workload_dir = self.__logs_operations.get_workload_dir()
        workload_files = [file for file in os.listdir(workload_dir) if file.startswith(self.__workload)]
        # Iterate over all files in the directory
        for file_name in workload_files:
            if 'workload' in file_name:
                workload_log_file = os.path.join(workload_dir, file_name)
        return workload_log_file

    @typechecked
    def extract_hammerdb_result(self, workload_log_file: str):
        """
        This method extracts hammerdb result
        @return: hammerdb result
        """
        start_content = '+-------------------------------------------------- HammerDB Results --------------------------------------------------+'
        end_content = '+-------------------------------------------------------------------------------------------------------------------+'
        with open(workload_log_file, 'r') as file:
            hammerdb_result = {}
            should_print = False
            for line in file:
                line = line.strip()
                if start_content in line:
                    should_print = True
                elif end_content in line:
                    should_print = False
                elif should_print:
                    if 'Worker(s):' in line:
                        thread = line.split(':')[-1]
                    if 'TPM:' in line:
                        tpm = line.split(':')[-1]
                        hammerdb_result[thread] = tpm
        return hammerdb_result

    @typechecked
    def display_hammerdb_result(self, hammerdb_result: dict, workload_log_file: str):
        """
        This method displays hammerdb result
        @return:
        """
        # Convert dictionary keys and values to lists
        x = list(hammerdb_result.keys())
        y = [int(val) for val in hammerdb_result.values()]

        # Create a figure
        p = figure(x_range=x, title=workload_log_file.split('/')[-1], x_axis_label='Threads', y_axis_label='TPM')

        # Set y-axis type to display full numbers
        p.yaxis.axis_label_text_font_size = '10pt'
        p.yaxis.axis_label_text_font_style = 'normal'
        p.yaxis.formatter = NumeralTickFormatter(format='0,0')
        p.yaxis.axis_label_standoff = 10

        # Add vertical bars to the figure with wider width
        bars = p.vbar(x=x, top=y, width=0.8)

        # Calculate the lower position for the labels
        label_offset = max(y) * 0.01
        label_y = [val - label_offset for val in y]

        # Add labels below the bars with commas
        p.text(x=x, y=label_y, text=[f"{val:,}" for val in y], text_baseline="top", text_align="center",
               text_font_size='10pt', text_color='white')

        # Add hover tool with x-axis and y-axis values
        hover = HoverTool(tooltips=[('Threads', '@x'), ('TPM', '@top{0,0}')], renderers=[bars])
        p.add_tools(hover)

        # Specify the output file
        output_file(os.path.join(f"{workload_log_file.split('.')[0]}.html"))

        # Display the plot in the notebook
        output_notebook()
        show(p)

    def compare_results(self, result1: dict, result2: dict, legend_label1: str, legend_label2: str, database: str):
        """
        This method compare between 2 hammerdb results
        @param result1:
        @param result2:
        @param legend_label1:
        @param legend_label2:
        @param database: PostgreSQL, Mariadb, MSSQL
        @return:
        """
        self.compare_run_results(result1=result1, result2=result2, legend_label1=legend_label1, legend_label2=legend_label2, title=f'{database} KTPM [ KTransactions Per Minutes ]', x_axis_label = 'Threads', y_axis_label= 'KTPM')
