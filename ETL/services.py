
def insert(table: str, keys: list, arguments: tuple, conflict_field: str) -> str:
    fields = ', '.join(keys)
    placeholder = ', '.join(['?'] * len(arguments))
    sql_line = (
        f'INSERT INTO {table} '
        f'({fields}) '
        f'VALUES ({placeholder});'
    )
    return sql_line


def table_creation(table: str, keys: list):
    fields = ', '.join(keys)
    sql_line = f"""CREATE TABLE IF NOT EXISTS {table} ({fields});"""
    return sql_line


