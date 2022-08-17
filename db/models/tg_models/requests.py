from sqlalchemy import (Column,
                        Integer,
                        Boolean, 
                        ForeignKey)

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy_utils import create_view
from typing import Any, ClassVar, overload

from .status import Status
from .user import User
from .user_status import user_status

from ..basemodel import basemodel, base

class Request(basemodel):
    """
    Таблица для хранения запросов на получение пользователями статусов.
    
    model args:
        user_id         : int
        status_id       : int
        is_active       : bool = True
    """
    __tablename__ = "requests"
    
    user_id = Column(Integer, ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    status_id = Column(Integer, ForeignKey('status.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # unique : (user_id, status_id, is_active=True)
    
    def __init__(self,
                user_id : int,
                status_id : int,
                is_active : bool = True 
        ):
        self.user_id = user_id
        self.status_id = status_id
        self.is_active = is_active
    def approve(self,
                S : Session = basemodel._S()
        ):
        """
        Метод экзепляра, "одобряет" запрос и вносит в базу user_status соответствующую запись
        """
        user : User = User.get(id=self.user_id,S=S).first()
        status : Status = Status.get(id=self.status_id,S=S).first()
        
        user.set_status(
            status_name=status.name,
            S=S
        )
        self.is_active = False
        self.commit(S)

# Представление с показательной информации из таблицы requests
_smt = select([
        Request.id,
        User.username,
        User.user_tg_id,
        Status.name,
        Request.is_active
    ]).where(
        Request.user_id ==  User.id,
        Request.status_id == Status.id
    )
class requests_view(basemodel):
    view = create_view('requests_view', _smt, base.metadata)
    __table__ = view