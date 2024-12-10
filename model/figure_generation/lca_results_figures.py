from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

import os

REGION_COLORS = {
    # IMAGE regions: https://web.archive.org/web/20231128100726/https://models.pbl.nl/image/index.php/Region_classification_map
    "CAN": "#c6e3f9",
    "USA": "#47afe8",
    "MEX": "#006e9a",
    "RCAM": "#656916",
    "BRA": "#989a34",
    "RSAM": "#c3c386",
    "NAF": "#ac4a7f",
    "WAF": "#be789e",
    "EAF": "#debed1",
    "SAF": "#6f0045",
    "WEU": "#e7d9b5",
    "CEU": "#C8AB5B",
    "TUR": "#997C6C",
    "UKR": "#684132",
    "STAN": "#492B66",
    "RUS": "#CCC5DA",
    "ME": "#776290",
    "INDIA": "#CB8517",
    "KOR": "#8FBA5F",
    "CHN": "#D8E5C5",
    "SEAS": "#FFF6A9",
    "INDO": "#FFEE31",
    "JAP": "#21803D",
    "OCE": "#91A18B",
    "RSAS": "#F2CD2E",
    "RSAF": "#9D0063",
    }

UNIT = "kt"

GRAVEL_SAND_SPLIT = {
        "gravel": 0.473833920927938,
        "sand": 0.352537634914311
    }  # amounts based on sand/gravel use in 1 kg concrete of average of all ecoinvent concrete products

METHODS = [
    "EF v3.1, climate change, global warming potential (GWP100)",
    "EF v3.1, climate change: fossil, global warming potential (GWP100)",
    "EF v3.1, climate change: biogenic, global warming potential (GWP100)",
    "EF v3.1, climate change: land use and land use change, global warming potential (GWP100)",
    "EF v3.1, acidification, accumulated exceedance (AE)",
    "EF v3.1, ecotoxicity: freshwater, comparative toxic unit for ecosystems (CTUe)",
    "EF v3.1, ecotoxicity: freshwater, inorganics, comparative toxic unit for ecosystems (CTUe)",
    "EF v3.1, ecotoxicity: freshwater, organics, comparative toxic unit for ecosystems (CTUe)",
    "EF v3.1, eutrophication: freshwater, fraction of nutrients reaching freshwater end compartment (P)",
    "EF v3.1, eutrophication: marine, fraction of nutrients reaching marine end compartment (N)",
    "EF v3.1, eutrophication: terrestrial, accumulated exceedance (AE)",
    "EF v3.1, human toxicity: carcinogenic, comparative toxic unit for human (CTUh)",
    "EF v3.1, human toxicity: carcinogenic, inorganics, comparative toxic unit for human (CTUh)",
    "EF v3.1, human toxicity: carcinogenic, organics, comparative toxic unit for human (CTUh)",
    "EF v3.1, human toxicity: non-carcinogenic, comparative toxic unit for human (CTUh)",
    "EF v3.1, human toxicity: non-carcinogenic, inorganics, comparative toxic unit for human (CTUh)",
    "EF v3.1, human toxicity: non-carcinogenic, organics, comparative toxic unit for human (CTUh)",
    "EF v3.1, ionising radiation: human health, human exposure efficiency relative to u235",
    "EF v3.1, ozone depletion, ozone depletion potential (ODP)",
    "EF v3.1, particulate matter formation, impact on human health",
    "EF v3.1, photochemical oxidant formation: human health, tropospheric ozone concentration increase",
    "EF v3.1, water use, user deprivation potential (deprivation-weighted water consumption)",
    "EF v3.1, land use, soil quality index",
    "EF v3.1, energy resources: non-renewable, abiotic depletion potential (ADP): fossil fuels",
    "EF v3.1, material resources: metals/minerals, abiotic depletion potential (ADP): elements (ultimate reserves)",
    "Inventory results and indicators, resources, aggregates",
]
METHOD_UNITS = {
    "EF v3.1, climate change, global warming potential (GWP100)": "kg CO2-Eq",
    "EF v3.1, climate change: fossil, global warming potential (GWP100)": "kg CO2-Eq",
    "EF v3.1, climate change: biogenic, global warming potential (GWP100)": "kg CO2-Eq",
    "EF v3.1, climate change: land use and land use change, global warming potential (GWP100)": "kg CO2-Eq",
    "EF v3.1, acidification, accumulated exceedance (AE)": "mol H+-Eq",
    "EF v3.1, ecotoxicity: freshwater, comparative toxic unit for ecosystems (CTUe)": "CTUe",
    "EF v3.1, ecotoxicity: freshwater, inorganics, comparative toxic unit for ecosystems (CTUe)": "CTUe",
    "EF v3.1, ecotoxicity: freshwater, organics, comparative toxic unit for ecosystems (CTUe)": "CTUe",
    "EF v3.1, eutrophication: freshwater, fraction of nutrients reaching freshwater end compartment (P)": "kg P-Eq",
    "EF v3.1, eutrophication: marine, fraction of nutrients reaching marine end compartment (N)": "kg N-Eq",
    "EF v3.1, eutrophication: terrestrial, accumulated exceedance (AE)": "mol N-Eq",
    "EF v3.1, human toxicity: carcinogenic, comparative toxic unit for human (CTUh)": "CTUh",
    "EF v3.1, human toxicity: carcinogenic, inorganics, comparative toxic unit for human (CTUh)": "CTUh",
    "EF v3.1, human toxicity: carcinogenic, organics, comparative toxic unit for human (CTUh)": "CTUh",
    "EF v3.1, human toxicity: non-carcinogenic, comparative toxic unit for human (CTUh)": "CTUh",
    "EF v3.1, human toxicity: non-carcinogenic, inorganics, comparative toxic unit for human (CTUh)": "CTUh",
    "EF v3.1, human toxicity: non-carcinogenic, organics, comparative toxic unit for human (CTUh)": "CTUh",
    "EF v3.1, ionising radiation: human health, human exposure efficiency relative to u235": "kBq U235-Eq",
    "EF v3.1, ozone depletion, ozone depletion potential (ODP)": "kg CFC-11-Eq",
    "EF v3.1, particulate matter formation, impact on human health": "disease incidence",
    "EF v3.1, photochemical oxidant formation: human health, tropospheric ozone concentration increase": "kg NMVOC-Eq",
    "EF v3.1, water use, user deprivation potential (deprivation-weighted water consumption)": "m3 world Eq deprived",
    "EF v3.1, land use, soil quality index": "dimensionless",
    "EF v3.1, energy resources: non-renewable, abiotic depletion potential (ADP): fossil fuels": "MJ, net calorific value",
    "EF v3.1, material resources: metals/minerals, abiotic depletion potential (ADP): elements (ultimate reserves)": "kg Sb-Eq",
    "Inventory results and indicators, resources, aggregates": "kg",
}

