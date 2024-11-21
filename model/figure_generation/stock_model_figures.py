from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

REGION_COLORS = {
    # IMAGE regions: https://web.archive.org/web/20231128100726/https://models.pbl.nl/image/index.php/Region_classification_map
    "Canada": "#c6e3f9",
    "USA": "#47afe8",
    "Mexico": "#006e9a",
    "Central America": "#656916",
    "Brazil": "#989a34",
    "Rest of South America": "#c3c386",
    "Northern Africa": "#ac4a7f",
    "Western Africa": "#be789e",
    "Eastern Africa": "#debed1",
    "South Africa": "#6f0045",
    "Western Europe": "#e7d9b5",
    "Central Europe": "#C8AB5B",
    "Turkey": "#997C6C",
    "Ukraine region": "#684132",
    "Central Asia": "#492B66",
    "Russia region": "#CCC5DA",
    "Middle East": "#776290",
    "India": "#CB8517",
    "Korea region": "#8FBA5F",
    "China region": "#D8E5C5",
    "Southeastern Asia": "#FFF6A9",
    "Indonesia region": "#FFEE31",
    "Japan": "#21803D",
    "Oceania": "#91A18B",
    "Rest of South Asia": "#F2CD2E",
    "Rest of Southern Africa": "#9D0063",
    }

UNIT = "kt"


df = pd.read_csv("../filtered_to_list.csv")

YEARS = [y for y in range(2020, 2051)]

# # filter on years
df = df[df["year"].isin(YEARS)]

def plot_col(df, col_name):

    _df = df.pivot_table(index=["Region"], columns="year", values=[col_name]).reset_index()

    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    for _, row in _df.iterrows():

        color = REGION_COLORS.get(row.values[0], "#000000")
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
        color = REGION_COLORS.get(row.values[0], "#000000")
        ax.plot(YEARS, row.values[1:], label=row.values[0], color=color)

    for _, row in _df_col2.iterrows():
        color = REGION_COLORS.get(row.values[0], "#000000")
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
    color = REGION_COLORS.get(row.values[0], "#000000")
    ax.plot(YEARS, row.values[1:], label=row.values[0], color=color, linewidth=1)

for _, row in _df_col2.iterrows():
    color = REGION_COLORS.get(row.values[0], "#000000")
    ax.plot(YEARS, row.values[1:], label=row.values[0], color=color, linestyle="dashed", linewidth=1)

lgd = ax.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=2, borderaxespad=0.)

ax.set_title(f"In-and-Outflow per region")
ax.set_yscale('log')
ax.grid('on')

ax = fig.add_subplot(212)

for _, row in _df_col3.iterrows():
    color = REGION_COLORS.get(row.values[0], "#000000")
    ax.plot(YEARS, row.values[1:], label=row.values[0], color=color)
ax.set_title(f"Substitution per region")
ax.grid('on')

plt.show()

# fig.savefig(f"../figure_test_In-and-Outflow.svg", bbox_extra_artists=(lgd,), bbox_inches='tight')