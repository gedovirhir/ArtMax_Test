from datetime import datetime
from sqlalchemy import (Column, 
                        String,
                        Integer,
                        not_,
                        and_)

from .user_status import user_status

from ..basemodel import basemodel, Session
from .status import Status
from sqlalchemy.orm import relationship

from sqlalchemy.orm import Query, Session, sessionmaker

from typing import Any, ClassVar

class User(basemodel):
    """
    Таблица для хранения пользователей.
    
    model args:
        user_tg_id  : int - ID пользователя в телеграми
        username    : str - Имя пользователя
    """
    __tablename__ = "user"
    
    user_tg_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    
    status = relationship('Status', secondary='user_status', backref='users',
                          primaryjoin="and_(User.id==user_status.user_id, user_status.is_active==True)",
                           viewonly=True)
                          #secondaryjoin="user_status.is_active==True"
                          #primaryjoin="User.id==user_status.user_id"
    
    def __init__(self,
                 user_tg_id : int,
                 username : str = None,
                 statuses : list[str] = []
        ):
        self.user_tg_id = user_tg_id
        self.username = username
        self.status = [Status.get(name=st) for st in statuses]
    def __repr__(self) -> str:
        return str({
            'id' : self.id,
            'user_tg_id' : self.user_tg_id,
            'username' : self.username
        })
    @classmethod
    def get_for_mail(cls,
                     allow : list[str] = ['mail_allowed'],
                     except_ : list[str] = ['banned'],
                     S : Session = basemodel._S()
        ) -> Query:
        """
        Возвращает объект запроса Query, содержащий пользователей, которые имеют доступ к рассылке
        """
        allow = [Status.get(name=n, S=S).first() for n in allow]
        except_ = [Status.get(name= n, S=S).first() for n in except_]
        
        clauses = [User.status.contains(st) for st in allow] \
                + [not_(User.status.contains(st)) for st in except_]
        
        users_q = cls.get(S=S).filter(and_(*clauses))
        
        return users_q
    @classmethod
    def get_with_status(cls,
                        status : str,
                        S : Session = basemodel._S()
        ) -> Query:
        """
        Возвращает объект запроса Query, содержащий пользотелей, имеющий введенный статус
        """
        users_q = S.query(cls).join(user_status) \
                              .join(Status) \
                              .filter(and_(Status.name == status,
                                           user_status.is_active == True
                                           )
                                      )
        return users_q
                            
        
    def set_status(self,
                   status_name : str,
                   start_date : datetime = datetime.today(),
                   is_unset : bool = False,
                   is_permastatus : bool = True,
                   end_date : datetime = None,
                   description : str = None,
                   S : Session = basemodel._S()
        ):
        """
        Устанавливает статус пользователя

        Args:
            status_name     : str - Название статуса 
            start_date      : datetime = datetime.today() - Дата начала действия статуса
            is_unset        : bool = False - Флаг снятия статуса 
            is_permastatus  : bool = None - Флаг если статус перманентный
            end_date        : datetime = None - Дата окончания действия статуса
            description     : str = None - Описание
        """
        status_obj : Status = Status.get(name=status_name,S=S).first()
        if not status_obj: raise Exception('status_name does not exist')
        status_active : user_status = user_status.get(user_id=self.id, status_id=status_obj.id, is_active=True).first()
        if status_active and is_unset:
            status_active._update(update_info={'is_active' : False}, S=S)
        elif not status_active and not is_unset:
            user_status.add(user_id=self.id,
                            status_id=status_obj.id, 
                            start_date=start_date, 
                            end_date=end_date, 
                            is_permastatus=is_permastatus, 
                            is_active=True, 
                            description=description)
        elif status_active:
            raise Exception('That User already have that status active. Deactivate first.')
        else:
            raise Exception('That User do not have this status to deactivate.')
            
        self.commit(S)
        
    def get_status(self):
        """
        Возвращает массив имен активных статусов пользователя
        """
        status = [st.name for st in self.status]
        
        return status