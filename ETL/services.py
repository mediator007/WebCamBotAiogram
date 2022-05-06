def insert(table: str, keys: list, arguments: tuple, conflict_field: str) -> str:
    # Убрал slots т.к. с ними не работает created: datetime = field(default_factory=datetime.now)
    fields = ', '.join(keys)
    placeholder = ', '.join(['%s'] * len(arguments))
    sql_line = (
        f'INSERT INTO {table} '
        f'({fields}) '
        f'VALUES ({placeholder}) ON CONFLICT ({conflict_field}) DO NOTHING;'
    )
    return sql_line