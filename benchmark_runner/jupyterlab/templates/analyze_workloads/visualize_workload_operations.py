
# display df
from IPython.display import clear_output

# display bokeh
from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file
from bokeh.models import HoverTool, Label, ColumnDataSource, LabelSet, Circle, NumeralTickFormatter


class VisualizeWorkloadOperations:
    """
    This class for visualize workloads operations
    """

    WIDTH = 1200
    HEIGHT = 600

    def __init__(self):
        self.clear_output()

    @staticmethod
    def clear_output():
        """
        This method clean output
        @return:
        """
        # clean latest bokeh output
        clear_output(wait=True)

    def compare_run_results(self, result1: dict, result2: dict, legend_label1: str, legend_label2: str, **workload_data: dict):
        """
        This method compare between 2 results
        @param result1: thread results in dictionary
        @param result2: thread results in dictionary
        @param legend_label1: first bar legend
        @param legend_label2: second bar legend
        @return:
        """
        title = workload_data.get('title')
        x_axis_label = workload_data.get('x_axis_label')
        y_axis_label = workload_data.get('y_axis_label')

        # Convert values to integers
        values1 = [float(value) for value in result1.values()]
        values2 = [float(value) for value in result2.values()]

        metrics = list(result1.keys())

        width = 0.3
        x = [i for i in range(len(metrics))]
        offset = 0.1  # Adjust the offset for x-axis shift
        x_middle = [i + width / 2 + offset for i in x]  # Adjust x-coordinates for centering and shift

        p = figure(title=title, x_range=metrics, width=self.WIDTH, height=self.HEIGHT)
        p.xaxis.axis_label = x_axis_label  # Add x-axis title
        p.yaxis.axis_label = y_axis_label  # Add y-axis title

        r1 = p.vbar(x=x_middle, top=values1, width=width,
                    line_color='white', fill_color='green', alpha=0.8,
                    legend_label=legend_label1, name=legend_label2)

        r2 = p.vbar(x=[i + width for i in x_middle], top=values2, width=width,
                    line_color='white', fill_color='blue', alpha=0.8,
                    legend_label=legend_label2, name=legend_label1)

        p.xgrid.grid_line_color = None
        p.legend.location = 'top_right'
        p.legend.title = 'Versions'

        p.x_range.range_padding = 0.1  # Adjust the padding between bars

        tooltips_1 = [('Version', legend_label1), (f'{y_axis_label}', '@top{0,0.00}')]
        tooltips_2 = [('Version', legend_label2), (f'{y_axis_label}', '@top{0,0.00}')]

        hover_1 = HoverTool(renderers=[r1], tooltips=tooltips_1)
        hover_2 = HoverTool(renderers=[r2], tooltips=tooltips_2)

        p.add_tools(hover_1, hover_2)  # Add the HoverTools to the figure

        # Add y-values on top of each bar
        for i, value in enumerate(values1):
            label = Label(x=x_middle[i], y=value, text=f'{value:,.2f}', text_font_size='8pt', text_color='black',
                          text_baseline='bottom', text_align='center')
            p.add_layout(label)

        for i, value in enumerate(values2):
            label = Label(x=x_middle[i] + width, y=value, text=f'{value:,.2f}', text_font_size='8pt',
                          text_color='black',
                          text_baseline='bottom', text_align='center')
            p.add_layout(label)

        p.yaxis.formatter = NumeralTickFormatter(format='0,')  # Format y-axis tick labels with commas

        # Percentage line

        # Calculate the percentage difference between result1 and result2
        # latency: Lower is better
        if 'latency'.upper() in [key.upper().upper() for key in result1.keys()]:
            percentage_diff = [(v1 - v2) / v2 * 100 if v2 != 0 else 0 for v1, v2 in zip(values1, values2)]
        else:  # Other: Higher is better
            percentage_diff = [(v2 - v1) / v1 * 100 if v1 != 0 else 0 for v1, v2 in zip(values1, values2)]
        percentage_diff = [round(diff, 2) for diff in percentage_diff]  # Round to 2 decimal places

        # Calculate the x-coordinates for the dots
        x_middle = [i + width / 2 + offset for i in x]

        # Calculate the maximum value from result1 and result2 dictionaries
        min_value = min(min(values1), min(values2))

        # Calculate the y-coordinate for the dots
        y_middle = [max(values1[i], values2[i]) + min_value for i in range(len(metrics))]

        # Add labels and dots for percentage difference
        for i, diff in enumerate(percentage_diff):
            x_pos = x_middle[i] + width / 4  # Adjust the x-coordinate to shift the label to the right
            y_pos = y_middle[i] + 0.1  # Adjust the y-coordinate to move the labels above the line
            color = 'red' if diff < 0 else 'green'  # Set label and dot color based on the sign of the difference
            label = Label(x=x_pos, y=y_pos, text=f'{diff}%', text_font_size='14pt', text_color=color,
                          text_baseline='bottom', text_align='center')
            p.add_layout(label)

            # Adjust the y-coordinate to place the dots below the labels
            dot_y = y_pos - 0.1
            dot_x = x_pos + width / 4  # Adjust the x-coordinate to shift the dots to the right

            # Change dot color based on the sign of the difference
            dot_color = 'red' if diff < 0 else 'green'
            dot_source = ColumnDataSource(data=dict(x=[dot_x], y=[dot_y], color=[dot_color]))
            p.circle(x='x', y='y', size=8, fill_color='color', line_color='color', source=dot_source)

        # Display the graph
        output_notebook()
        show(p)
