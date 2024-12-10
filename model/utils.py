def df_status(df, _t = None
              ) -> dict:
    """Return some info from the df in a dict """
    status = {
        "shape": df.shape,
        }
    if _t:
        status["time taken"] = f"{round(_t, 1)}s"
    return status
