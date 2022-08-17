from typing import Any
from urllib.error import HTTPError
from requests import session, Session
from fake_useragent import UserAgent
import json

from .baseparser import baseparser

class flamp_parser(baseparser):
    """
    Парсер сайта flamp.
    Парсит с помощью внутреннего api
    """
    class Meta:
        id : int = None
        name : str = 'flamp'
        main_url : str = 'https://ufa.flamp.ru'
    
    _rootpath: str = None # Ссылка на получение списка филиалов организации (например поиск по сайту)
    _orgname: str = None
    _token : str = None
    _s : Session = session() # Сессия для request запросов
    
    _get_filials_api : str = "https://flamp.ru/api/2.0/filials/" 
    _get_reviews_api : str = "https://flamp.ru/api/2.0/filials/{filial_web_id}/reviews"
    
    def __init__(self, orgname: str, rootpath: str = Meta.main_url):
        super().__init__(rootpath, orgname)
        
        self._get_access_token()

    @property
    def _headers(self):
        return {
            'user-agent' : "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
            'Authorization' : f'Bearer {self._token}'
        }
    def _get_access_token(self):
        resp = self._s.get(
            self._rootpath
        )
        self._token = resp.cookies['__cat']
    def get_filials(self) -> list[dict]:
        page_no = 1
        params = lambda: {
            "project" : "ufa",
            "limit" : "15",
            "nocache" : "true",
            "page" : page_no,
            "sort" : "rating",
            "fields" : "id,url,is_deleted,name_primary,name_extension,name_description,address,city",
            "what" : self._orgname
        }
        
        get_objects = lambda: json.loads(
            self._s.get(
                self._get_filials_api, 
                params=params(), 
                headers=self._headers
            ).content
        )
        
        objects = get_objects()
        
        if objects['code'] != 200:
            raise HTTPError(
                objects['message']
            )

        all_filials = []
        while objects['meta']['total'] > 0:
            
            for obj in objects['filials']:
                obj.update({'web_id' : obj['id']})
                obj.pop('id')
            
            all_filials.extend(
                objects['filials']
            )
            
            page_no += 1
            objects = get_objects()
        
        return all_filials
    
    def extract_info(self, filial_web_id : str, limit : int = 5) -> dict:
        reviews = json.loads(
            self._s.get(
                self._get_reviews_api.format(filial_web_id=filial_web_id),
                headers=self._headers,
                params={"limit" : limit}
            ).content
        )
        
        if reviews['code'] != 200:
            raise HTTPError(reviews['message'])
        
        all_reviews = []
        while True:
            for rev in reviews['reviews']:
                all_reviews.append(
                    {
                        'orgname' : self._orgname,
                        'web_id' :  str(rev['id']),
                        'filial_web_id' : rev['filial_id'],
                        'url' : rev['url'],#.replace('\\', ''),
                        'user' : rev['user'],#.replace('\\', ''),
                        'date_created' : rev['date_created'],
                        'rating' : rev['rating'],
                        'text' : rev['text']
                    }
                )
            if not reviews.get('next_link'): break
            reviews = json.loads(
                self._s.get(
                    reviews['next_link'],
                    headers=self._headers
                ).content
            )
        return all_reviews

    def start_parsing(self):
        filials = self.get_filials()
        operations = self._get_operations()
        
        for func in operations['filials']:
            func(filials, self)
        
        reviews = []
        for fl in filials:
            reviews.extend(self.extract_info(
                fl['web_id']
            ))
        
        for func in operations['reviews']:
            func(reviews, self)