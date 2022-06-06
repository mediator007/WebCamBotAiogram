# WebCamBotAiogram
Телеграм бот для контроля баланса зарегестрированных пользователей.

## Перед запуском необходимо:

  - В директории utils создать файл ```config.py``` с переменными: 
    - token - для связи с telegram
    - registration_file - с именем файла регистрации на GoogleDrive
    - main_file - с именем главного файла на GoogleDrive
  - Добавить в корень файл .json  для связи с google drive через gspread.

## Запуск в docker:

  `````./run.sh start`````

## Запуск через systemd:
  - ```sudo apt-get update -y```
  - ```sudo apt-get install -y systemd```
  - В файле ```bot.service``` указать директорию бота на сервере
  - Положить файл ```bot.service``` в директорию ```/etc/systemctl/system```
  - Выполнить команды:
    - ```systemctl daemon-reload```
    - ```systemctl enable bot```
    - ```systemctl start bot```
    - ```systemctl status bot```

## При запуске:
  - Поднимается база данных sqlite3. 
  - Создаётся файл для логирования.
  - Запускается ETL-pipeline GDrive-SQlite для синхронизации данных из Google Sheets в бд
  - Запускается сервис рассылки 
    
