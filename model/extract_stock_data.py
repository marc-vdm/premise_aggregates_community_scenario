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
import pandas as pd
import numpy as np
from copy import deepcopy

from utils import df_status, UNIT

# global variables:
REGIONS = {
    # IMAGE regions: https://web.archive.org/web/20181231082909/https://models.pbl.nl/image/index.php/Region_classification_map
    1:  "Canada",
    2:  "USA",
    3:  "Mexico",
    4:  "Central America",
    5:  "Brazil",
    6:  "Rest of South America",
    7:  "Northern Africa",
    8:  "Western Africa",
    9:  "Eastern Africa",
    10: "South Africa",
    11: "Western Europe",
    12: "Central Europe",
    13: "Turkey",
    14: "Ukraine region",
    15: "Central Asia",
    16: "Russia region",
    17: "Middle East",
    18: "India",
    19: "Korea region",
    20: "China region",
    21: "Southeastern Asia",
    22: "Indonesia region",
    23: "Japan",
    24: "Oceania",
    25: "Rest of South Asia",
    26: "Rest of Southern Africa",
    }

def clean_and_reorganize(df: pd.DataFrame, 
                         prints: str ="end") -> pd.DataFrame:
    """remove un-needed data and reorganize format.
    
    output format is a list with columns: Region, year, inflow and outflow
    
    prints is optional variable for printing convenience data, options are 
    - all (print every step)
    - end (print only final result)
    - anything else (don't print)
    """
    
    # drop all "material" that are not "concrete"
    df = df.loc[df["material"] == "concrete"]
    if prints == "all":
        print(f"Filtered to only 'concrete' material flows: {df_status(df)}")
    
    # drop all "flow" that are not "stock"
    df = df.loc[df["flow"] != "stock"]
    if prints == "all":
        print(f"Filtered to only non-'stock' material flows: {df_status(df)}")

    # write correct region names from region codes
    df["Region"] = df["Region"].apply(lambda x: REGIONS[x])
    
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
        print(f"Cleaned and reorganized: {df_status(df)}")
        
    # finally, convert the unit type of column 'year' to int
    df.astype({"year": "int32"}).dtypes
    
    return df


def calculate_availability(df: pd.DataFrame, 
                           stock_conversion_rate: float = 1.0,
                           stock_conversion_abs: float = -1) -> pd.DataFrame:
    """calculate and add columns for 'aggregate stock', 'recycled inflow'
    
    Calculates how much of old building stock is converted to new recycled 
    inflow. Takes into account stock for unused recycled production. Stock is 
    reset when the 'Region' changes.
    
    Stock is moderated by the conversion rate (stock_conversion_rate) and the 
    absolute production (stock_conversion_abs). The conversion rate limits the
    building outflow as a percentage that can be converted (e.g. 0.75 = 75% of
    buildings can be recycled in a given year). The absolute production limits
    the amount that can be produced (recycled) per timestep (e.g. a limit of 10
    would mean that no more than 10 (of given unit) can be recycled in a given
    year). If the absolute production is set to -1, it is assumed there is no
    limit, otherwise, the limit is assumed to be the same unit as the inflow and
    outflow columns.
    """
    
    df = deepcopy(df)
    available_stock_name = f"available stock ({UNIT})"
    recycled_inflow_name = f"recycled inflow ({UNIT})"
    
    # set in/outflow names correctly
    inflow_col = df.columns[2]
    outflow_col= df.columns[3]
    
    # check if conversion rates are possible
    if stock_conversion_rate > 1 or stock_conversion_rate <= 0:
        raise BaseException(f"conversions rates must be higher than 0 (0%) "
                            f"and lower or equal to 1 (100%), rate is: "
                            f"stock_conversion_rate: {stock_conversion_rate}")
    if stock_conversion_abs <= 0 and not stock_conversion_abs == -1:
        raise BaseException(f"absolute production must be higher than 0 {UNIT} "
                            f"or be set to -1 for no limit: "
                            f"stock_conversion_abs: {stock_conversion_abs}")
    elif stock_conversion_abs == -1:
        # set a -1 rate to infinity
        stock_conversion_abs = np.inf
    
    # create column for stock
    last_row = {col: 0 for col in df.columns}
    last_row[available_stock_name] = 0  # add stock to the dict so it can be used
    
    data = []
    
    for idx, row in df.iterrows():

        # restart stock if the region is different
        if row["Region"] != last_row["Region"]:
            last_row[available_stock_name] = 0
                
        # find available outflow, moderated by conversions
        available_outflow = min(
            stock_conversion_rate * row[outflow_col],
            stock_conversion_abs
        )
        # find stock balance for this time period
        balance = (
                available_outflow -  # this is supply from recycling
                row[inflow_col]  # this is demand from recycling
        )
        
        # 3 options for recycled inflow and available stock
        if balance > 0:
            # more material is available than consumed
            
            # fulfil complete demand (inflow)
            recycled_inflow = row[inflow_col]
            # add remainder to stock
            available_stock = (last_row[available_stock_name]
                               + balance)

        elif balance * -1 > last_row[available_stock_name]:
            # there is less material available and stock would be depleted 
            
            # fulfil demand partially
            recycled_inflow = (available_outflow 
                               + last_row[available_stock_name])
            # deplete stock
            available_stock = 0
            
        else:
            # there is less material available but demand can be completely
            # fulfilled by stock
            
            # fulfil complete demand (inflow)
            recycled_inflow = row[inflow_col]
            # reduce stock
            available_stock = (last_row[available_stock_name]
                               + balance)

        # show the last row
        last_row = {
            "Region": row["Region"],
            "year": row["year"],
            inflow_col: row[inflow_col],
            outflow_col: row[outflow_col],
            available_stock_name: available_stock,
            recycled_inflow_name: recycled_inflow,
        }
        data.append(last_row)
    
    df = pd.DataFrame(data)
    return df
        

# read data
# Original file is from Deetman et al. (2020): https://github.com/SPDeetman/BUMA
# in the folder 'output'
df_orig = pd.read_excel("Supplementary Data (Original model).xlsx",
                   sheet_name="material_output")
print(f"Data loaded: {df_status(df_orig)}")

# clean data
df_clean = clean_and_reorganize(df_orig)

# calculate new stock data
df_done = calculate_availability(df_clean, 
                                 stock_conversion_rate=0.95,
                                 stock_conversion_abs=-1)
print(f"Data converted: {df_status(df_done)}")

# export to excel
# df_done.to_excel("filtered_to_list.xlsx", index=False)
df_done.to_csv("filtered_to_list.csv", index=False)
print("Exported data")
