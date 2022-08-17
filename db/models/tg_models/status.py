from sqlalchemy import (Column, 
                        String,
                        Text
                        )
from sqlalchemy.orm import relationship
from ..basemodel import basemodel
"""
admin
mail_allowed
banned
"""
class Status(basemodel):
    """
    Таблица для хранения статусов. Основные: admin, mail_allowed, banned
    
    model args:
        name        : str - Название статуса
        description : str - Описание статуса
    """
    __tablename__ = "status"

    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    # users - relationship
    
    def __init__(self,
                 name : str,
                 description : str = None
        ):
        self.name = name
        self.description = description