from aiogram.dispatcher.filters.state import State, StatesGroup

class dialog(StatesGroup):
    spam = State()
    ban = State()
    unban = State()
    mail_allow = State()
    
    banned_user = State()
    admin = State()