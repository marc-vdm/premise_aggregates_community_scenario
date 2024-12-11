# imports
import pandas as pd

from utils import df_status

from statics import UNIT, PREMISE_REGIONS, MARKET_SHARES


# read data
df_orig = pd.read_csv("filtered_to_list.csv")

print(f"Data loaded: {df_status(df_orig)}")

# filter to only scenario data and right region names and drop irrelevant cols
YEARS = [2025, 2030, 2035, 2040, 2045, 2050]

# filter on years
df_clean = df_orig[df_orig["year"].isin(YEARS)]
# rename regions
df_clean = df_clean.replace({"Region": PREMISE_REGIONS})
# drop irrelevant cols
df_clean = df_clean[["Region", "year",
                     f"all sand supply ({UNIT})", f"recycled sand supply ({UNIT})",
                     f"all gravel supply ({UNIT})", f"recycled gravel supply ({UNIT})"]]

print(f"df cleaned: {df_status(df_clean)}")


def reorder(df, scenario, MARKET_SHARES):
    """TODO description"""

    # get the correct market shares from MARKET_SHARES for the share_type (e.g. gravel, round) and region (e.g. BRA)
    # will return dict of source types (variable, e.g. SAND_QUARRY) and amounts as key/values from MARKET_SHARES above
    get_shares = lambda share_type, region: MARKET_SHARES[share_type].get(region, MARKET_SHARES[share_type]["default"])

    def share_per_route(share_type):
        """TODO description:
        Calculate a share per conventional production route
        """

        _data = []

        # infer aggregate type column
        _share_type = share_type.split(",")[0]

        total_conventional = (float(
            row[f"all {_share_type} supply ({UNIT})"])
            - float(row[f"recycled {_share_type} supply ({UNIT})"]))
        for variable, share in get_shares(share_type, row["Region"]).items():
            material = share_type.split(',')[0].capitalize()
            var_name = f"Production|{material}|{variable}"
            _row = {
                "scenario": scenario,
                "region": row["Region"],
                "variables": var_name,
                "unit": UNIT,
                "year": str(row["year"]),
                "amount": total_conventional * share,
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
            "amount": float(row[f"recycled gravel supply ({UNIT})"]),
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
            "amount": float(row[f"recycled sand supply ({UNIT})"]),
        })

        data = data + share_per_route("sand")

    df = pd.DataFrame(data)

    df = df.pivot_table(index=["scenario", "region", "variables", "unit"], columns="year", values="amount").reset_index()

    return df

df_reorder = reorder(df_clean, "SSP2-Base-image", MARKET_SHARES)

print(f"df cleaned: {df_status(df_reorder)}")

df_reorder.to_csv("../scenario_data/scenario_data.csv", index=False)
