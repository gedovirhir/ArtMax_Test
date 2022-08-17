from sqlalchemy import (Column, 
                        String,
                        Integer, 
                        Text, 
                        DateTime,
                        Boolean, 
                        ForeignKey,
                        update)
from sqlalchemy.orm import relationship

from datetime import datetime

from .basemodel import basemodel, Session, sessionmaker
from .source import Source
from .filial import Filial

class Review(basemodel):
    """
    Таблица для хранения отзывов.
    
    model args:
        orgname         : str - Название организации
        filial_id       : int = None - id филиала, ForeignKey
        web_id          : str = None - id отзыва на сайте
        url             : str = None - Ссылка на отзыв
        user            : str = None - Автор
        date_created    : datetime = None - Дата создания
        rating          : int = None - Рейтинг
        text            : str = None - Содержание отзыва
        is_new          : bool = None - Если отзыв новый
        is_deleted      : bool = False - Если отзыв удален
    """
    __tablename__ = "review"
    
    orgname = Column(String, nullable=False)
    web_id = Column(String, unique=True)
    url = Column(String)
    user = Column(String)
    date_created = Column(DateTime)
    rating = Column(Integer)
    text = Column(Text)
    is_deleted = Column(Boolean)
    is_new = Column(Boolean)
    
    filial_id = Column(Integer(), ForeignKey('filial.id'))
    
    filial = relationship('Filial', backref='all_reviews')
    
    def __init__(self,
                 orgname : str,
                 filial_id : int = None,
                 web_id : str = None,
                 url : str = None,
                 user : str = None,
                 date_created : datetime = None,
                 rating : int = None,
                 text : str = None,
                 is_new : bool = None,
                 is_deleted : bool = False
        ):
        self.orgname = orgname
        self.filial_id = filial_id
        self.web_id = web_id
        self.url = url
        self.user = user
        self.date_created = date_created
        self.rating = rating
        self.text = text
        self.is_new = is_new 
        self.is_deleted = is_deleted

    @classmethod
    def set_not_new(cls,
                    source_id,
                    S : Session = basemodel._S()):
        
        q = ( 
             update(cls).where(cls.filial_id == Filial.id) \
                        .where(Filial.source_id == source_id)
                        .values(is_new=False)
        )
        S.execute(q, execution_options={'synchronize_session' : 'fetch'})
        cls.commit(S)
    @classmethod
    def exclude_add_and_del(cls, 
                       id_field : str,
                       kwargs_list : list[dict],
                       S : Session = basemodel._S()
        ):
        ids = [i[id_field] for i in kwargs_list]
        all = cls.get(S, is_deleted=False)
        
        todel = all.filter(
            getattr(cls, id_field).not_in(ids)
        )
        todel.update({cls.is_deleted : True})
        
        cls.commit(S)
        
        return cls.add_objects_set(
            id_field,
            kwargs_list,
            S
        )