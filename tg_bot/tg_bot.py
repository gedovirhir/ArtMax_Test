from shutil import ExecError
from urllib import request
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import logging
import os
import sys

from markup import i_not_allowed_user, i_admin, i_back,i_user
from states import dialog

sys.path.append(os.path.abspath('./'))
from db.db_api import (User,
                       Status,
                       user_status,
                       Request,
                       requests_view
                       )
from tg_bot_api import generate_report, mail_send
TOKEN = os.getenv('TOKEN')
ADMIN = int(os.getenv('ADMIN'))


def _is_admin(user_tg_id : int):
    user = User.get(user_tg_id=user_tg_id).first()
    return user_tg_id == ADMIN \
           or (user and 'admin' in user.get_status())
def _reg_user(
    user_tg_id : int,
    username : str, 
    statuses : list[str] = []
):
    new_user = User.add(
            user_tg_id=user_tg_id,
            username=username
        )
    for s in statuses:
        new_user.set_status(s)
    return new_user
def _get_all_users():
    all_users = User.get().all()
    return all_users
def _get_requests():
    all_req = requests_view.get(is_active=True).all()
    return all_req
def _get_users_with_status(status : str):
    return User.get_with_status(status).all()
    

logging.basicConfig(level=logging.INFO)

_bot = Bot(token=TOKEN)
_dp = Dispatcher(_bot, storage=MemoryStorage())


@_dp.message_handler(commands=['start'])
async def start(message: Message):
    tg_user = message.from_user
    db_user = User.get(user_tg_id=tg_user.id).first()
    
    if _is_admin(tg_user.id):
        if not db_user: 
            _reg_user(
                tg_user.id,
                tg_user.username,
                ['admin', 'mail_allowed']
            )
            
        await message.answer("Добро пожаловать на админ-панель", reply_markup=i_admin)
    else: 
        if not db_user: 
            db_user = _reg_user(
                user_tg_id=tg_user.id,
                username=tg_user.username
            )
            await message.answer("Вы зарегистрированы в боте")
        elif 'banned' in db_user.get_status(): 
            await message.answer("Доступ заблокирован")
            dialog.banned_user.set()
            return
        
        mrk = i_not_allowed_user if 'mail_allowed' not in db_user.get_status() else i_user
        await message.answer('Привет!', reply_markup=mrk)
            
@_dp.message_handler(content_types=['text'], text='Заблокировать')
async def ban_handler(message : Message, state: FSMContext):
    if _is_admin(message.from_user.id):
        header = 'id    tg_id   username    status\n'
        body_t = '{id}    {tg_id} {username}    {status}\n'
        body = ''

        for u in _get_all_users():
            body += body_t.format(id=u.id,
                                  tg_id=u.user_tg_id,
                                  username=u.username,
                                  status=','.join([st.name for st in u.status]))
        await dialog.ban.set()
        await message.answer('Введите id пользователя, которого нужно заблокировать.\nДля отмены нажмите кнопку "Назад"\n' + header + body, reply_markup=i_back)
        
@_dp.message_handler(content_types=['text'], text='Разблокировать')
async def unban_handler(message : Message, state: FSMContext):
    if _is_admin(message.from_user.id):
        header = 'id    tg_id   username    status\n'
        body_t = '{id}    {tg_id} {username}    {status}\n'
        body = ''

        for u in _get_users_with_status('banned'):
            body += body_t.format(id=u.id,
                                  tg_id=u.user_tg_id,
                                  username=u.username,
                                  status=','.join([st.name for st in u.status]))
        await dialog.unban.set()
        await message.answer('Введите id пользователя, которого нужно Разблокировать.\nДля отмены нажмите кнопку "Назад"\n' + header + body, reply_markup=i_back)

@_dp.message_handler(content_types=['text'], text='Список пользователей')
async def getUsers_handler(message : Message, state: FSMContext):
    if _is_admin(message.from_user.id):
        header = 'id    tg_id   username    status\n'
        body_t = '{id}    {tg_id} {username}    {status}\n'
        body = ''

        for u in _get_all_users():
            body += body_t.format(id=u.id,
                                  tg_id=u.user_tg_id,
                                  username=u.username,
                                  status=','.join([st.name for st in u.status]))
        await message.answer('Список пользователей\n' + header + body, reply_markup=i_admin)
        
