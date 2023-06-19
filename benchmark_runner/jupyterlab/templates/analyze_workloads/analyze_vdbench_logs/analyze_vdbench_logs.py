import csv
import os
import pandas as pd

# display df
from IPython.display import display

# display bokeh
from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file
from bokeh.models import HoverTool

from typeguard import typechecked

from benchmark_runner.jupyterlab.templates.logs_operations.logs_operations import LogsOperations


class AnalyzeVdbenchLogs:
    """
    This class analyzes Vdbench logs
    """
    def __init__(self, s3_logs_url: str):
        self.__workload = 'vdbench'
        self.s3_logs_url = s3_logs_url
        self.__logs_operations = LogsOperations(s3_logs_url= self.s3_logs_url )

    @staticmethod
    @typechecked
    def is_csv_file(file_path: str):
        """
        This method checks if file is csv
        @param file_path:
        @return:
        """
        try:
            with open(file_path, 'r') as file:
                dialect = csv.Sniffer().sniff(file.read(1024))
                return dialect.delimiter == ',' or dialect.delimiter == ';'
        except csv.Error:
            return False

    def get_vdbench_csv_log_files(self):
        """
        This method returns vdbench csv log files path
        @return: vdbench csv log files path
        """
        workload_dir_name = self.__logs_operations.get_workload_dir(workload=self.__workload)
        # Iterate over all files in the directory
        workload_files_path = []
        for file_name in os.listdir(workload_dir_name):
            file_path = os.path.join(workload_dir_name, file_name)
            if os.path.isfile(file_path) and self.is_csv_file(file_path) and self.__workload in file_name:
                workload_files_path.append(file_path)
        return workload_files_path

    def display_df(self):
        """
        This method display dataframe
        @return:
        """
        csv_files = self.get_vdbench_csv_log_files()
        for csv_file in csv_files:
            # Read the CSV file
            df = pd.read_csv(csv_file)
            df = df[df["Run"] != "fillup"]
            print(f"display file: {csv_file.split('/')[-1]}")
            display(df)

    def display_latency_horizontal(self):
        """
        This method displays vdbench latency horizontal
        @return:
        """
        output_notebook()

        for csv_file in self.get_vdbench_csv_log_files():
            # Read the CSV file
            df = pd.read_csv(csv_file)
            df = df[df["Run"] != "fillup"]
            df = df.sort_values("Resp")
            # Extract the desired columns from the DataFrame
            x = df["Run"]
            y = df["Resp"]

            # Create a Bokeh figure
            p = figure(title=csv_file.split('/')[-1], y_range=x, x_axis_label="Latency (sec)", width=800)

            # Add a horizontal bar glyph to the figure
            bars = p.hbar(y=x, right=y, height=0.5)

            # Add labels to the bars
            labels = [f"{val:.2f}" for val in y]
            p.text(x=y, y=x, text=labels, text_baseline="middle", text_align="left", text_font_size='10pt')

            # Add hover tool with x-axis and y-axis values
            hover = HoverTool(tooltips=[('Run', '@y'), ('Resp', '@right{0.00}')])
            p.add_tools(hover)

            # Specify the output file
            output_file(os.path.join(f"{csv_file.split('.')[0]}_latency_horizontal.html"))

            # Display the graph
            show(p)

    def display_latency_vertical(self):
        """
        This method displays vdbench latency vertical
        @return:
        """
        # Configure Bokeh to display plots in the notebook
        output_notebook()
        for csv_file in self.get_vdbench_csv_log_files():
            # Read the CSV file
            df = pd.read_csv(csv_file)
            df = df[df["Run"] != "fillup"]
            df = df.sort_values("Resp")
            # Extract the desired columns from the DataFrame
            x = df["Run"]
            y = df["Resp"]

            # Create a Bokeh figure
            p = figure(title=csv_file.split('/')[-1], x_range=x, y_axis_label="Latency (sec)", width=800)

            # Add vertical bars to the figure
            bars = p.vbar(x=x, top=y, width=0.5)

            # Add labels to the bars
            labels = [f"{val:.2f}" for val in y]
            p.text(x=x, y=y, text=labels, text_baseline="bottom", text_align="center", text_font_size='10pt')

            # Add hover tool with x-axis and y-axis values
            hover = HoverTool(tooltips=[('Run', '@x'), ('Resp', '@top{0.00}')])
            p.add_tools(hover)

            # Customize the x-axis tick labels
            p.xaxis.major_label_orientation = "vertical"

            # Specify the output file
            output_file(os.path.join(f"{csv_file.split('.')[0]}_latency_vertical.html"))

            # Display the graph
            show(p)

    def display_iops_horizontal(self):
        """
        This method displays vdbench iops horizontal
        @return:
        """
        # Configure Bokeh to display plots in the notebook
        output_notebook()

        for csv_file in self.get_vdbench_csv_log_files():
            # Read the CSV file
            df = pd.read_csv(os.path.join(csv_file))
            df = df[df["Run"] != "fillup"]
            df = df.sort_values("Rate")
            # Extract the desired columns from the DataFrame
            x = df["Run"]
            y = df["Rate"]

            # Create a Bokeh figure with adjusted width
            p = figure(title=csv_file.split('/')[-1], y_range=x, x_axis_label="IOPS", width=800)

            # Add a horizontal bar glyph to the figure
            bars = p.hbar(y=x, right=y, height=0.5)

            # Add labels to the bars
            labels = [f"{int(val):,}" for val in y]
            p.text(y=x, x=y, text=labels, text_baseline="middle", text_align="left", text_font_size='10pt')

            # Add hover tool with x-axis and y-axis values
            hover = HoverTool(tooltips=[('Run', '@y'), ('Rate', '@right{0,0}')], renderers=[bars])
            p.add_tools(hover)

            # Specify the output file
            output_file(os.path.join(f"{csv_file.split('.')[0]}_iops_horizontal.html"))

            # Display the graph
            show(p)

    def display_iops_vertical(self):
        """
        This method displays vdbench iops vertical
        @return:
        """
        # Configure Bokeh to display plots in the notebook
        output_notebook()

        for csv_file in self.get_vdbench_csv_log_files():
            # Read the CSV file
            df = pd.read_csv(csv_file)
            df = df[df["Run"] != "fillup"]
            df = df.sort_values("Rate")
            # Extract the desired columns from the DataFrame
            x = df["Run"]
            y = df["Rate"]

            # Create a Bokeh figure
            p = figure(title=csv_file.split('/')[-1], x_range=x, y_axis_label="IOPS", width=800)

            # Add vertical bars to the figure
            bars = p.vbar(x=x, top=y, width=0.5)

            # Add labels to the bars
            labels = [f"{int(val):,}" for val in y]
            p.text(x=x, y=y, text=labels, text_baseline="bottom", text_align="center", text_font_size='10pt')

            # Add hover tool with x-axis and y-axis values
            hover = HoverTool(tooltips=[('Run', '@x'), ('Rate', '@top{0,0}')], renderers=[bars])
            p.add_tools(hover)

            # Specify the output file
            output_file(os.path.join(f"{csv_file.split('.')[0]}_iops_vertical.html"))

            # Customize the x-axis tick labels
            p.xaxis.major_label_orientation = "vertical"

            # Display the graph
            show(p)
