def df_status(df) -> dict:
    """Return some info from the df in a dict """
    status = {
        "shape": df.shape
        }
    return status

# global unit
UNIT = "kt"  # unit of flows