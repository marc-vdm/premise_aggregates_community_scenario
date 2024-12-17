# file for static variables required in multiple files
UNIT = "kt"

IMAGE_REGIONS = {
    # Mapping IMAGE region number (key) to IMAGE region name (value)
    # IMAGE regions: https://web.archive.org/web/20231128100726/https://models.pbl.nl/image/index.php/Region_classification_map
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

IMAGE_REGION_COLORS = {
    # Mapping IMAGE region name (key) to region color (value)
    # IMAGE regions: https://web.archive.org/web/20231128100726/https://models.pbl.nl/image/index.php/Region_classification_map
    "Canada": "#c6e3f9",
    "USA": "#47afe8",
    "Mexico": "#006e9a",
    "Central America": "#656916",
    "Brazil": "#989a34",
    "Rest of South America": "#c3c386",
    "Northern Africa": "#ac4a7f",
    "Western Africa": "#be789e",
    "Eastern Africa": "#debed1",
    "South Africa": "#6f0045",
    "Western Europe": "#e7d9b5",
    "Central Europe": "#C8AB5B",
    "Turkey": "#997C6C",
    "Ukraine region": "#684132",
    "Central Asia": "#492B66",
    "Russia region": "#CCC5DA",
    "Middle East": "#776290",
    "India": "#CB8517",
    "Korea region": "#8FBA5F",
    "China region": "#D8E5C5",
    "Southeastern Asia": "#FFF6A9",
    "Indonesia region": "#FFEE31",
    "Japan": "#21803D",
    "Oceania": "#91A18B",
    "Rest of South Asia": "#F2CD2E",
    "Rest of Southern Africa": "#9D0063",
    }

PREMISE_REGIONS = {
    # Mapping IMAGE region (key) to PREMISE region (value)
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

REV_PREMISE_REGIONS = {
    # Reverse mapping or PREMISE REGION with PREMISE region (key) to IMAGE region (value)
    premise_region: image_region for image_region, premise_region in PREMISE_REGIONS.items()}

PREMISE_REGION_COLORS = {
    # Mapping PREMISE region name (key) to region color (value)
    premise_region: IMAGE_REGION_COLORS[image_region]
    for premise_region, image_region in REV_PREMISE_REGIONS.items()}

MARKET_SHARES = {
    # market shares of conventional production routes
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

GRAVEL_SAND_PROD_SPLIT = {
    "gravel": 0.614,
    "sand": 0.193
}  # amounts based on ADR/HAS production. 1kg concrete can be converted to these products.

GRAVEL_SAND_USE_SPLIT = {
    "gravel": 0.461061682106339,
    "sand": 0.373182244079256
}  # amounts based on sand/gravel fraction in "concrete, all types to generic market for concrete, normal strength" ROW
   # summed from inventory results for "market for gravel" (round and crushed) and "market for sand"

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

METHOD_SAFE_NAME = {
    "EF v3.1, climate change, global warming potential (GWP100)": "climate change",
    "EF v3.1, climate change: fossil, global warming potential (GWP100)": "climate change: fossil",
    "EF v3.1, climate change: biogenic, global warming potential (GWP100)": "climate change: biogenic",
    "EF v3.1, climate change: land use and land use change, global warming potential (GWP100)": "climate change: land use and land use change",
    "EF v3.1, acidification, accumulated exceedance (AE)": "acidification",
    "EF v3.1, ecotoxicity: freshwater, comparative toxic unit for ecosystems (CTUe)": "ecotoxicity: freshwater",
    "EF v3.1, ecotoxicity: freshwater, inorganics, comparative toxic unit for ecosystems (CTUe)": "ecotoxicity: freshwater, inorganics",
    "EF v3.1, ecotoxicity: freshwater, organics, comparative toxic unit for ecosystems (CTUe)": "ecotoxicity: freshwater, organics",
    "EF v3.1, eutrophication: freshwater, fraction of nutrients reaching freshwater end compartment (P)": "eutrophication: freshwater",
    "EF v3.1, eutrophication: marine, fraction of nutrients reaching marine end compartment (N)": "eutrophication: marine",
    "EF v3.1, eutrophication: terrestrial, accumulated exceedance (AE)": "eutrophication: terrestrial",
    "EF v3.1, human toxicity: carcinogenic, comparative toxic unit for human (CTUh)": "human toxicity: carcinogenic",
    "EF v3.1, human toxicity: carcinogenic, inorganics, comparative toxic unit for human (CTUh)": "human toxicity: carcinogenic, inorganics",
    "EF v3.1, human toxicity: carcinogenic, organics, comparative toxic unit for human (CTUh)": "human toxicity: carcinogenic, organics",
    "EF v3.1, human toxicity: non-carcinogenic, comparative toxic unit for human (CTUh)": "human toxicity: non-carcinogenic",
    "EF v3.1, human toxicity: non-carcinogenic, inorganics, comparative toxic unit for human (CTUh)": "human toxicity: non-carcinogenic, inorganics",
    "EF v3.1, human toxicity: non-carcinogenic, organics, comparative toxic unit for human (CTUh)": "human toxicity: non-carcinogenic, organics",
    "EF v3.1, ionising radiation: human health, human exposure efficiency relative to u235": "ionising radiation",
    "EF v3.1, ozone depletion, ozone depletion potential (ODP)": "ozone depletion",
    "EF v3.1, particulate matter formation, impact on human health": "particulate matter formation",
    "EF v3.1, photochemical oxidant formation: human health, tropospheric ozone concentration increase": "photochemical oxidant formation",
    "EF v3.1, water use, user deprivation potential (deprivation-weighted water consumption)": "water use",
    "EF v3.1, land use, soil quality index": "land use",
    "EF v3.1, energy resources: non-renewable, abiotic depletion potential (ADP): fossil fuels": "energy resources: non-renewable",
    "EF v3.1, material resources: metals/minerals, abiotic depletion potential (ADP): elements (ultimate reserves)": "material resources: metals and minerals",
    "Inventory results and indicators, resources, aggregates": "resources, aggregates",
}

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