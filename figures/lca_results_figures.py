from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

import os

from model.statics import UNIT, PREMISE_REGION_COLORS, GRAVEL_SAND_USE_SPLIT, METHODS, METHOD_SAFE_NAME

IMPORT_PATH_LCA = os.path.join(*[os.getcwd(), "..", "lca_results"])
IMPORT_PATH_SCENARIO = os.path.join(*[os.getcwd(), "..", "scenario_data", "scenario_data.csv"])
EXPORT_PATH = os.path.join(*[os.getcwd(), "lca_results_figures"])

FIGURE_FORMAT = "png"

def overall_scores_to_df(path: str) -> pd.DataFrame:

    # read data from disk
    _df = pd.read_excel(path, index_col=0, header=[0, 1], skiprows=[2])

    # create multiindex from single index
    new_index = []
    for row in _df.index.to_list():
        row = row.replace("\n", " ")
        row = row.replace("COMPARE", "")
        items = [item.strip(" ,") for item in row.split("|")]
        new_index.append((items[0], items[2]))  # reference product, activity name, location

    new_index = pd.MultiIndex.from_tuples(new_index, names=["reference product", "location"])
    return pd.DataFrame(data=_df.values, index=new_index, columns=_df.columns)


gravel_df = overall_scores_to_df(os.path.join(*[IMPORT_PATH_LCA, "gravel", "overall.xlsx"]))

sand_df = overall_scores_to_df(os.path.join(*[IMPORT_PATH_LCA, "sand", "overall.xlsx"]))

def combine_aggregates(dfg, dfs):
    """Combine gravel and sand into two dataframes for recycled and conventional aggregates needed for 1kg concrete."""
    # split into recycled/conventional and multiply with gravel/sand proportion in 1kg concrete
    # recycled
    dfgr = dfg[dfg.index.get_level_values("reference product") == "gravel, recycled"] * GRAVEL_SAND_USE_SPLIT["gravel"]
    dfsr = dfs[dfs.index.get_level_values("reference product") == "sand, recycled"] * GRAVEL_SAND_USE_SPLIT["sand"]
    # conventional
    dfgc = dfg[dfg.index.get_level_values("reference product") != "gravel, recycled"] * (GRAVEL_SAND_USE_SPLIT["gravel"] / 2)
    dfsc = dfs[dfs.index.get_level_values("reference product") == "sand"] * GRAVEL_SAND_USE_SPLIT["sand"]

    # combine into recycled group by region
    dfr = pd.concat([dfsr, dfgr])
    dfr = dfr.groupby(level="location").sum()

    # combine into conventional group by region
    dfc = pd.concat([dfsc, dfgc])
    dfc = dfc.groupby(level="location").sum()

    return dfr, dfc

recycled_df, conventional_df = combine_aggregates(gravel_df, sand_df)

def plot_method(dfs, line_styles, method, prepend="", append="", export=False):

    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    for _df, line_style in zip(dfs, line_styles):
        df = _df.T[_df.columns.get_level_values("method") == method].T
        years = [col.split(" - ")[2] for col in df.columns.get_level_values("scenario")]  # extract only the year
        df.columns = years

        for region, row in df.iterrows():
            color = PREMISE_REGION_COLORS.get(region, "#000000")
            ax.plot(years, row.values, label=region, color=color, linestyle=line_style)

    lgd = ax.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=2, borderaxespad=0.)

    title = f"{prepend} {METHOD_SAFE_NAME[method]} {append}".strip()
    ax.set_title(title)
    ax.grid('on')

    if export:
        file = os.path.join(EXPORT_PATH, f"{title}.{FIGURE_FORMAT}")
        fig.savefig(file, bbox_extra_artists=(lgd,), bbox_inches="tight")
        fig.clear()
    else:
        plt.show()


# method per 1 kg aggregates
for method in METHODS:
    # pass
    plot_method([recycled_df, conventional_df],
                line_styles=["solid", "dashed"],
                method=method,
                prepend="",
                append="1kg aggregates",
                export=True)

concrete_df = overall_scores_to_df(os.path.join(*[IMPORT_PATH_LCA, "concrete", "overall.xlsx"]))

def get_scenario_df(path):
    df = pd.read_csv(path)
    del df["scenario"], df["unit"]

    # drop 1 gravel type for overcounting
    df = df[df["variables"] != "Production|Gravel|GRAVEL_CRUSHED"]

    variables = []
    for row in df["variables"]:
        if row.split("|")[1] == "Sand" and row.split("_")[1] == "HAS":
            new = "sand, recycled"
        elif row.split("|")[1] == "Sand" and row.split("_")[1] != "HAS":
            new = "sand"
        elif row.split("|")[1] == "Gravel" and row.split("_")[1] == "ADR":
            new = "gravel, recycled"
        elif row.split("|")[1] == "Gravel" and row.split("_")[1] == "CRUSHED":
            new = "gravel, crushed"
        elif row.split("|")[1] == "Gravel" and row.split("_")[1] == "ROUND":
            new = "gravel, round"
        else:
            raise f"ERROR, got '{row}'"
        variables.append(new)
    df["variables"] = variables

    df = df.groupby(by=["region", "variables"], as_index=False).sum()

    return df

def plot_method_demand(dfs, demand, line_styles, method, prepend="", append="", export=False):

    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    for _df, line_style in zip(dfs, line_styles):
        df = _df.T[_df.columns.get_level_values("method") == method].T
        years = [col.split(" - ")[2] for col in df.columns.get_level_values("scenario")]  # extract only the year
        df.columns = years

        for region, row in df.iterrows():
            color = PREMISE_REGION_COLORS.get(region, "#000000")
            ax.plot(years, row.values, label=region, color=color, linestyle=line_style)

    lgd = ax.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=2, borderaxespad=0.)

    title = f"{prepend} {METHOD_SAFE_NAME[method]} {append}".strip()
    ax.set_title(title)
    ax.grid('on')

    if export:
        file = os.path.join(EXPORT_PATH, f"{title}.{FIGURE_FORMAT}")
        fig.savefig(file, bbox_extra_artists=(lgd,), bbox_inches="tight")
        fig.clear()
    else:
        plt.show()


scenario_df = get_scenario_df(IMPORT_PATH_SCENARIO)

# method per full demand
# for method in METHODS:
#     plot_method([recycled_df, conventional_df],
#                 demand=scenario_df,
#                 line_styles=["solid", "dashed"],
#                 method=method,
#                 prepend="",
#                 append="1kg aggregates",
#                 export=True)




#TODO
# 1 multiplied with demand recy/conventional
# 2 above with max recycling, >25%, no recycling (world only?) to show differences
# 3 above for concrete impact



print("")

