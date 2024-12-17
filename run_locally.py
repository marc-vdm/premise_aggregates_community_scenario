from premise import NewDatabase
from datapackage import Package
import bw2data as bd

#project
PROJECT = "premise_aggregates"
bd.projects.set_current(PROJECT)

# database settings
SOURCE_DB = "ecoinvent-3.10.1-cutoff"
# SOURCE_DB = "premise_superstructure"
SOURCE_V = "3.10"
NEW_DB_NAME = "premise_aggregates"
# NEW_DB_NAME = "test"

# key
with open("./key.txt", "r") as f:
    KEY = f.readline()

# get external data
fp = r"./datapackage.json"
aggregates = Package(fp)

# set scenarios
SCENARIOS = [
    {"model": "image", "pathway": "SSP2-Base", "year": 2025, "external scenarios":
        [{"scenario": "SSP2-Base-image", "data": aggregates}]
     },
    {"model": "image", "pathway": "SSP2-Base", "year": 2030, "external scenarios":
        [{"scenario": "SSP2-Base-image", "data": aggregates}]
     },
    {"model": "image", "pathway": "SSP2-Base", "year": 2035, "external scenarios":
        [{"scenario": "SSP2-Base-image", "data": aggregates}]
     },
    {"model": "image", "pathway": "SSP2-Base", "year": 2040, "external scenarios":
        [{"scenario": "SSP2-Base-image", "data": aggregates}]
     },
    {"model": "image", "pathway": "SSP2-Base", "year": 2045, "external scenarios":
        [{"scenario": "SSP2-Base-image", "data": aggregates}]
     },
    {"model": "image", "pathway": "SSP2-Base", "year": 2050, "external scenarios":
        [{"scenario": "SSP2-Base-image", "data": aggregates}]
     },
]

# set sectors to change
SECTORS = [
    "biomass",
    "battery",
    "electricity",
    "cement",
    "steel",
    "dac",
    "fuels",
    "heat",
    "emissions",
    "two_wheelers",
    "cars",
    "trucks",
    "buses",
    "trains",
    "external",
]

# create new database
ndb = NewDatabase(
    scenarios=SCENARIOS,
    source_db=SOURCE_DB,
    source_version=SOURCE_V,
    key=KEY,
    keep_source_db_uncertainty=True,
    keep_imports_uncertainty=True,
    use_absolute_efficiency=True,
    use_cached_inventories=False,
    )

# update sectors
ndb.update(SECTORS)

# write to BW a superstructure
ndb.write_superstructure_db_to_brightway(NEW_DB_NAME)

# # write to BW db
# names = [f"{NEW_DB_NAME} - {scenario['year']}" for scenario in SCENARIOS]
# ndb.write_db_to_brightway(names)
