# WebCamBotAiogram
Телеграм бот для контроля баланса зарегестрированных пользователей.

## Перед запуском необходимо:

  - В директории utils создать файл ```config.py``` с переменными: 
    - token - для связи с telegram
    - registration_file - с именем файла регистрации на GoogleDrive
    - main_file - с именем главного файла на GoogleDrive
  - Добавить в корень файл .json  для связи с google drive через gspread.

## Чтобы запустить бота в docker:

  `````./run.sh start`````

## Чтобы запустить бота через systemctl:  
  - Положить файл ```bot.service``` в директорию ```/etc/systemctl```
  - Выполнить команду ```systemctl start bot```

## При запуске:
  - Поднимается база данных sqlite3. 
  - Создаётся файл для логирования.
  - Запускается ETL-pipeline GDrive-SQlite для синхронизации данных из Google Sheets в бд
  - Запускается сервис рассылки 
    
