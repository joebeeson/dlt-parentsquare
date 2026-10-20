"""Load ParentSquare data into a local DuckDB database."""

import dlt

from dlt_parentsquare import parentsquare

pipeline = dlt.pipeline(
    pipeline_name="parentsquare",
    destination="duckdb",
    dataset_name="school",
)
load_info = pipeline.run(parentsquare())
print(load_info)
