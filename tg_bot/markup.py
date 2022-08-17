from ctypes import resize
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

i_not_allowed_user = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Запрос доступа к рассылке")
)

i_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Список пользователей"),
    KeyboardButton("Запросы на доступ"),
    KeyboardButton("Заблокировать"),
    KeyboardButton("Разблокировать"),
    KeyboardButton("Получить данные"),
)

i_back = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Назад")
)

i_user = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Получить данные")
)

