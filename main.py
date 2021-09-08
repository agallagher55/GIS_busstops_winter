import os

import pandas as pd

from arcgis.features import GeoAccessor
from utils import get_domain_values

OUTPUT_CSV = "./reports/grouped_results.csv"
SDE = r"C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde"

BUS_STOPS = os.path.join(SDE, "SDEADM.TRN_bus_stop")
WINT_ZONE_DOMAIN = "AST_sidewalk_plow_zone"
WINT_ROUTE_DOMAIN = "AST_sidewalk_plow_routes"

bus_stop_fields = [
    "BUSSTOPID",
    "STOPNUMBER",
    "LOCATION",
    "BUSSTATUS",
    "WINT_PLOW",
    "WINT_MAINT",  # CONTRACT
    "WINT_ROUTE",  # ROUTE
    "WINT_LOS",  # PRIORITY
    "WINT_RESP",
    "WINT_COMM"
]

bus_stop_sql = "BUSSTATUS NOT LIKE 'OUT' AND WINT_PLOW LIKE 'Y'"

df = GeoAccessor.from_featureclass(
    location=BUS_STOPS,
    where_clause=bus_stop_sql,
    fields=bus_stop_fields
)

print(df.head())
print(df.info())

# Replace domain values
for col in {"WINT_MAINT", "WINT_ROUTE"}:
    df.replace(
        to_replace={col: get_domain_values(BUS_STOPS, col)},
        inplace=True
    )

# Group values BY CONTRACT, ROUTE
df.sort_values(
    by=["WINT_MAINT", "WINT_ROUTE", "LOCATION", "STOPNUMBER"]
)

# Rename columns
df.rename(
    {
        "WINT_MAINT": "WINTER MAINTENANCE ZONE",
        "WINT_ROUTE": "WINTER MAINTENANCE ROUTE",
        "WINT_LOS": "WINTER MAINTENANCE LEVEL OF SERVICE",  # Priority
        "WINT_RESP": "WINTER MAINTENANCE RESPONSIBILITY",
        "WINT_COMM": "COMMENTS",
        "STOPNUMBER": "STOP NUMBER",
    },
    inplace=True,
    axis="columns"
)

# Replace column values
contract_values = get_domain_values(BUS_STOPS, "WINT_MAINT")

# Drop columns
print(df.columns)
for col in ["SHAPE", "BUSSTATUS", "WINT_PLOW"]:
    if col in df.columns:
        df.drop([col], axis=1, inplace=True)

print(df.head())

if not os.path.exists("./reports"):
    os.makedirs("reports")

if not os.path.exists(OUTPUT_CSV):
    open(OUTPUT_CSV, "a").close()

# Group by Contract
contracts = sorted(df['WINTER MAINTENANCE ZONE'].unique().tolist())
for contract in contracts:
    print(f"\tCONTRACT: {contract}")

    contract_df = df[df['WINTER MAINTENANCE ZONE'] == contract]
    contract_df.sort_values(by=["WINTER MAINTENANCE ROUTE", "LOCATION", "STOP NUMBER"], inplace=True)

    contract_df = contract_df.append(pd.Series(), ignore_index=True)  # append blank row

    contract_df.to_csv(OUTPUT_CSV, index=False, mode='a')


# TODO: format - add title, get records counts of groups
