# -*- coding: utf-8 -*-
"""
Created on Mon May 27 10:46:23 2024

@author: meidemtvander
"""

"""
Goal: Find concrete stock outflow and assess how much can be recycled to new concrete
This script takes data from Deetman et al. (2020) and adds new data for every region:
- one column for supply from recycling
- one column for available stock (outflow that wasn't used immediately)

references:
Deetman et al. 2020: https://doi.org/10.1016/j.jclepro.2019.118658
"""

# imports
from typing import Union, Tuple
import pandas as pd
import numpy as np
from copy import deepcopy
from time import time

from utils import df_status
from statics import UNIT, IMAGE_REGIONS, GRAVEL_SAND_PROD_SPLIT, GRAVEL_SAND_USE_SPLIT


def clean_and_reorganize(df: pd.DataFrame, 
                         prints: str ="end") -> pd.DataFrame:
    """remove un-needed data and reorganize format.
    
    output format is a list with columns: Region, year, inflow and outflow
    
    prints is optional variable for printing convenience data, options are 
    - all (print every step)
    - end (print only final result)
    - anything else (don't print)
    """

    t = time()

    # drop all "material" that are not "concrete"
    df = df.loc[df["material"] == "concrete"]
    if prints == "all":
        print(f"Filtered to only 'concrete' material flows: {df_status(df)}")
    
    # drop all "flow" that are not "stock"
    df = df.loc[df["flow"] != "stock"]
    if prints == "all":
        print(f"Filtered to only non-'stock' material flows: {df_status(df)}")

    # write correct region names from region codes
    df["Region"] = df["Region"].apply(lambda x: IMAGE_REGIONS[x])
    
    # merge all "type" and "area" for given "Region" and "flow"
    df = df.drop(columns=["type", "area", "material"])
    df = df.groupby(["Region", "flow"]).sum().reset_index()
    if prints == "all":
        print(f"Grouped flows with same 'type' and 'area': {df_status(df)}")
    
    # transform from table to list 
    df = df.melt(id_vars=["Region", "flow"], var_name="year", value_name=f"amount ({UNIT})")
    df = df.pivot(index=["Region", "year"], columns="flow", values=f"amount ({UNIT})").reset_index()
    df.columns.name = None
    df.rename(columns={"inflow": f"inflow ({UNIT})", "outflow": f"outflow ({UNIT})"}, inplace=True)
    if prints == "all":
        print(f"Converted to list: {df_status(df)}")
    elif prints == "end":
        print(f"Cleaned and reorganized: {df_status(df, time() - t)}")
        
    # finally, convert the unit type of column 'year' to int
    df.astype({"year": "int32"}).dtypes
    
    return df


