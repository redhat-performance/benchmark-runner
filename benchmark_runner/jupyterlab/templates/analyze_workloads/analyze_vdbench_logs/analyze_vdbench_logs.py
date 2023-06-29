import csv
import os
import pandas as pd

# display df
from IPython.display import display

# display bokeh
from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file
from bokeh.models import HoverTool, Label, ColumnDataSource, LabelSet, Circle

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

    @staticmethod
    def compare_results_latency(csv_log_files1: str, csv_log_files2: str, legend_label1: str, legend_label2: str):
        """
        This method compare between latency results (Resp column)
        @param csv_log_files1:
        @param csv_log_files2:
        @param legend_label1: first bar legend
        @param legend_label2: second bar legend
        @return:
        """
        # Read the CSV file into a DataFrame
        df1 = pd.read_csv(csv_log_files2[0])
        df2 = pd.read_csv(csv_log_files1[0])

        # Filter the DataFrame to include only the desired rows
        df1 = df1[df1["Run"].isin(
            ["oltp1", "oltp2", "oltphw", "odss2", "odss128", "4kb_read_16threads", "64kb_read_4threads",
             "4kb_write_16threads", "64kb_write_4threads"])]
        df2 = df2[df2["Run"].isin(
            ["oltp1", "oltp2", "oltphw", "odss2", "odss128", "4kb_read_16threads", "64kb_read_4threads",
             "4kb_write_16threads", "64kb_write_4threads"])]

        # Set the index to the "Run" column
        df1.set_index("Run", inplace=True)
        df2.set_index("Run", inplace=True)

        # Convert the DataFrame to a dictionary
        result1 = df1["Resp"].to_dict()
        result2 = df2["Resp"].to_dict()
        # Extract the keys and values from the dictionaries
        keys = list(result1.keys())
        values1 = list(result1.values())
        values2 = list(result2.values())

        # Calculate the x-coordinates for data1 and results bars
        x1 = [i - 0.2 for i in range(len(keys))]
        x2 = [i + 0.2 for i in range(len(keys))]

        # Shift the x-coordinates to the right
        x1_shifted = [x + 0.5 for x in x1]
        x2_shifted = [x + 0.5 for x in x2]

        # Create a Bokeh figure
        p = figure(title="Vdbench Latency Comparison - Lower better", x_range=keys, y_axis_label="Latency (sec)",
                   width=1200)

        # Add vertical bars for data1
        r1 = p.vbar(x=x1_shifted, top=values1, width=0.4, color='green', legend_label=legend_label2)

        # Add vertical bars for data2
        r2 = p.vbar(x=x2_shifted, top=values2, width=0.4, color='blue', legend_label=legend_label1)

        # Customize the x-axis tick labels
        p.xaxis.major_label_orientation = 45  # Rotate the labels by 45 degrees
        p.xaxis.axis_label = "Applications"  # Add x-axis title
        p.xaxis.major_label_text_font_size = "12pt"  # Increase the label font size

        # Add tooltips for data1 bars
        hover1 = HoverTool(renderers=[r1], tooltips=[(legend_label2, "@top{0.0000}")])
        p.add_tools(hover1)

        # Add tooltips for data2 bars
        hover2 = HoverTool(renderers=[r2], tooltips=[(legend_label1, "@top{0.0000}")])
        p.add_tools(hover2)

        # Add labels for result1 bars
        for i, value in enumerate(values1):
            label = Label(x=x1_shifted[i], y=value, text=f"{value:.4f}", text_font_size="10pt", text_color="black",
                          text_baseline="bottom", text_align="center")
            p.add_layout(label)

        # Add labels for result2 bars
        for i, value in enumerate(values2):
            label = Label(x=x2_shifted[i], y=value, text=f"{value:.4f}", text_font_size="10pt", text_color="black",
                          text_baseline="bottom", text_align="center")
            p.add_layout(label)

        # Show the legend on the right side
        p.legend.location = "top_left"

        # Display the graph
        output_notebook()
        show(p)

    @staticmethod
    def compare_results(csv_log_files1: str, csv_log_files2: str, legend_label1: str, legend_label2: str,
                        metric: str):
        """
        The method compare between log files results
        @param csv_log_files1:
        @param csv_log_files2:
        @param legend_label1:
        @param legend_label2:
        @param metric: metric to compare can be 'IOPS' or 'Latency'
        @return:
        """
        if metric == 'IOPS':
            metric_key = 'Rate'
            title = 'IOPS - higher is better'
        elif metric == 'Latency':
            metric_key = 'Resp'
            title = 'Latency - lower is better'
        else:  # default IOPS
            metric_key = 'Rate'
            title = 'IOPS - higher is better'

            # Read the CSV file into a DataFrame
        df1 = pd.read_csv(csv_log_files2[0])
        df2 = pd.read_csv(csv_log_files1[0])

        # Filter the DataFrame to include only the desired rows
        columns = ["oltp1", "oltp2", "oltphw", "odss2", "odss128", "4kb_read_16threads", "64kb_read_4threads",
                   "4kb_write_16threads", "64kb_write_4threads"]
        df1 = df1[df1["Run"].isin(columns)]
        df2 = df2[df2["Run"].isin(columns)]

        # Set the index to the "Run" column
        df1.set_index("Run", inplace=True)
        df2.set_index("Run", inplace=True)

        # Convert the DataFrame to a dictionary Rate/Resp
        result1 = df1[metric_key].to_dict()
        result2 = df2[metric_key].to_dict()

        # Extract the keys and values from the dictionaries
        keys = list(result1.keys())
        values1 = list(result1.values())
        values2 = list(result2.values())

        # Calculate the x-coordinates for data1 and data2 bars
        x1 = [i - 0.2 for i in range(len(keys))]
        x2 = [i + 0.2 for i in range(len(keys))]

        # Shift the x-coordinates to the right
        x1_shifted = [x + 0.5 for x in x1]
        x2_shifted = [x + 0.5 for x in x2]

        # Create a Bokeh figure
        p = figure(title=f"Vdbench {title}", x_range=keys, y_axis_label="Latency (sec)", width=1200, height=600)

        # Adjust the y-axis range
        p.y_range.start = 0
        p.y_range.end = max(max(result1.values()), max(result2.values())) * 2

        # Add vertical bars for data1
        r1 = p.vbar(x=x1_shifted, top=values1, width=0.4, color='green', legend_label=legend_label2)

        # Add vertical bars for data2
        r2 = p.vbar(x=x2_shifted, top=values2, width=0.4, color='blue', legend_label=legend_label1)

        # Percentage line
        # Calculate the percentage difference between data1 and data2
        percentage_diff = [(v1 - v2) / v2 * 100 if v2 != 0 else 0 for v1, v2 in zip(values1, values2)]
        percentage_diff = [round(diff, 2) for diff in percentage_diff]  # Round to 2 decimal places

        # Customize the x-axis tick labels
        p.xaxis.major_label_orientation = 45  # Rotate the labels by 45 degrees
        p.xaxis.axis_label = "Applications"  # Add x-axis title
        p.xaxis.major_label_text_font_size = "12pt"  # Increase the label font size

        # Add tooltips for data1 bars
        hover1 = HoverTool(renderers=[r1], tooltips=[(legend_label2, "@top{0.00}")])
        p.add_tools(hover1)

        # Add tooltips for data2 bars
        hover2 = HoverTool(renderers=[r2], tooltips=[(legend_label1, "@top{0.00}")])
        p.add_tools(hover2)

        # Add labels for result1 bars
        for i, value in enumerate(values1):
            label = Label(x=x1_shifted[i], y=value, text=f"{value:.2f}", text_font_size="10pt", text_color="black",
                          text_baseline="bottom", text_align="center")
            p.add_layout(label)

        # Add labels for result2 bars
        for i, value in enumerate(values2):
            label = Label(x=x2_shifted[i], y=value, text=f"{value:.2f}", text_font_size="10pt", text_color="black",
                          text_baseline="bottom", text_align="center")
            p.add_layout(label)

        # Calculate the maximum value from result1 and result2 dictionaries
        min_value = min(min(values1), min(values2))

        # Calculate the percentage difference between data1 and data2
        if metric == 'Latency':
            percentage_diff = [(v1 - v2) / v2 * 100 if v2 != 0 else 0 for v1, v2 in zip(values1, values2)]
        elif metric == 'IOPS':
            percentage_diff = [(v2 - v1) / v1 * 100 if v2 != 0 else 0 for v1, v2 in zip(values1, values2)]
        percentage_diff = [round(diff, 2) for diff in percentage_diff]  # Round to 2 decimal places

        # Calculate the x-coordinates for the dots
        x_middle = [(x1_shifted[i] + x2_shifted[i]) / 2 for i in range(len(keys))]

        # Calculate the y-coordinate for the dots
        y_middle = [max(values1[i], values2[i]) + min_value for i in range(len(keys))]

        # Add dots for each number on the line
        dot_source = ColumnDataSource(data=dict(x=x_middle, y=y_middle, values=percentage_diff))
        dot_glyph = Circle(x='x', y='y', size=6, line_color='red', fill_color='white')
        p.add_glyph(dot_source, dot_glyph)

        # Add lines showing the percentage difference
        line_source = ColumnDataSource(data=dict(x=x_middle, y=y_middle, values=percentage_diff))
        line_glyph = p.line(x='x', y='y', source=line_source, line_width=2, line_color="orange")

        # Add labels for percentage difference
        for i, diff in enumerate(percentage_diff):
            x_pos = x_middle[i]
            y_pos = y_middle[i] + 0.1  # Adjust the y-coordinate to move the labels above the line
            label = Label(x=x_pos, y=y_pos, text=f"{diff}%", text_font_size="10pt", text_color="orange",
                          text_baseline="bottom", text_align='center')  # Set text_color to 'green'
            p.add_layout(label)

        # Show the legend on the top-left corner
        p.legend.location = "top_right"

        # Display the graph
        output_notebook()
        show(p)

    def compare_latency(self, csv_log_files1: str, csv_log_files2: str, legend_label1: str, legend_label2: str,
                        metric: str = 'Latency'):
        """
        This method compare latency results between logs
        @param csv_log_files2:
        @param legend_label1:
        @param legend_label2:
        @param metric:
        @return: default Latency
        """
        self.compare_results(csv_log_files1, csv_log_files2, legend_label1, legend_label2, metric=metric)

    def compare_iops(self, csv_log_files1: str, csv_log_files2: str, legend_label1: str, legend_label2: str,
                        metric: str = 'IOPS'):
        """
        This method compare iops results between logs
        @param csv_log_files2:
        @param legend_label1:
        @param legend_label2:
        @param metric: default IOPS
        @return:
        """
        self.compare_results(csv_log_files1, csv_log_files2, legend_label1, legend_label2, metric=metric)