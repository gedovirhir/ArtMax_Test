from sqlalchemy import (Column, 
                        String,
                        Integer)

from .basemodel import basemodel,Session

class Source(basemodel):
    """
    Таблица для хранения информации о основных источниках данных.
    
    model args:
        name        : str - Название источника данных
        main_url    : str = None - Ссылка на основную страницу
    """
    __tablename__ = 'source'
    
    name = Column(String, unique=True, nullable=False)
    main_url = Column(String)
    
    def __init__(self,
                 name : str, 
                 main_url : str = None
        ):
        """
        args:
            name        : str - Название источника данных
            main_url    : str = None - Ссылка на основную страницу
        """
        self.name = name
        self.main_url = main_url
        