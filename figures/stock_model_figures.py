from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

import os

from model.statics import UNIT, IMAGE_REGION_COLORS

IMPORT_PATH = os.path.join(*[os.getcwd(), "..", "model"])
EXPORT_PATH = os.path.join(*[os.getcwd(), "stock_model_figures"])

FIGURE_FORMAT = "png"

YEARS = [y for y in range(2025, 2051)]

df_model = pd.read_csv(os.path.join(*[IMPORT_PATH, "filtered_to_list.csv"]))
df_model = df_model[df_model["year"].isin(YEARS)]  # filter on years
df_no_limit = pd.read_csv(os.path.join(*[IMPORT_PATH, "filtered_to_list_no_limits.csv"]))
df_no_limit = df_no_limit[df_no_limit["year"].isin(YEARS)]  # filter on years

# combine sand and gravel for single aggregate in/outflow and substitution

def get_substitution(df: pd.DataFrame) -> pd.DataFrame:
    substitution = []
    for idx, row in df.iterrows():
        recycled_agg = row[f"recycled sand supply ({UNIT})"] + row[f"recycled gravel supply ({UNIT})"]
        weighted_substitution = (
            (row["sand substitution"] * (row[f"recycled sand supply ({UNIT})"] / recycled_agg))
            + (row["gravel substitution"] * (row[f"recycled gravel supply ({UNIT})"] / recycled_agg))
        )
        substitution.append(weighted_substitution)

    df["substitution"] = substitution
    return df

df_model = get_substitution(df_model)
df_no_limit = get_substitution(df_no_limit)

substitution_column = "substitution"

df_sand_model = df_model.pivot_table(index=["Region"], columns="year", values=["sand substitution"]).reset_index()
df_sand_no_limit = df_no_limit.pivot_table(index=["Region"], columns="year", values=["sand substitution"]).reset_index()
df_gravel_model = df_model.pivot_table(index=["Region"], columns="year", values=["gravel substitution"]).reset_index()
df_gravel_no_limit = df_no_limit.pivot_table(index=["Region"], columns="year", values=["gravel substitution"]).reset_index()

def add_ax(ax, df, title, legend=False):
    for _, row in df.iterrows():
        color = IMAGE_REGION_COLORS.get(row.values[0], "#000000")
        ax.plot(YEARS, row.values[1:], label=row.values[0], color=color, linewidth=1)

    ax.set_title(title)
    ax.grid('on')

    if legend:
        return ax.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=2, borderaxespad=0.)

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2, sharex=True, sharey=True)
add_ax(ax1, df_sand_model, "A: sand substitution")
lgd = add_ax(ax2, df_gravel_model, "B: gravel substitution", legend=True)
add_ax(ax3, df_sand_no_limit, "C: maximum sand substitution")
add_ax(ax4, df_gravel_no_limit, "D: maximum gravel substitution")

plt.show()

filename = "substitution_rates"
filename_format = f"{filename}.{FIGURE_FORMAT}"
file = os.path.join(EXPORT_PATH, filename_format)
fig.savefig(file, bbox_extra_artists=(lgd,), bbox_inches="tight")
