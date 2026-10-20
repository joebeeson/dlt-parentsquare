"""Load synthetic or live ParentSquare data into a local DuckDB database."""

import os

import dlt

from dlt_parentsquare import parentsquare


pipeline = dlt.pipeline(
    pipeline_name="parentsquare",
    destination="duckdb",
    dataset_name="school",
)
load_info = pipeline.run(
    parentsquare(
        username=os.environ["PARENTSQUARE_USERNAME"],
        password=os.environ["PARENTSQUARE_PASSWORD"],
    )
)
print(load_info)