def calculate_availability(df: pd.DataFrame,
                           outflow_conversion_rate: Union[dict, float, int] = 1.0,
                           inflow_conversion_rate: Union[dict, float, int] = 1.0,
                           key_type: str = "year") -> pd.DataFrame:
    """calculate and add columns for sand and gravel supply and stock

    Calculates how much of old building stock is converted to new recycled
    inflow. Takes into account stock for unused recycled production. Stock is
    reset when the 'Region' changes.

    Stock is moderated by the outflow conversion rate (outflow_conversion_rate)
    and the inflow conversion rate.
    The outflow conversion rate limits the building outflow as a percentage that
    can be converted (e.g. 0.75 = 75% of buildings can be recycled in a given year).
    The inflow conversion rate is similar to the outflow conversion rate, but it
    moderates how much of the available material (from outflow and stock from
    previous timesteps) can be converted to new material, it is moderated as a max
    percentage of the inflow (demand) (e.g. 0.3 = 30% of available material can be
    converted to new material in a given year).

    The conversion factors can be given as a single number (float or int), or as a
    dict with one value per year, region or year/region pair. The key type should be
    given as key_type (year, region or year/region).
    """

    def convert_check_types(variable: Union[float, int, dict], var_name: str) -> dict:
        """Ensure that variables are in correct format and possible"""

        # ensure format
        if isinstance(variable, (float, int)):
            variable = {
                "any": float(variable)
            }
        elif isinstance(variable, dict):
            if "any" not in variable.keys():
                raise BaseException(f"Variable '{var_name}' is given as dict, it MUST contain 'any' as key")
        else:
            raise BaseException(f"variable must be of type `dict`, `float` or `int` "
                                f"but type for '{var_name}' given was {type(variable)}")

        # ensure rates are possible
        for key, value in variable.items():
            if value > 1 or value < 0:
                raise BaseException(f"Conversions rates must be higher or equal to 0 (0%) "
                                    f"and lower or equal to 1 (100%), rate is: "
                                    f"{var_name}: {key} for {value}")
        return variable

    def balance_check(balance, max_demand, max_rec_supply, stock) -> Tuple[float, float]:
        """calculate supply from recycled sources based on max supply and existing material stock."""
        # 3 options for balance
        if balance > 0:
            # more material is available than consumed

            # fulfil complete demand (inflow)
            rec_supply = max_demand
            # add remainder to stock
            stock = (stock
                     + balance)
        elif (balance * -1) > stock:
            # there is less material available and not enough stock to supply full demand

            # fulfil maximum possible demand
            rec_supply = max_rec_supply + stock
            # deplete stock
            stock = 0
        else:
            # there is less material available but demand can be completely fulfilled by supply + stock

            # fulfil complete demand
            rec_supply = max_demand
            # adjust stock to new level (note that balance is negative so add to avoid double negative)
            stock = stock + balance

        return rec_supply, stock

    df = deepcopy(df)
    df = df.sort_values(["Region", "year"], ascending=True)  # ensure the data is sorted as expected

    sand_stock_name = f"sand stock ({UNIT})"
    gravel_stock_name = f"gravel stock ({UNIT})"

    # set in/outflow names correctly
    inflow_col = df.columns[2]  # named 'inflow ({UNIT})'
    outflow_col = df.columns[3]  # named 'outflow ({UNIT})'

    # set conversion rates to correct format
    outflow_conversion_rate = convert_check_types(outflow_conversion_rate, "outflow_conversion_rate")
    inflow_conversion_rate = convert_check_types(inflow_conversion_rate, "inflow_conversion_rate")

    # check key_type:
    if key_type not in ["year", "region", "year/region", "region/year"]:
        raise BaseException(f"'key_type' should be 'year', 'region' or 'year/region' but got '{key_type}'")

    # create columns for stock of sand and gravel
    last_row = {col: 0 for col in df.columns}
    last_row[sand_stock_name] = 0  # add stock to the dict so it can be used
    last_row[gravel_stock_name] = 0

    data = []

    # do the actual stock calculations, going over each region and time step
    for idx, row in df.iterrows():

        if row["Region"] != last_row["Region"]:
            # reset stock if we start on a new region
            last_row[sand_stock_name] = 0
            last_row[gravel_stock_name] = 0

        # set correct key
        if key_type == "year":
            key = row["year"]
        elif key_type == "region":
            key = row["region"]
        else:
            key = f'{row["year"]}/{row["region"]}'

        # find available outflow and inflow, moderated by conversions
        ocr = outflow_conversion_rate.get(key, outflow_conversion_rate["any"])
        icr = inflow_conversion_rate.get(key, inflow_conversion_rate["any"])

        # maximum recycled aggregate availability from eol concrete
        available_rec_sand = row[outflow_col] * ocr * GRAVEL_SAND_PROD_SPLIT["sand"]
        available_rec_gravel = row[outflow_col] * ocr * GRAVEL_SAND_PROD_SPLIT["gravel"]

        # total aggregate demand for new building stock
        all_sand_demand = row[inflow_col] * GRAVEL_SAND_USE_SPLIT["sand"]
        all_gravel_demand = row[inflow_col] * GRAVEL_SAND_USE_SPLIT["gravel"]

        # recycled aggregate supply
        rec_sand_supply = min(
            all_sand_demand * icr,
            available_rec_sand
        )
        rec_gravel_supply = min(
            all_gravel_demand * icr,
            available_rec_gravel
        )

        # aggregates stock balance
        sand_balance = (
            available_rec_sand
            - all_sand_demand
        )
        gravel_balance = (
                available_rec_gravel
                - all_gravel_demand
        )

        rec_sand_supply, sand_stock = balance_check(sand_balance,
                                                    all_sand_demand,
                                                    rec_sand_supply,
                                                    last_row[sand_stock_name])
        rec_gravel_supply, gravel_stock = balance_check(gravel_balance,
                                                        all_gravel_demand,
                                                        rec_gravel_supply,
                                                        last_row[gravel_stock_name])

        # calculate substitution rates
        sand_substitution = rec_sand_supply / all_sand_demand if all_sand_demand != 0 else 0
        gravel_substitution = rec_gravel_supply / all_gravel_demand if all_gravel_demand != 0 else 0

        # make new last row
        last_row = {
            "Region": row["Region"],  # the region
            "year": row["year"],  # the year
            inflow_col: row[inflow_col],  # how much material goes IN stock
            outflow_col: row[outflow_col],  # how much material come OUT of stock (available for recycling)
            f"all sand supply ({UNIT})": all_sand_demand,  # how much sand is required for inflow
            f"recycled sand supply ({UNIT})": rec_sand_supply,  # how much sand is supplied from recycling
            f"sand stock ({UNIT})": sand_stock,  # how much sand stock there is
            f"sand substitution": sand_substitution,  # how much sand is substituted
            f"all gravel supply ({UNIT})": all_gravel_demand,  # how much gravel is required for inflow
            f"recycled gravel supply ({UNIT})": rec_gravel_supply,  # how much gravel is supplied from recycling
            f"gravel stock ({UNIT})": gravel_stock,  # how much gravel stock there is
            f"gravel substitution": gravel_substitution,  # how much gravel is substituted
        }

        # build rows for dataframe
        data.append(last_row)

    df = pd.DataFrame(data)
    return df

