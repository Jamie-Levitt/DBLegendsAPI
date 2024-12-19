from __future__ import annotations
from typing import Optional, Union, TYPE_CHECKING

from API.FlagTypes import DBTableType, ConfigType
from API.DataTypes import Equipment

if TYPE_CHECKING:
    from API.utils import DBAPIConnection

def findInDB(APIConn:DBAPIConnection, itemID:Union[str,int], tableName:str, fetchCount:Optional[int] = None, ordering_args:Optional[str] = 'id ASC;'):
    conn = APIConn.getDBConn()
    cursor = conn.cursor()
    if fetchCount is None: r = cursor.execute(f'SELECT * FROM "{tableName}" where id = {itemID} ORDER BY {ordering_args}').fetchone()
    elif fetchCount == -1: r = cursor.execute(f'SELECT * FROM "{tableName}" where id = {itemID} ORDER BY {ordering_args}').fetchall()
    else: r = cursor.execute(f'SELECT * FROM "{tableName}" where id = {itemID} ORDER BY {ordering_args}').fetchmany(fetchCount)
    conn.close()
    return r

def _get_args_dict(fn, args, kwargs):
    args_names = fn.__code__.co_varnames[:fn.__code__.co_argcount]
    return {**dict(zip(args_names, args)), **kwargs}

def checkForTable(type:DBTableType):
    def decorator(func):
        def wrapper(*args, **kwargs):
            APIConn = _get_args_dict(func, args, kwargs)['APIConn']
            config = APIConn.loadConfig(ConfigType.DB, type.name)['DATABASE-SOURCE']
            sqlCommand = f"\nCREATE TABLE IF NOT EXISTS {type.name.lower()} (\n"
            for i, arg in enumerate(config):
                if i == len(config) - 1: sqlCommand += f"{arg}\n"
                else: sqlCommand += f"{arg},\n"
            sqlCommand += ")\n"
            
            conn = APIConn.getDBConn()
            cursor = conn.cursor()
            cursor.execute(sqlCommand)
            conn.commit()
            conn.close()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def loadEquipDB(APIConn:DBAPIConnection) -> list[Equipment]:
    conn = APIConn.getDBConn()
    cursor = conn.cursor()
    rawList = cursor.execute('SELECT * from "equip"').fetchall()
    conn.close()
    return [Equipment(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[8], e[9]) for e in rawList]