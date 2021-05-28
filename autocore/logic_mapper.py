# Setup names that you would use in your "source_data" files
# to invoke or apply logic/ logical conditions on the data.
import template_logic.postgresql.ddl as ddl


logic_map = {
    "clean_postgresql_columns" : ddl.clean_data
}