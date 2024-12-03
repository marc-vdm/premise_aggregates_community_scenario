# imports
import pandas as pd

from utils import df_status, UNIT

REGIONS = {
    # IMAGE regions: https://web.archive.org/web/20231128100726/https://models.pbl.nl/image/index.php/Region_classification_map
    # PREMISE region mapping: https://github.com/polca/premise/blob/master/premise/iam_variables_mapping/topologies/image-topology.json
    "Canada": "CAN",
    "USA": "USA",
    "Mexico": "MEX",
    "Central America": "RCAM",
    "Brazil": "BRA",
    "Rest of South America": "RSAM",
    "Northern Africa": "NAF",
    "Western Africa": "WAF",
    "Eastern Africa": "EAF",
    "South Africa": "SAF",
    "Western Europe": "WEU",
    "Central Europe": "CEU",
    "Turkey": "TUR",
    "Ukraine region": "UKR",
    "Central Asia": "STAN",
    "Russia region": "RUS",
    "Middle East": "ME",
    "India": "INDIA",
    "Korea region": "KOR",
    "China region": "CHN",
    "Southeastern Asia": "SEAS",
    "Indonesia region": "INDO",
    "Japan": "JAP",
    "Oceania": "OCE",
    "Rest of South Asia": "RSAS",
    "Rest of Southern Africa": "RSAF",
    }

# read data
df_orig = pd.read_csv("filtered_to_list.csv")

print(f"Data loaded: {df_status(df_orig)}")

# filter to only scenario data and right region names and drop irrelevant cols
YEARS = [2020, 2025, 2030, 2035, 2040, 2045, 2050]

# filter on years
df_clean = df_orig[df_orig["year"].isin(YEARS)]
# rename regions
df_clean = df_clean.replace({"Region": REGIONS})
# drop irrelevant cols
df_clean = df_clean[["Region", "year", f"inflow ({UNIT})", f"recycled inflow ({UNIT})"]]

print(f"df cleaned: {df_status(df_clean)}")

SHARES = {
    # market shares of conventional virgin production routes
    # production routes are based on ecoinvent market shares
    "gravel, crushed": {
        "default": {
            "GRAVEL_CRUSHED": 1,
        },
    },
    "gravel, round": {
        "default": {
            "GRAVEL_ROUND": 1,
        },
    },
    "sand": {
        "default": {
            "SAND_QUARRY": 0.707465674107445,
            "SAND_RIVER": 0.292442375462464,
            "SAND_ZINC": 9.19504300903769e-05,
        },
        "BRA": {
            "SAND_RIVER": 0.699973685199805,
            "SAND_PIT": 0.300026314800195,
        },
        "INDIA": {
            "SAND_RIVER": 1,
        },
    },
}

GRAVEL_SAND_SPLIT = {
    "gravel": 0.473833920927938,
    "sand": 0.352537634914311
}  # amounts based on sand/gravel use in 1 kg concrete of average of all ecoinvent concrete products

def reorder(df, scenario, SHARES):
    """TODO description"""

    # get the correct market shares from SHARES for the share_type (e.g. gravel, round) and region (e.g. BRA)
    get_shares = lambda share_type, region: SHARES[share_type].get(region, SHARES[share_type]["default"])

    def share_per_route(share_type):
        """TODO description:
        Calculate a share per virgin production route
        """

        _data = []
        total_virgin = float(row[f"inflow ({UNIT})"]) - float(row[f"recycled inflow ({UNIT})"])
        for variable, share in get_shares(share_type, row["Region"]).items():
            var_name = f"Production|{share_type.split(',')[0].capitalize()}|{variable}"
            _row = {
                "scenario": scenario,
                "region": row["Region"],
                "variables": var_name,
                "unit": UNIT,
                "year": str(row["year"]),
                "amount": total_virgin * share,
            }
            _data.append(_row)
        return _data

    data = []

    for _, row in df.iterrows():

        data.append(
            { # gravel ADR
            "scenario": scenario,
            "region": row["Region"],
            "variables": "Production|Gravel|GRAVEL_ADR",
            "unit": UNIT,
            "year": str(row["year"]),
            "amount": float(row[f"recycled inflow ({UNIT})"]) * GRAVEL_SAND_SPLIT["gravel"],
        })

        data = data + share_per_route("gravel, crushed")
        data = data + share_per_route("gravel, round")

        data.append(
            {  # sand HAS
            "scenario": scenario,
            "region": row["Region"],
            "variables": "Production|Sand|SAND_HAS",
            "unit": UNIT,
            "year": str(row["year"]),
            "amount": float(row[f"recycled inflow ({UNIT})"]) * GRAVEL_SAND_SPLIT["sand"],
        })

        data = data + share_per_route("sand")

    df = pd.DataFrame(data)

    df = df.pivot_table(index=["scenario", "region", "variables", "unit"], columns="year", values="amount").reset_index()

    return df

df_reorder = reorder(df_clean, "SSP2-Base-image", SHARES)

print(f"df cleaned: {df_status(df_reorder)}")

df_reorder.to_csv("../scenario_data/scenario_data.csv", index=False)
