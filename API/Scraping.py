from typing import Optional, TYPE_CHECKING

import requests
from bs4 import BeautifulSoup

from API.DataTypes import SCRAPER_CONFIG
from API.FlagTypes import page_root
    
class Scraper:
    def __init__(self, config:dict):
        self.config = config

    def __findPagePath(self, target_page:page_root) -> str: return f'{self.config.rootURL}/{self.config.page_roots[target_page]}'

    @classmethod
    def scrape(self, targetPage:str) -> BeautifulSoup:
        page = requests.get(targetPage)
        return BeautifulSoup(page.content, "html.parser")
    
    def loadPageData(self, targetPage:page_root, id:Optional[str] = None) -> BeautifulSoup:
        print(targetPage)
        print(self.config)
        print(self.config.page_roots[targetPage])
        if id != None: return self.scrape(f'{self.__findPagePath(targetPage)}/{id}')
        else: return self.scrape(self.__findPagePath(targetPage))
    
    def getImage(self, targetAsset:str):
        return requests.get(f'{self.config.rootURL}/assets/{targetAsset}', stream=True)
    
    #region PROPERTIES
    @property
    def config(self) -> SCRAPER_CONFIG: return self.__config
    @config.setter
    def config(self, cf:dict) -> None:
        self.__config = SCRAPER_CONFIG(cf['rootURL'], dict([(page_root(key), val) for key, val in cf['page_roots'].items()]))
    #endregion