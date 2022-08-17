import json
from datetime import date, timedelta
from re import L
import schedule
from sqlalchemy.exc import ProgrammingError
from parsers.flamp_parser import flamp_parser, baseparser
from tg_bot.tg_bot_api import send_new_reviews_mail, mail_send
from db import db_api

# При создании нового класса - парсера его нужно сюда добавить
ALL_PARSERS = {
    flamp_parser : {
        'вкусно и точка' : flamp_parser('вкусно и точка')
    }
}

def add_active_parsers():
    """
    Добавляет новые парсеры в БД
    """
    for p in ALL_PARSERS:
        newp = db_api.Source.get(name=p.Meta.name).first()
        if not newp:
            newp = db_api.Source.add(
                name=p.Meta.name,
                main_url=p.Meta.main_url
            )
        p.Meta.id = newp.id
def parsers_iterator(func):
    """
    Итерирует парсеры функцией
    """
    for p in ALL_PARSERS:
        for sub_p in ALL_PARSERS[p]:
            func(ALL_PARSERS[p][sub_p])

@flamp_parser.set_content_handler(content='filials')
def filials_key_normalize(filials : list[dict], parser):
    """
    Добавляет айди источника в информацию о филиалах    
    """
    for obj in filials:
            obj.update({'source_id' : parser.Meta.id})

@flamp_parser.set_content_handler(content='filials')
def add_filials(filials : list[dict], parser):
    """
    Добавляет массив филиалов в БД 
    """
    db_api.Filial.exclude_add_and_del(
        'web_id', 
        filials
    )

@flamp_parser.set_content_handler(content='reviews')
def reviews_key_normalize(reviews : list[dict], parser):
    for rev in reviews:
        filial_id = db_api.Filial.get(fields_=['id'], web_id=rev['filial_web_id']).first()[0]
        rev.update({
            'filial_id' : filial_id,
            'is_new' : True
        })
        rev.pop('filial_web_id')
@flamp_parser.set_content_handler(content='reviews')
def add_reviews(reviews : list[dict], parser : baseparser):
    db_api.Review.set_not_new(parser.Meta.id)
                 
    db_api.Review.exclude_add_and_del(
        'web_id',
        reviews
    )


def start_parsing():
    parsers_iterator(
        lambda x: x.start_parsing()
    )
if __name__ == '__main__':
    monitoringDelay = timedelta(minutes=3).total_seconds()
    try:
        db_api.create_database_if_not_exist()
    except ProgrammingError:
        pass
    add_active_parsers()
    schedule.every(monitoringDelay).seconds.do(start_parsing)
    schedule.every(monitoringDelay).seconds.do(send_new_reviews_mail)
    
    while True:
        schedule.run_pending()