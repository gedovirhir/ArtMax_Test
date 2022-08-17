from sqlalchemy import (Column, 
                        String, 
                        Integer,
                        Boolean,
                        ForeignKey)
from sqlalchemy.orm import relationship

from .basemodel import basemodel, Session

class Filial(basemodel):
    """
    Таблица для хранения данных о филиалах.
    
        model args:
            name_primary        : str - Название организации 
            source_id           : int = None - id источника, ForeignKey
            web_id              : str = None - id филиала на сайте
            url                 : str  = None - Ссылка на филиал 
            name_extension      : str = None - Доп название
            name_description    : str = None - Описание
            address             : str = None - Адрес
            city                : str = None - Город
            is_deleted          : bool = None - Если филиал удален
    """
    __tablename__ = 'filial'
    
    name_primary = Column(String, nullable=False)
    web_id = Column(String, unique=True)
    url = Column(String)
    name_extension = Column(String)
    name_description = Column(String)
    address = Column(String)
    city = Column(String)
    is_deleted = Column(Boolean)
    
    source_id = Column(Integer, ForeignKey('source.id'))
    
    source = relationship('Source', backref='all_filials')
    
    #reviews_count = Column(Integer)
    #rating_recimal = Column(Float)
    
    def __init__(self,
                 name_primary : str,
                 source_id : int = None,
                 web_id : str = None,
                 url : str  = None,
                 name_extension : str = None,
                 name_description : str = None,
                 address : str = None,
                 city : str = None,
                 is_deleted : bool = None,
        ):
        self.name_primary = name_primary
        self.source_id = source_id
        self.web_id = web_id
        self.url = url
        self.name_extension = name_extension
        self.name_description = name_description
        self.address = address
        self.city = city
        self.is_deleted = is_deleted
    
    @classmethod
    def exclude_add_and_del(cls, 
                       id_field : str,
                       kwargs_list : list[dict],
                       S : Session = basemodel._S()
        ):
        """
        Принимает список словарей с информацией о филиалах.
        Добавляет те, которые не присутствуют в БД, помечает как удаленные филиалы из БД, не присутствующие в входном наборе.
        """
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
    