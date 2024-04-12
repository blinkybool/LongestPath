""" Various utilities (especially plotting related) for the notebooks.
"""
import matplotlib.pyplot as plt
import os
import sys

top_level_path = os.path.abspath(os.path.join('..'))
if top_level_path not in sys.path:
	sys.path.append(top_level_path)

from benchmarking import Benchmark


# The standard matplotlib color cycle
prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

# All methods that we are considering that can be compared on running time
all_methods = [
  "brute('BRANCH_N_BOUND')",
  "brute('BRUTE_FORCE')",
  "brute('BRUTE_FORCE_COMPLETE')",
  "brute('FAST_BOUND')",
  "ilp()",
  "kalp()",
  "kalp(threads=4)"
]
method_name_dict = {
  "brute('BRANCH_N_BOUND')" : "Branch and bound",
  "brute('BRUTE_FORCE')" : "Brute force",
  "brute('BRUTE_FORCE_COMPLETE')" : "Brute force (complete)",
  "brute('FAST_BOUND')" : "Fast bound",
  "ilp()" : "ILP",
  "kalp()" : "KaLP single threaded",
  "kalp(threads=4)" : "KaLP on 4 threads",
}

# We assign specific colors to the methods
color_assignment = {method : col for method, col in zip(all_methods, colors)}
color_assignment


def build_plotting_dataframes(benchmark: Benchmark):
  """ Builds dataframes relevant for making plots of average out degree over time.
  """
  df = benchmark.get_dataframe()
  # Group by average_out_degree
  df_grouped = df \
    .groupby(['average_out_degree', 'solver', 'solver_name']) \
    .agg({
      "run_time": ["mean", "median", "std"], 
      "failure": "any"
    }) \
    .reset_index() \
    .rename(columns={"any": ""})

  # Collapse the multicolumns
  # Example:
  # ("name1", "name2") |-> "name1_name2"
  # ("name" , ""     ) |-> "name"
  df_grouped.columns = [a + ("_" + b if b != "" else "")  for (a,b) in df_grouped.columns]

  # We remove groups with even a single failure as these would yield biased aggregates
  df_grouped_failures_removed = df_grouped[df_grouped["failure"] == False]

  # We pivot the resulting df so that it is easy to plot using df.plot()
  to_plot = df_grouped_failures_removed.pivot(
    index='average_out_degree', 
    columns='solver_name', 
    values=['run_time_mean', 'run_time_std']
  ).reset_index()

  return df, df_grouped, df_grouped_failures_removed, to_plot

def setup_info(to_plot, title=None):
    """ Set up the info for a 'running time by average degree' plot
    """
    if title != None: plt.title(title)
    plt.ylabel("run-time (seconds)")
    plt.xlabel("mean degree")
    methods = list(to_plot.columns.droplevel())
    plt.legend([method_name_dict[m] for m in methods[1:len(methods)//2+1]], loc='center left', bbox_to_anchor=(1, 0.5))
  
def plt_with_scatter(benchmark: Benchmark, offsets = None, title=None):
    """ 
    Creates a mixed line and scatter plot of the running time by the average degree.
    Args:
    - benchmark
    - offset, a list of horizontal offset values per method for the scatter values.
    - title, an optional title
    """
    df, df_grouped, df_grouped_failures_removed, to_plot = build_plotting_dataframes(benchmark)

    fig, ax = plt.subplots()

    to_plot.plot(
        style="o-", 
        x="average_out_degree", 
        y="run_time_mean", 
        color=color_assignment, 
        ax=ax
    )

    offset_values = offsets if offsets != None else [0 for _ in benchmark.solver_names()]

    for offsets, solver_name in zip(offset_values, benchmark.solver_names()):
        solver_df = df[df["solver_name"] == solver_name]  # Select rows where run-time is not null
        plt.scatter(
            solver_df['average_out_degree'] + offsets,  
            solver_df['run_time'], 
            label=solver_name, 
            alpha=0.2, 
            s=7,
            color=color_assignment[solver_name]
        )
    setup_info(to_plot, title=title)


def plot_with_symmetric_errbars(benchmark: Benchmark, offsets = None, title=None):
    """
    Creates a plot with symmetric error bars of the running time by the average degree.
    Args:
    - benchmark
    - offset, a list of horizontal offset values per method for the errorbars
    - title, an optional title
    """
    df, df_grouped, df_grouped_failures_removed, to_plot = build_plotting_dataframes(benchmark)

    fig, ax = plt.subplots()

    to_plot.plot(
        style="o-",
        x="average_out_degree",
        y="run_time_mean", 
        color=color_assignment,
        ax=ax,
    )

    offset_values = offsets if offsets != None else [0 for _ in benchmark.solver_names()]

    for offsets, solver_name in zip(offset_values, benchmark.solver_names()):
        plt.errorbar(
        to_plot['average_out_degree'] + offsets,
        to_plot['run_time_mean'][solver_name],
        yerr = to_plot['run_time_std'][solver_name],
        fmt='none',
        capsize=3,
        alpha=0.5,
        color=color_assignment[solver_name],
        )
    setup_info(to_plot, title=title)
