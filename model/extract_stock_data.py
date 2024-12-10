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
from typing import Union
import pandas as pd
import numpy as np
from copy import deepcopy
from time import time

from utils import df_status
from statics import UNIT, IMAGE_REGIONS


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
                           outlfow_conversion_rate: Union[float, dict, int] = 1.0,
                           outlfow_conversion_abs: Union[float, dict, int] = -1.0,
                           inflow_conversion_rate: Union[float, dict, int] = 1.0,
                           key_type: str = "year") -> pd.DataFrame:
    """calculate and add columns for 'aggregate stock', 'recycled inflow'
    
    Calculates how much of old building stock is converted to new recycled 
    inflow. Takes into account stock for unused recycled production. Stock is 
    reset when the 'Region' changes.
    
    Stock is moderated by the outlfow conversion rate (outflow_conversion_rate),
    the absolute production (outflow_conversion_abs) and the inflow conversion rate.
    The outflow conversion rate limits the building outflow as a percentage that
    can be converted (e.g. 0.75 = 75% of buildings can be recycled in a given year).
    The absolute production limits the amount that can be produced (recycled) per
    timestep (e.g. a limit of 10 would mean that no more than 10 (of given unit) can
    be recycled in a given year). If the absolute production is set to -1, it is
    assumed there is no limit, otherwise, the limit is assumed to be the same unit
    as the inflow and outflow columns. The inflow conversion rate is similar to the
    outflow conversion rate, but it moderates how much of the available material
    (from outflow and stock from previous timesteps) can be converted to new
    material, it is moderated as a max percentage of the inflow (demand) (e.g. 0.3
    = 30% of available material can be converted to new material in a given year).

    The conversion factors can be given as a single number (float or int), or as a
    dict with one value per year, region or year/region pair. The key type should be
    given as key_type (year, region or year/region).
    """
    def convert_check_types(variable):
        if not isinstance(variable, (dict, float, int)):
            raise BaseException(f"variable must be of type `dict`, `float` or `int` "
                                f"but type given was {type(variable)}")
        elif isinstance(variable, (float, int)):
            variable = {
                "any": float(variable)
            }
        elif isinstance(variable, dict) and "any" not in variable:
            raise BaseException("if variable is given as dict, it MUST contain 'any'")
        return variable

    df = deepcopy(df)
    available_stock_name = f"available stock ({UNIT})"
    recycled_inflow_name = f"recycled inflow ({UNIT})"
    
    # set in/outflow names correctly
    inflow_col = df.columns[2]  # named 'inflow (kt)'
    outflow_col= df.columns[3]  # named 'outflow (kt)'

    # set conversion rates to correct format
    outlfow_conversion_rate = convert_check_types(outlfow_conversion_rate)
    outlfow_conversion_abs = convert_check_types(outlfow_conversion_abs)
    inflow_conversion_rate = convert_check_types(inflow_conversion_rate)

    # check if conversion rates are possible
    for key, value in outlfow_conversion_rate.items():
        if value > 1 or value < 0:
            raise BaseException(f"conversions rates must be higher or equal to 0 (0%) "
                                f"and lower or equal to 1 (100%), rate is: "
                                f"stock_conversion_rate: {value} for {key}")
    for key, value in outlfow_conversion_abs.items():
        if value < 0 and not value == -1:
            raise BaseException(f"absolute production must be higher or equal to 0 {UNIT} "
                                f"or be set to -1 for no limit: "
                                f"stock_conversion_abs: {value} for {key}")
        elif value == -1:
            # set a -1 rate to infinity
            outlfow_conversion_abs[key] = np.inf

    # check key_type:
    if key_type not in ["year", "region", "year/region", "region/year"]:
        raise BaseException(f"'key_type' should be 'year', 'region' or 'year/region' but got '{key_type}'")

    # create column for stock
    last_row = {col: 0 for col in df.columns}
    last_row[available_stock_name] = 0  # add stock to the dict so it can be used
    
    data = []
    
    for idx, row in df.iterrows():

        # restart stock if the region is different
        if row["Region"] != last_row["Region"]:
            last_row[available_stock_name] = 0

        # set correct key
        if key_type == "year":
            key = row["year"]
        elif key_type == "region":
            key = row["region"]
        else:
            key = f'{row["year"]}/{row["region"]}'
                
        # find available outflow and inflow, moderated by conversions
        ocr = outlfow_conversion_rate.get(key, outlfow_conversion_rate["any"])
        oca = outlfow_conversion_abs.get(key, outlfow_conversion_abs["any"])
        icr = inflow_conversion_rate.get(key, inflow_conversion_rate["any"])

        available_outflow = min(
            ocr * row[outflow_col],
            oca
        )
        max_inflow = min(
            icr * row[inflow_col],
            available_outflow
        )

        # find stock balance for this time period
        balance = (
                available_outflow  # this is supply from recycling
                - row[inflow_col]  # this is demand for new material
        )
        transfer_balance = (
                available_outflow  # this is supply from recycling
                - max_inflow  # this is demand that can be satisfied
        )
        
        # 3 options for recycled inflow and available stock
        if balance > 0:
            # more material is available than consumed
            
            # fulfil complete demand (inflow)
            recycled_inflow = max_inflow
            # add remainder to stock
            available_stock = (last_row[available_stock_name]
                               + transfer_balance)

        elif balance * -1 > last_row[available_stock_name]:
            # there is less material available and stock would be depleted 
            
            # fulfil demand partially
            recycled_inflow = min(available_outflow + last_row[available_stock_name],
                                  max_inflow)
            # deplete stock
            available_stock = 0
            
        else:
            # there is less material available but demand can be completely
            # fulfilled by stock
            
            # fulfil complete demand (inflow)
            recycled_inflow = max_inflow
            # reduce stock
            available_stock = (last_row[available_stock_name]
                               - transfer_balance)

        # calculate substitution rate
        substitution = recycled_inflow / row[inflow_col] if row[inflow_col] != 0 else 0

        # show the last row
        last_row = {
            "Region": row["Region"],  # the region
            "year": row["year"],  # the year
            inflow_col: row[inflow_col],  # how much material goes IN stock (both conventional and recycled)
            outflow_col: row[outflow_col],  # how much material come OUT of stock (available for recycling)
            available_stock_name: available_stock,  # how much material is still available for recycling in later years
            recycled_inflow_name: recycled_inflow,  # how much material goes IN stock from recycling
            "substitution": substitution,  # percentage of substituted stock
        }
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
outlfow_conversion_rate = np.linspace(0, 0.5, 32)
outlfow_conversion_rate = {2020 + i: rate for i, rate in enumerate(outlfow_conversion_rate[1:])}
outlfow_conversion_rate["any"] = 0
# outlfow_conversion_rate = 1  # set if no limit

inflow_conversion_rate = np.linspace(0.5, 0.750, 32)
inflow_conversion_rate = {2020 + i: rate for i, rate in enumerate(inflow_conversion_rate[1:])}
inflow_conversion_rate["any"] = 0.5
# inflow_conversion_rate = 1  # set if no limit

# calculate new stock data
t = time()
df_done = calculate_availability(df_clean, 
                                 outlfow_conversion_rate=outlfow_conversion_rate,
                                 inflow_conversion_rate=inflow_conversion_rate)
print(f"Data converted: {df_status(df_done, time() - t)}")

# export to excel
# df_done.to_excel("filtered_to_list.xlsx", index=False)
df_done.to_csv("filtered_to_list.csv", index=False)
print(f"Exported data | Total time taken: {round(time() - ts, 1)}s")
