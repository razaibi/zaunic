# Setup names that you would use in your "source_data" files
# to invoke or apply logic/ logical conditions on the data.
from template_logic import postgresql


logic_map = {
    "clean_postgresql_columns" : postgresql.clean_postgresql_ddl_data
}