# read data
# Original file is from Deetman et al. (2020): https://github.com/SPDeetman/BUMA
# in the folder 'output'
ts = time()
df_orig = pd.read_excel("Supplementary Data (Original model).xlsx",
                   sheet_name="material_output")
print(f"Data loaded: {df_status(df_orig, time() - ts)}")

# clean data
df_clean = clean_and_reorganize(df_orig)

# generate conversion rate per year

# linspace explanation:
# first number is lower rate, second higher, last the steps
# steps is 32, first step is lowest number (but we want 1 higher)
# the first is deleted, the 31 remaining are 2020-2050

# assume 5% of building stock outflow can never be recycled
outflow_conversion_rate = 0.95

# assume market share of 0% to (max) 50% growing between 2025-2050
inflow_conversion_rate = np.linspace(0, 0.5, (2050 - 2025 + 2))
inflow_conversion_rate = {2025 + i: rate for i, rate in enumerate(inflow_conversion_rate[1:])}
inflow_conversion_rate["any"] = 0
# inflow_conversion_rate = 1  # set if no limit

# calculate new stock data
t = time()
df_done = calculate_availability(df_clean,
                                 outflow_conversion_rate=outflow_conversion_rate,
                                 inflow_conversion_rate=inflow_conversion_rate)
print(f"Data converted: {df_status(df_done, time() - t)}")

# export to excel
# df_done.to_excel("filtered_to_list.xlsx", index=False)
df_done.to_csv("filtered_to_list.csv", index=False)
print(f"Exported data | Total time taken: {round(time() - ts, 1)}s")
