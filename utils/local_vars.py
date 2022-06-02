from typing import NamedTuple

# порог $ для начала рассылки
c = 500

# пароль админа
admin_pass = 8800

cells_for_sum = [
    'Chaturbate (tks)', 'CamSoda', 'MFC (tks)',
    'Stripchat (tks)', 'Jasmin', 'Streamate'
]

bonus_table = {
    400: 51, 450: 52, 500: 53, 550: 54, 600: 55,
    650: 56, 700: 57, 750: 58, 800: 59, 850: 60
}

available_work_buttons = [
    "отправить отчет", 
    "узнать баланс", 
    "остаток до бонуса", 
    "выйти из аккаунта",
    ]

available_sites_buttons = [
    'Chaturbate', 
    'Stripchat', 
    'Jasmin', 
    'Streamate', 
    'CamSoda', 
    'MFC',
    'SkyPrivate',
    ]

available_admin_buttons = [
    "отчет за сегодня",
    "отчет по дате",
    "список моделей",
    "добавить модель", 
    "удалить модель", 
    "выйти из аккаунта",
    ]