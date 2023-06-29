import csv
import os
import pandas as pd

# display df
from IPython.display import display

# display bokeh
from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file
from bokeh.models import HoverTool, Label, ColumnDataSource, LabelSet, Circle, NumeralTickFormatter

from typeguard import typechecked

from benchmark_runner.jupyterlab.templates.logs_operations.logs_operations import LogsOperations


class AnalyzeHammerdbLogs:
    """
    This class analyzes Hammerdb logs
    """

    def __init__(self, s3_logs_url: str):
        self.__workload = 'hammerdb'
        self.s3_logs_url = s3_logs_url
        self.__logs_operations = LogsOperations(s3_logs_url=self.s3_logs_url)

    def get_hammerdb_log_file(self):
        """
        This method returns hammerdb log file
        @return: hammerdb log file
        """
        workload_dir = self.__logs_operations.get_workload_dir(workload=self.__workload)
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

    @staticmethod
    def compare_results(result1: dict, result2: dict, legend_label1: str, legend_label2: str, database: str):
        """
        This method compare between 2 hammerdb results
        @param result1: hammerdb thread results in dictionary
        @param result2: hammerdb thread results in dictionary
        @param legend_label1: first bar legend
        @param legend_label2: second bar legend
        @param database: PostgreSQL, Mariadb, MSSQL
        @return:
        """
        # Convert values to integers
        values1 = [int(value) for value in result1.values()]
        values2 = [int(value) for value in result2.values()]

        threads = list(result1.keys())

        width = 0.3
        x = [i for i in range(len(threads))]
        offset = 0.1  # Adjust the offset for x-axis shift
        x_middle = [i + width / 2 + offset for i in x]  # Adjust x-coordinates for centering and shift

        p = figure(title=f"{database} KTPM [ KTransactions Per Minutes ]", x_range=threads,
                   y_axis_label="Latency (sec)", width=1200, height=600)
        p.xaxis.axis_label = "Threads"  # Add x-axis title
        p.yaxis.axis_label = "KTPM"  # Add y-axis title

        r1 = p.vbar(x=x_middle, top=values2, width=width,
                    line_color='white', fill_color='green', alpha=0.8,
                    legend_label=legend_label2, name=legend_label2)

        r2 = p.vbar(x=[i + width for i in x_middle], top=values1, width=width,
                    line_color='white', fill_color='blue', alpha=0.8,
                    legend_label=legend_label1, name=legend_label1)

        p.xgrid.grid_line_color = None
        p.legend.location = "top_right"
        p.legend.title = "Versions"

        p.x_range.range_padding = 0.1  # Adjust the padding between bars

        tooltips_1 = [("Version", legend_label2), ("KTPM", "@top{0,}")]
        tooltips_2 = [("Version", legend_label1), ("KTPM", "@top{0,}")]

        hover_1 = HoverTool(renderers=[r1], tooltips=tooltips_1)
        hover_2 = HoverTool(renderers=[r2], tooltips=tooltips_2)

        p.add_tools(hover_1, hover_2)  # Add the HoverTools to the figure

        # Add y-values on top of each bar
        for i, value in enumerate(values2):
            label = Label(x=x_middle[i], y=value, text=f"{value:,}", text_font_size="10pt", text_color="black",
                          text_baseline="bottom", text_align="center")
            p.add_layout(label)

        for i, value in enumerate(values1):
            label = Label(x=x_middle[i] + width, y=value, text=f"{value:,}", text_font_size="10pt", text_color="black",
                          text_baseline="bottom", text_align="center")
            p.add_layout(label)

        p.yaxis.formatter = NumeralTickFormatter(format="0,")  # Format y-axis tick labels with commas

        # Percentage line

        # Calculate the percentage difference between result1 and result2
        percentage_diff = [(v1 - v2) / v2 * 100 if v2 != 0 else 0 for v1, v2 in zip(values1, values2)]
        percentage_diff = [round(diff, 2) for diff in percentage_diff]  # Round to 2 decimal places

        # Calculate the x-coordinates for the dots
        x_middle = [i + width / 2 + offset for i in x]

        # Calculate the maximum value from result1 and result2 dictionaries
        min_value = min(min(values1), min(values2))

        # Calculate the y-coordinate for the dots
        y_middle = [max(values1[i], values2[i]) + min_value for i in range(len(threads))]

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
                          text_baseline="bottom", text_align='center')
            p.add_layout(label)
        # Display the graph
        output_notebook()
        show(p)
