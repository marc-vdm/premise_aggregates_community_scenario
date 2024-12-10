from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

import os

from ..statics import UNIT, IMAGE_REGION_COLORS

PATH = "./stock_model_figures"
FIGURE_FORMAT = ".png"


df = pd.read_csv("../filtered_to_list.csv")

YEARS = [y for y in range(2020, 2051)]

# # filter on years
df = df[df["year"].isin(YEARS)]

def plot_col(df, col_name):

    _df = df.pivot_table(index=["Region"], columns="year", values=[col_name]).reset_index()


    for _, row in _df.iterrows():

        color = IMAGE_REGION_COLORS.get(row.values[0], "#000000")
        ax.plot(YEARS, row.values[1:], label=row.values[0], color=color)

    lgd = ax.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=2, borderaxespad=0.)

    ax.set_title(f"{col_name} per region")
    ax.grid('on')

    plt.show()

    fig.savefig(f"../figure_test_{col_name}.svg", bbox_extra_artists=(lgd,), bbox_inches='tight')

plots = [f"inflow ({UNIT})", f"outflow ({UNIT})", f"available stock ({UNIT})", f"recycled inflow ({UNIT})", "substitution"]
plots = [f"available stock ({UNIT})"]

for plot_name in plots:
    print(plot_name)
    plot_col(df, plot_name)

def plot_2col(df, col_name1, col_name2):
    # Figure market share
    _df_col1 = df.pivot_table(index=["Region"], columns="year", values=[col_name1]).reset_index()
    _df_col2 = df.pivot_table(index=["Region"], columns="year", values=[col_name2]).reset_index()

    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    for _, row in _df_col1.iterrows():
        color = IMAGE_REGION_COLORS.get(row.values[0], "#000000")
        ax.plot(YEARS, row.values[1:], label=row.values[0], color=color)

    for _, row in _df_col2.iterrows():
        color = IMAGE_REGION_COLORS.get(row.values[0], "#000000")
        ax.plot(YEARS, row.values[1:], label=row.values[0], color=color, linestyle="dashed")

    lgd = ax.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=2, borderaxespad=0.)

    ax.set_title(f"In-and-Outflow per region")
    ax.grid('on')

    plt.show()

    fig.savefig(f"../figure_test_In-and-Outflow.svg", bbox_extra_artists=(lgd,), bbox_inches='tight')

plot_2col(df, f"inflow ({UNIT})", f"outflow ({UNIT})")


# Figure market share
_df_col1 = df.pivot_table(index=["Region"], columns="year", values=[f"inflow ({UNIT})"]).reset_index()
_df_col2 = df.pivot_table(index=["Region"], columns="year", values=[f"outflow ({UNIT})"]).reset_index()
_df_col3 = df.pivot_table(index=["Region"], columns="year", values=["substitution"]).reset_index()

fig = plt.figure(1)
ax = fig.add_subplot(211)

cmap = plt.get_cmap("viridis")
colors = [cmap(i) for i in np.linspace(0, 1, len(YEARS))]

for _, row in _df_col1.iterrows():
    color = IMAGE_REGION_COLORS.get(row.values[0], "#000000")
    ax.plot(YEARS, row.values[1:], label=row.values[0], color=color, linewidth=1)

for _, row in _df_col2.iterrows():
    color = IMAGE_REGION_COLORS.get(row.values[0], "#000000")
    ax.plot(YEARS, row.values[1:], label=row.values[0], color=color, linestyle="dashed", linewidth=1)

lgd = ax.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=2, borderaxespad=0.)

ax.set_title(f"In-and-Outflow per region")
ax.set_yscale('log')
ax.grid('on')

ax = fig.add_subplot(212)

for _, row in _df_col3.iterrows():
    color = IMAGE_REGION_COLORS.get(row.values[0], "#000000")
    ax.plot(YEARS, row.values[1:], label=row.values[0], color=color)
ax.set_title(f"Substitution per region")
ax.grid('on')

plt.show()

filename = "figure_test_In-and-Outflow"
filename_format = f"{filename}.{FIGURE_FORMAT}"
file = os.path.join(PATH, filename_format)
fig.savefig(file, bbox_extra_artists=(lgd,), bbox_inches="tight")