PATH = "./"
FIGURE_FORMAT = ".png"

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


gravel_df = overall_scores_to_df(os.path.join("..", "..", "lca_results", "gravel", "overall.xlsx"))

sand_df = overall_scores_to_df(os.path.join("..", "..", "lca_results", "sand", "overall.xlsx"))

def combine_aggregates(dfg, dfs):
    """Combine gravel and sand into two dataframes for recycled and conventional aggregates needed for 1kg concrete."""
    # split into recycled/conventional and multiply with gravel/sand proportion in 1kg concrete
    # recycled
    dfgr = dfg[dfg.index.get_level_values("reference product") == "gravel, recycled"] * GRAVEL_SAND_SPLIT["gravel"]
    dfsr = dfs[dfs.index.get_level_values("reference product") == "sand, recycled"] * GRAVEL_SAND_SPLIT["sand"]
    # conventional
    dfgc = dfg[dfg.index.get_level_values("reference product") != "gravel, recycled"] * (GRAVEL_SAND_SPLIT["gravel"] / 2)
    dfsc = dfs[dfs.index.get_level_values("reference product") == "sand"] * GRAVEL_SAND_SPLIT["sand"]

    # combine into recycled group by region
    dfr = pd.concat([dfsr, dfgr])
    dfr = dfr.groupby(level="location").sum()

    # combine into conventional group by region
    dfc = pd.concat([dfsc, dfgc])
    dfc = dfc.groupby(level="location").sum()

    return dfr, dfc

recycled_df, conventional_df = combine_aggregates(gravel_df, sand_df)

def plot_method(dfs, line_styles, method):

    methods = list(set(dfs[0].columns.get_level_values("method")))  # extract all methods

    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    for _df, line_style in zip(dfs, line_styles):
        df = _df.T[_df.columns.get_level_values("method") == method].T
        cols = df.columns.get_level_values("scenario")
        cols = [col.split(" - ")[2] for col in cols]
        df.columns = cols

        for row_name, row in df.iterrows():
            color = REGION_COLORS.get(row_name, "#000000")
            ax.plot(cols, row.values, label=row_name, color=color, linestyle=line_style)

    lgd = ax.legend(bbox_to_anchor=(1.01, 1), loc=2, ncol=2, borderaxespad=0.)

    ax.set_title(f"{method}")
    ax.grid('on')

    plt.show()


for method in METHODS:
    plot_method([recycled_df, conventional_df], line_styles=["solid", "dashed"], method=method)

#TODO
# 1 multiplied with demand recy/conventional
# 2 above with max recycling, >25%, no recycling (world only?) to show differences
# 3 above for concrete impact


print("")