@_dp.message_handler(content_types=['text'], text='Запросы на доступ')
async def usersRequests_handler(message : Message, state: FSMContext):
    if _is_admin(message.from_user.id):
        header = '\nid    tg_id   username    status\n'
        body_t = '{id}    {tg_id} {username}    {status}\n'
        body = ''

        for r in _get_requests():
            body += body_t.format(id=r.id,
                                  tg_id=r.user_tg_id,
                                  username=r.username,
                                  status=r.name)
        await message.answer('Список заявок на доступ к рассылке\nВведите id заявки для одобрения' + header + body, reply_markup=i_back)
        await dialog.mail_allow.set()

        
        
@_dp.message_handler(content_types=['text'], text='Назад', state=dialog.mail_allow)      
@_dp.message_handler(content_types=['text'], text='Назад', state=dialog.unban)
@_dp.message_handler(content_types=['text'], text='Назад', state=dialog.ban)
async def ban_exit(message: Message, state: FSMContext):
    await message.answer('Отмена.', reply_markup=i_admin)
    await state.finish()
    
@_dp.message_handler(content_types=['text'], state=dialog.ban)
async def ban_exec(message: Message, state: FSMContext):
    if message.text.isdigit():   
        user = User.get(id=message.text).first()
        if not user: 
            await message.answer('Введены некорректные данные')
        else:
            try:
                user.set_status(status_name='banned')
                await message.answer('Пользователь забанен', reply_markup=i_admin)
            except Exception:
                await message.answer('Пользователь уже забанен', reply_markup=i_admin)
    else:
        await message.answer('Введены некорректные данные')
    await state.finish()
    
@_dp.message_handler(content_types=['text'], state=dialog.unban)
async def unban_exec(message: Message, state: FSMContext):
    if message.text.isdigit():   
        user = User.get(id=message.text).first()
        if not user: 
            await message.answer('Введены некорректные данные')
        else:
            try:
                user.set_status(status_name='banned', is_unset=True)
                await message.answer('Пользователь разбанен', reply_markup=i_admin)
            except Exception:
                await message.answer('Пользователь не был в бане', reply_markup=i_admin)
        await state.finish()
    else:
        await message.answer('Введены некорректные данные')
    await state.finish()

@_dp.message_handler(content_types=['text'], state=dialog.mail_allow)  
async def mail_allow_exec(message: Message, state: FSMContext):
    if message.text.isdigit():   
        req = Request.get(id=message.text).first()
        if not request: 
            await message.answer('Введены некорректные данные')
        else:
            try:
                req.approve()
                await message.answer('Заявка одобрена', reply_markup=i_admin)
            except Exception:
                await message.answer('Заявка уже одобрена', reply_markup=i_admin)
        await state.finish()
    else:
        await message.answer('Введены некорректные данные')
    await state.finish()
    

@_dp.message_handler(content_types=['text'], text='Запрос доступа к рассылке')
async def request_handler(message: Message, state: FSMContext):
    db_user = User.get(user_tg_id=message.from_user.id).first() 
    
    if not db_user: await message.answer('Вы не зарегистрированы в боте, для регистрации вызовите /start.')
    
    else:
        stat = Status.get(name='mail_allowed').first()
        req = Request.get(user_id=db_user.id, status_id=stat.id, is_active=True).first()
        
        if req: await message.answer('Ваша заявка ожидает одобрения администратора.')
        
        elif stat.name in db_user.get_status(): await message.answer('У вас уже есть доступ к рассылке', reply_markup=i_user)
        
        else:
            Request.add(user_id=db_user.id, status_id=stat.id)
            await message.answer('Ваша заявка отправлена, ждите одобрения администратора.')
@_dp.message_handler(content_types=['text'], text='Получить данные')
async def getData_handler(message: Message, state: FSMContext):
    db_user = User.get(user_tg_id=message.from_user.id).first()
    
    if not db_user: await message.answer('Вы не зарегистрированы, для регистрации введите /start')
    
    elif 'banned' in db_user.get_status(): await message.answer('Вы заблокированы')
    elif 'mail_allowed' not in db_user.get_status(): await message.answer('У вас нет доступа к рассылке')
    else: 
        header, mesg = generate_report()
        mail_send(db_user.user_tg_id, header, mesg)

if __name__ == '__main__':
    executor.start_polling(_dp, skip_updates=True)