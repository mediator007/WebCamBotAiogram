
def insert(table: str, keys: list, arguments: tuple) -> str:
    fields = ', '.join(keys)
    placeholder = ', '.join(['?'] * len(arguments))
    sql_line = (
        f'INSERT INTO {table} '
        f'({fields}) '
        f'VALUES ({placeholder});'
    )
    return sql_line

def data_values_to_dataclass(data_class, data):
    my_data = data_class(**data)
    return my_data

# def create_index(table: str, *args):
#     sql_line = f"""CREATE UNIQUE INDEX {table}_idx ON {table} {args};"""
#     return sql_line

# if __name__ == "__main__":
#     print(create_index('reg', 'date', 'name'))