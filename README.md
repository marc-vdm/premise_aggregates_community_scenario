## Description
Premise community scenario for production of (recycled) sand and gravel (together aggregates) for concrete production.

## Sourced from publication
Recovering sand and gravel from End-of-Life concrete: The global potential

## Ecoinvent database compatibility
ecoinvent 3.10 cut-off

## IAM scenario compatibility
Compatible with the following IAM scenarios:
* IMAGE SSP2-Base 2025-2050

## How to use it?

```python

    import brightway2 as bw
    from premise import NewDatabase
    from datapackage import Package
    
    
    fp = r"https://raw.githubusercontent.com/marc-vdm/premise_aggregates_community_scenario/main/datapackage.json"
    aggregates = Package(fp)

    external_scenarios = [{"scenario": "SSP2-Base-image", "data": aggregates},]
    
    bw.projects.set_current("your_bw_project")
    
    ndb = NewDatabase(
            scenarios = [
                {"model":"image", "pathway":"SSP2-Base", "year":2050, "external scenarios": external_scenarios}},
            ],        
            source_db="ecoinvent 3.10 cutoff",
            source_version="3.10",
            key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
        )
    
    ndb.update("external") # or ndb.update() to include the IAM scenario and the external one
```
