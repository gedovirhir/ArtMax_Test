from abc import ABC, abstractmethod
from typing import Any, Callable, overload

def _extend_two_dicts(dict1 :  dict[str, list], dict2 : dict[str, list]):
    new_dict = {}
    for key in dict1:
        new_dict.update(
            {key : dict1[key] + dict2[key]}
        )
    return new_dict
    
class baseparser(ABC):
    """
    Базовыый абстрактный класс парсера.
    Каждый класс-потомок реализует парсинг с определенного сайта.
    Каждый экземпляр реализует парсинг определенной организации.
    """
    class Meta:
        id : int = None
        name : str = None
        main_url : str = None
            
    _rootpath : str = None      # url страницы, на которой находятся блоки для парсинга
    _orgname : str = None       # Название организации
     
    _class_operations : dict[str, list[Callable]] = { # Пул функций, применяемых к полученному контенту
        'filials' : [], # К полученным филиалам
        'reviews' : [] # К полученным отзывам
    }
    def __init__(self, rootpath : str, orgname : str):
        self._rootpath = rootpath
        self._orgname = orgname
        
        self._object_operations : dict[str, list[Callable]] = { # Пул функий на уровне экземпляра
            'filials' : [],
            'reviews' : []
        }
    @abstractmethod
    def get_filials(self) -> list[dict[str, Any]]:
        """
        Функция получения интересующих заведений
        
        return -> list [ filial (dict) {
            name_primary : str - Название организации (филиала)
            url : str | None - Ссылка на филиал
            web_id : str | None - Идентификатор филиала для ориентирования на сайте
            name_extension : str | None - Доп название 
            name_description : str | None - Описание
            address : str | None - Адрес
            city : str | None - Город
            is_deleted | None - Если филиал удален, закрыт и т.д.
        }, ...]
        """
        pass
    
    @abstractmethod
    def extract_info(self, filial_id) -> list[dict[str, Any]]:
        """
        Функция, извлекающее из объекта заведения нужную информацию в виде словаря.
        
         return -> list [ review (dict) {
            orgname : str - Название организации
            filial_web_id : str | None - Идентификатор филиала, к которому написан отзыв, для ориентирования на сайте 
            web_id : str | None - Идентификатор отзыва для ориентирования на сайте
            url : str | None - Ссылка на отзыв
            user : Any | None - Пользователь в любом виде (ссылка, никнейм, id)
            date_created : str | None - Дата  создания
            rating : int | None - Рейтинг
            text : str | None - Текст отзыва
        }, ...]
        """
        pass
    @abstractmethod
    def start_parsing(self):
        """
        Запуск процесса парсинга, где получаются информация с помощью методов и к информации применяются внешне заданные функции
        """
        pass
    
    def _get_operations(self = None):
        if self:
            return _extend_two_dicts(self._class_operations, self._object_operations)
        return __class__._class_operations
    
    @overload
    def set_content_handler(content : str, func : Callable) -> Callable: ...
    @overload
    def set_content_handler(self, content : str, func : Callable, ) -> Callable: ...
    
    def set_content_handler(self = None, **kwargs) -> Callable:
        """
        Декоратор, заносит декорируемую функцию в пул функций, применяемых к паршенному контенту. 
        Декоратор можно применять на уровне класса или на уровне экзепляра (функции применяются при парсинге определенной организации)
        """
        if self:
            def decorator(func):
                self._object_operations[kwargs['content']].append(func)
                return func
        else:
            cls = __class__
            def decorator(func):
                cls._class_operations[kwargs['content']].append(func)
        return decorator
        