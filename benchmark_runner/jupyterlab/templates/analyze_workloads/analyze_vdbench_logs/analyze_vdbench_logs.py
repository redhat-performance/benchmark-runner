
import csv
import os
import pandas as pd

# display df
from IPython.display import display
from typeguard import typechecked

# display bokeh
from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file
from bokeh.models import HoverTool, Label, ColumnDataSource, LabelSet, Circle, NumeralTickFormatter

from benchmark_runner.jupyterlab.templates.logs_operations.logs_operations import LogsOperations
from benchmark_runner.jupyterlab.templates.analyze_workloads.visualize_workload_operations import VisualizeWorkloadOperations


class AnalyzeVdbenchLogs(VisualizeWorkloadOperations):
    """
    This class analyzes Vdbench logs
    """
    def __init__(self, s3_logs_url: str):
        super().__init__()
        self.__workload = 'vdbench'
        self.s3_logs_url = s3_logs_url
        self.__logs_operations = LogsOperations(s3_logs_url=self.s3_logs_url)

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
        workload_dir_name = self.__logs_operations.get_workload_dir()
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
            df = df[df['Run'] != 'fillup']
            print(f"display file: {csv_file.split('/')[-1]}")
            display(df)

    def __display_horizontal(self, metric: str):
        """
        This method displays Vdbench metric horizontal
        @param metric: Latency/ IOPS
        @return:
        """
        metric_key, title = self.init_and_get_key_metric(metric)
        for csv_file in self.get_vdbench_csv_log_files():
            # Read the CSV file
            df = pd.read_csv(csv_file)
            df = df[df['Run'] != 'fillup']
            df = df.sort_values(metric_key)
            # Extract the desired columns from the DataFrame
            x = df['Run']
            y = df[metric_key]

            # Reverse the order of x values
            y = y[::-1]

            # Create a Bokeh figure
            p = figure(title=csv_file.split('/')[-1], y_range=x, x_axis_label='Latency (sec)',  width=VisualizeWorkloadOperations.WIDTH, height=VisualizeWorkloadOperations.HEIGHT)

            # Add a horizontal bar glyph to the figure with legend_label
            bars = p.hbar(y=x, right=y, height=0.5, legend_label=metric)

            # Add labels to the bars
            labels = [f"{val:,.2f}" for val in y]
            p.text(x=y, y=x, text=labels, text_baseline='middle', text_align='left', text_font_size='10pt')

            # Add hover tool with x-axis and y-axis values
            hover = HoverTool(tooltips=[('Run', '@y'), (metric, '@right{0,0.00}')], renderers=[bars])
            p.add_tools(hover)

            # Customize the legend
            p.legend.title = title
            p.legend.location = 'top_right'
            p.legend.orientation = 'vertical'
            p.legend.click_policy = 'hide'

            # Display the graph
            show(p)

    def display_iops_horizontal(self):
        """
        This method displays iops horizontal
        @return:
        """
        self.__display_horizontal(metric='IOPS')

    def display_latency_horizontal(self):
        """
        This method displays latency horizontal
        @return:
        """
        self.__display_horizontal(metric='Latency')

    def __display_vertical(self, metric: str):
        """
        This method displays Vdbench metric vertical
        @param metric: Latency/ IOPS
        @return:
        """
        metric_key, title = self.init_and_get_key_metric(metric)
        for csv_file in self.get_vdbench_csv_log_files():
            # Read the CSV file
            df = pd.read_csv(csv_file)
            df = df[df['Run'] != 'fillup']
            df = df.sort_values(metric_key)
            # Extract the desired columns from the DataFrame
            x = df['Run']
            y = df[metric_key]

            # Create a Bokeh figure
            p = figure(title=csv_file.split('/')[-1], x_range=x, y_axis_label=metric, width=VisualizeWorkloadOperations.WIDTH, height=VisualizeWorkloadOperations.HEIGHT)

            # Add vertical bars to the figure with legend_label
            bars = p.vbar(x=x, top=y, width=0.5, legend_label=metric)

            # Add labels to the bars
            labels = [f"{val:,.2f}" for val in y]
            p.text(x=x, y=y, text=labels, text_baseline='bottom', text_align='center', text_font_size='10pt')

            # Add hover tool with x-axis and y-axis values
            hover = HoverTool(tooltips=[('Run', '@x'), (metric, '@top{0,0.00}')], renderers=[bars])
            p.add_tools(hover)

            # Customize the y-axis tick formats
            p.yaxis.formatter = NumeralTickFormatter(format='0,0')

            # Customize the x-axis tick labels
            p.xaxis.major_label_orientation = 'vertical'
            p.xaxis.major_label_orientation = 45  # Rotate the labels by 45 degrees

            # Customize the legend
            p.legend.location = 'top_left'
            p.legend.orientation = 'vertical'
            p.legend.click_policy = 'hide'

            # Display the graph
            show(p)

    def display_iops_vertical(self):
        """
        This method displays iops vertical
        @return:
        """
        self.__display_vertical(metric='IOPS')

    def display_latency_vertical(self):
        """
        This method displays latency vertical
        @return:
        """
        self.__display_vertical(metric='Latency')

    @staticmethod
    def init_and_get_key_metric(metric: str):
        """
        This method init metric
        @param metric:
        @return:
        """
        if metric == 'Latency':
            metric_key = 'Resp'
            title = 'Latency - lower is better'
        elif metric == 'IOPS':
            metric_key = 'Rate'
            title = 'IOPS - higher is better'
        else:  # default Latency
            metric_key = 'Rate'
            title = 'IOPS - higher is better'
        # Configure Bokeh to display plots in the notebook
        output_notebook()
        return metric_key, title

    def __compare_results(self, csv_log_files1: str, csv_log_files2: str, legend_label1: str, legend_label2: str,
                          metric: str):
        """
        This method compares between artifacts run results
        @param csv_log_files1:
        @param csv_log_files2:
        @param legend_label1:
        @param legend_label2:
        @param metric:
        @return:
        """
        metric_key, title = self.init_and_get_key_metric(metric)
        # Read the CSV file into a DataFrame
        df1 = pd.read_csv(csv_log_files1[0])
        df2 = pd.read_csv(csv_log_files2[0])

        # Filter the DataFrame to include only the desired rows
        columns = ['oltp1', 'oltp2', 'oltphw', 'odss2', 'odss128', '4kb_read_16threads', '64kb_read_4threads',
                   '4kb_write_16threads', '64kb_write_4threads']
        df1 = df1[df1['Run'].isin(columns)]
        df2 = df2[df2['Run'].isin(columns)]

        # Set the index to the "Run" column
        df1.set_index('Run', inplace=True)
        df2.set_index('Run', inplace=True)

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

        # Shift the x-coordinates to the right switch between x1 to x2 to change the bar display order
        x1_shifted = [x + 0.5 for x in x2]
        x2_shifted = [x + 0.5 for x in x1]

        # Create a Bokeh figure
        p = figure(title=f'Vdbench {title}', x_range=keys, y_axis_label='Latency (sec)',  width=VisualizeWorkloadOperations.WIDTH, height=VisualizeWorkloadOperations.HEIGHT)

        # Adjust the y-axis range
        p.y_range.start = 0
        p.y_range.end = max(max(result1.values()), max(result2.values())) * 2
        p.yaxis.formatter = NumeralTickFormatter(format='0,')  # Format y-axis tick labels with commas

        # Add vertical bars for data1
        r1 = p.vbar(x=x2_shifted, top=values1, width=0.4, color='green', legend_label=legend_label1)

        # Add vertical bars for data2
        r2 = p.vbar(x=x1_shifted, top=values2, width=0.4, color='blue', legend_label=legend_label2)

        # Calculate the percentage difference between values1 and values2
        percentage_diff = [(v1 - v2) / v2 * 100 if v2 != 0 else 0 for v1, v2 in zip(values1, values2)]
        percentage_diff = [round(diff, 2) for diff in percentage_diff]  # Round to 2 decimal places

        # Customize the x-axis tick labels
        p.xaxis.major_label_orientation = 45  # Rotate the labels by 45 degrees
        p.xaxis.axis_label = 'Applications'  # Add x-axis title
        p.xaxis.major_label_text_font_size = '12pt'  # Increase the label font size

        # Add tooltips for data1 bars
        hover1 = HoverTool(renderers=[r1], tooltips=[(legend_label1, '@top{0,0.00}')])
        p.add_tools(hover1)

        # Add tooltips for data2 bars
        hover2 = HoverTool(renderers=[r2], tooltips=[(legend_label2, '@top{0,0.00}')])
        p.add_tools(hover2)

        # Add labels for result1 bars
        for i, value in enumerate(values2):
            label = Label(x=x1_shifted[i], y=value, text=f'{value:,.2f}', text_font_size='8pt', text_color='black',
                          text_baseline='bottom', text_align='center')
            p.add_layout(label)

        # Add labels for result2 bars
        for i, value in enumerate(values1):
            label = Label(x=x2_shifted[i], y=value, text=f'{value:,.2f}', text_font_size='8pt', text_color='black',
                          text_baseline='bottom', text_align='center')
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

        # Add labels and dots for percentage difference
        for i, diff in enumerate(percentage_diff):
            x_pos = x_middle[i]
            y_pos = y_middle[i] + 0.1  # Adjust the y-coordinate to move the labels above the line
            color = "red" if diff < 0 else 'green'  # Set label and dot color based on the sign of the difference
            label = Label(x=x_pos, y=y_pos, text=f'{diff}%', text_font_size='14pt', text_color=color,
                          text_baseline='bottom', text_align='center')
            p.add_layout(label)

            # Adjust the y-coordinate to place the dots below the labels
            dot_y = y_pos - 0.1

            # Change dot color based on the sign of the difference
            dot_color = 'red' if diff < 0 else 'green'
            dot_source = ColumnDataSource(data=dict(x=[x_middle[i]], y=[dot_y], color=[dot_color]))
            p.circle(x='x', y='y', size=8, fill_color='color', line_color='color', source=dot_source)

        # Display the graph
        show(p)

    def compare_latency(self, csv_log_files1: str, csv_log_files2: str, legend_label1: str, legend_label2: str,
                        metric: str = 'Latency'):
        """
        This method compares latency results between logs
        @param csv_log_files1:
        @param csv_log_files2:
        @param legend_label1:
        @param legend_label2:
        @param metric:
        @return:
        """
        self.__compare_results(csv_log_files1, csv_log_files2, legend_label1, legend_label2, metric=metric)

    def compare_iops(self, csv_log_files1: str, csv_log_files2: str, legend_label1: str, legend_label2: str,
                     metric: str = 'IOPS'):
        """
        This method compares iops results between logs
        @param csv_log_files1:
        @param csv_log_files2:
        @param legend_label1:
        @param legend_label2:
        @param metric:
        @return:
        """
        self.__compare_results(csv_log_files1, csv_log_files2, legend_label1, legend_label2, metric=metric)
