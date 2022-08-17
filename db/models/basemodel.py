from sqlalchemy import (Column,
                        Integer,
                        Boolean,
                        update
                        ) 
from sqlalchemy.orm import Session, sessionmaker, Query

from typing import Any, ClassVar

from .db_exec import base, session

class basemodel(base):
    """
    Базовый абстрактный класс модели базы данных
    """
    __abstract__: ClassVar[bool] = True
    
    _S : sessionmaker = session
    
    id = Column(Integer, primary_key=True, autoincrement=True)
        
    @classmethod
    def commit(cls,
               S : Session,
        ):
        if not S.autocommit:
            S.commit()
        S.close()
    @classmethod
    def get(cls,
            S : Session = _S(),
            fields_ : list[str] = [],
            **kwargs
        ) -> Query:
        q = S.query(cls)
        
        if fields_:
            q = q.with_entities(
                *[
                    getattr(cls, field) for field in fields_ 
                ]
            )
        
        for key, item in kwargs.items():
            q = q.filter(getattr(cls, key) == item)
        
        
        #cls.commit(S)
        return q
    @classmethod
    def add(cls, 
            S : Session = _S(), 
            **kwargs
        ) -> Any:
        new = cls(**kwargs)
        S.add(new)
        
        S.commit()
        
        return new
        
    @classmethod
    def add_objects_set(
        cls, 
        id_field : str,
        kwargs_list : list[dict],
        S : Session = _S()
    ) -> list[Any]:
        """
        Добавляет список объектов
        """
        all = cls.get(S)
        
        added_objects = []
        db_ids = [getattr(obj, id_field) for obj in all]
        
        for obj_toadd in kwargs_list:
            if obj_toadd[id_field] not in db_ids:
                added_objects.append(
                    cls.add(S,**obj_toadd)
                )
                
        S.commit()
        S.close()
        
        return added_objects
                
    @classmethod
    def exclude_add_and_del(cls, 
                       id_field : str,
                       kwargs_list : list[dict],
                       S : Session = _S()
        ) -> list[Any]:
        """
        Принимает список словарей с информацией об объектах.
        Добавляет те, которые не присутствуют в БД, удаляет объекты из БД, не присутствующие в входном наборе.
        """
        ids = [i[id_field] for i in kwargs_list]
        all = cls.get(S, is_deleted=False)
        
        todel = all.filter(
            getattr(cls, id_field).not_in(ids)
        )
        todel.delete()
        
        cls.commit(S)
        
        return cls.add_objects_set(
            id_field,
            kwargs_list,
            S
        )

    @classmethod
    def delete(cls,
               S : Session = _S(),
               **kwargs
        ):
        q = cls.get(S, **kwargs)
        q.delete()
        
        cls.commit(S)
        
    def _update(self,
               update_info :  dict,
               S : Session,
        ):
        for key, item in update_info.items():
            setattr(self, key, item)
        S.commit()