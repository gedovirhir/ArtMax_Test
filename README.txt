Настройка и запуск:

Клонируйте репозиторий на локальную машину: git clone https://github.com/gedovirhir/ArtMax_Test
Заполните поле CHAT_ID в конфиг файле config/.env.prod. Чтобы получить chat_id, запустите бота @username_to_id_bot.
Бот присылающий уведомления доступен по адресу @kanalserviceNoticeBot.
Перед запуском докер композа обязательно найдите бота в тг
Убедитесь что на вашей машине установлен docker и docker-compose
Находясь в папке проекта запустите команду в терминале: docker-compose up