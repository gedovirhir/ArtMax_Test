from datetime import datetime
from sqlalchemy import (Column,
                        Text,
                        DateTime,
                        Integer,
                        Boolean, 
                        ForeignKey,
                        UniqueConstraint)

from ..basemodel import basemodel

class user_status(basemodel):
    """
    Таблица для хранения информации о статусах пользователей.
    
    model args:
        user_id         : int - ID пользователя
        status_id       : int - ID статуса
        start_date      : datetime = datetime.today() - Дата начала действия статуса
        end_date        : datetime = None - Дата окончания действия статуса
        is_permastatus  : bool = None - Флаг если статус перманентный
        is_active       : bool = True - Флаг активности статуса
        description     : str = None - Описание
    """
    __tablename__ = "user_status"
    
    user_id = Column(Integer, ForeignKey('user.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    status_id = Column(Integer, ForeignKey('status.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    is_permastatus = Column(Boolean, default=True)  
    start_date = Column(DateTime, nullable=False, default=datetime.now())
    end_date = Column(DateTime)
    is_active = Column(Boolean, nullable=False, default=True)
    description = Column(Text)
    
    # unique : (user_id, status_id, is_active=True)
    
    def __init__(self,
                user_id : int,
                status_id : int,
                start_date : datetime = datetime.now(),
                end_date : datetime = None,
                is_permastatus : bool = None,
                is_active : bool = True,
                description : str = None 
        ):
        if not end_date and not is_permastatus: is_permastatus = True
        
        self.user_id = user_id
        self.status_id = status_id
        self.start_date = start_date
        self.end_date = end_date
        self.is_permastatus = is_permastatus
        self.is_active = is_active
        self.description = description

        