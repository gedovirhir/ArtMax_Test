from datetime import datetime, date
import sys
import os
import requests

sys.path.append(os.path.abspath('./'))
from db import db_api 

TOKEN = os.getenv('TOKEN')
request_url = "https://api.telegram.org/bot{bot_token}/{operation}"

def send_message(chat_id : str, text : str):
    url = request_url.format(
        bot_token=TOKEN,
        operation='sendMessage'
    )
    params = {
        'chat_id' : chat_id,
        'text' : text 
    }
    r = requests.get(
        url,
        params=params
    )
    return r
def mail_send(users_tg_id : list, header : str, messages : list[str]):
    if not isinstance(users_tg_id, list): users_tg_id = [users_tg_id]
    for id in users_tg_id:
        send_message(
            id,
            header
        )
        for mesg in messages:
            send_message(
                id, 
                mesg
            )
def generate_report():
    new_reviews : list[db_api.Review] = db_api.Review.get(is_new=True).all()
    
    header = f'НОВЫЕ ОТЗЫВЫ на {date.today()}:'
    mesg = []
    for r in new_reviews:
        mesg.append(f'Ссылка: {r.url}\nАвтор: {r.user}\nДата: {r.date_created}\nРейтинг: {r.rating}\nТекст:\n{r.text}\n\n')
    if not mesg: mesg = ['Нет.']
    return (header, mesg)

def send_new_reviews_mail():
    users_to_send : list[db_api.User] = db_api.User.get_for_mail().all()
    header, mesg = generate_report()
    mail_send(
        [
            u.user_tg_id for u in users_to_send
        ], header, mesg
    )
    