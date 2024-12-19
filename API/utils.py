from typing import Optional, Union

import os, json, sqlite3, shutil
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from API.DataTypes import (API_CONFIG,
                             Equipment, Trait, TraitRarity)
from API.FlagTypes import ConfigType, page_root

from API.Scraping import Scraper
from API.Database.DBTools import findInDB
from API.Database.EquipUtils import downloadEquipData
from API.Database.TraitUtils import findTrait, dictedTraits

class DBAPIConnection:
    def __init__(self, app_root:str) -> None:
        self.appRoot = self.__getRoot(app_root)
        self.config = self.loadConfig((ConfigType.API))
        self.scraper = Scraper(self.loadConfig(ConfigType.SCRAPER))
        self.__affirmDB()

    #region UTILS

    #region CLASS METHODS
    @classmethod
    def __joinpaths(self, root:str, addon:str) -> str: return os.path.join(root, addon)
    @classmethod
    def __getRoot(self, path:str) -> str: return os.path.dirname(path)
    #endregion

    #region RELPATH
    def getAssetPath(self, asset_rel_path:str) -> None: return self.__joinpaths(self.appRoot, f'{self.config.asset_rel_root}/{asset_rel_path}')
    def buildRelAssetPath(self, asset_rel_path:str) -> None: return f'static{os.sep}assets{os.sep}{asset_rel_path}{os.sep}'
    def getConfigPath(self, configType:ConfigType) -> str: return self.__joinpaths(self.appRoot, f'DBLAPI-CONFIG{os.sep}{configType.value}.json')
    #endregion

    #region CONFIG
    def loadConfig(self, configType:ConfigType, field:Optional[str] = None) -> Union[dict, str]:
        with open(self.getConfigPath(configType), 'r') as cFile: config = json.load(cFile)

        if field is None: return config
        else: return config[field]

    def updateConfig(self, configType:ConfigType, field:str, value) -> None:
        configPath = self.getConfigPath(configType)
        with open(configPath, 'r') as cFile:
            config = json.load(cFile)
        config[field] = value
        with open(configPath, 'w') as cFile:
            json.dump(config, cFile)

    #endregion

    #endregion

    #region SCRAPING
    def loadPageData(self, targetPage:page_root, id:Optional[str] = None) -> BeautifulSoup: return self.scraper.loadPageData(targetPage, id)

    def scrapeTraitData(self, traitID:int) -> dict:
        soup = self.scraper.loadPageData(page_root.TRAIT, traitID)
        rawData = soup.find('div', class_ = 'container text-center')
        return {'name': rawData.find('h2').text, 'desc': rawData.find('h5').text}
    
    #endregion

    #region DATABASE
    def getDBConn(self) -> sqlite3.Connection: return sqlite3.connect(self.dbPath)

    def getLastDBSyncDate(self, iso:bool):
        if iso is False: return datetime.strptime(self.config.db_last_updated, '%d/%m/%y %H')
        else: return datetime.strptime(self.config.db_last_updated, '%d/%m/%y %H').isoformat()

    def __affirmDB(self) -> None:
        lUpdate = datetime.now() - self.getLastDBSyncDate(False)
        if lUpdate.total_seconds() >= timedelta(days=7).total_seconds():
            self.__updateDBs()
            self.updateConfig(ConfigType.API, 'db_last_updated', datetime.strftime(datetime.now(), '%d/%m/%y %H'))

    def __updateDBs(self) -> None: self.__updateEquipDB()

    def findInDB(self, itemID:Union[str,int], tableName:str) -> dict: return findInDB(self, itemID, tableName)

    def __updateEquipDB(self) -> None:
        equipList = downloadEquipData(self)
        with open(self.getAssetPath('temp.txt'), 'w') as f:
            f.write(f'{equipList}')
        conn = self.getDBConn()
        cursor = conn.cursor()
        cursor.executemany('''
                           REPLACE INTO "equip" (id, name, rarity, img_path, is_ToP, conditions, effect1, effect2, effect3)
                           VALUES (?,?,?,?,?,?,?,?,?)
                            ''', [(e.id, e.name, e.rarity.value, e.img_path, e.is_ToP, e.conditions, e.effect1, e.effect2, e.effect3) for e in equipList])
        conn.commit()
        conn.close()

    def loadEquipDB(self, conditions:Optional[str] = None, ordering_args:Optional[str] = 'id ASC;') -> list[Equipment]:
        conn = self.getDBConn()
        cursor = conn.cursor()
        if conditions is None: rawList = cursor.execute(f'SELECT * from "equip" ORDER BY {ordering_args}').fetchall()
        else: rawList = cursor.execute(f'SELECT * from "equip" WHERE {conditions} ORDER BY {ordering_args}').fetchall()
        return [Equipment(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8]) for e in rawList]

    def getDictedEquipData(self, conditions:Optional[str] = None, ordering_args:Optional[str] = 'id ASC;') -> list[dict]:
        eList = self.loadEquipDB(conditions, ordering_args)
        return [ {  'id': e.id,
                    'name': e.name,
                    'rarity': e.rarity,
                    'img_path': e.img_path,
                    'is_ToP': e.is_ToP,
                    'conditions': [t for t in dictedTraits(self, e.conditions)],
                    'effects': [e.effect1, e.effect2, e.effect3]
                } for e in eList]

    def equipImgConfirm(self, equipID:str, webSRC:str):
        equipImgPath = self.getAssetPath(f'equips{os.sep}{equipID}.png')
        if os.path.isfile(equipImgPath) == False:
            r = self.scraper.getImage(webSRC)
            with open(f'{equipImgPath}', 'wb') as out_file:
                shutil.copyfileobj(r.raw, out_file)
            del r

    def findTrait(self, traitID:int, traitRarity:Optional[TraitRarity] = None) -> Trait: return findTrait(self, traitID, traitRarity)

    #endregion

    #region PROPERTIES
    @property
    def appRoot(self) -> str: return self.__appRoot
    @appRoot.setter
    def appRoot(self, appRoot:str) -> None:
        if hasattr(self, '__appRoot'): raise Exception
        elif os.path.exists(appRoot) is False: raise Exception
        elif os.path.isfile is True: raise Exception
        else: self.__appRoot = appRoot

    @property
    def config(self) -> API_CONFIG: return self.__config
    @config.setter
    def config(self, config:dict) -> None:
        if hasattr(self, '__appRoot'): raise Exception
        else: self.__config = API_CONFIG(config['asset_rel_root'].replace('[os.sep]', os.sep), config['db_last_updated'])

    @property
    def dbPath(self) -> str: return self.__joinpaths(self.appRoot, f'static{os.sep}assets{os.sep}database.db')
    #endregion