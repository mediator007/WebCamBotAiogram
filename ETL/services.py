
def insert(table: str, keys: list, arguments: tuple) -> str:
    fields = ', '.join(keys)
    placeholder = ', '.join(['?'] * len(arguments))
    sql_line = (
        f'INSERT INTO {table} '
        f'({fields}) '
        f'VALUES ({placeholder});'
    )
    return sql_line


def empty_str_to_null(data_str: str):
    if data_str == '':
        return 0
    else:
        return data_str