from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from API.Database.DBTools import checkForTable

from API.DataTypes import Trait, TraitRarity
from API.FlagTypes import DBTableType

if TYPE_CHECKING:
    from API.utils import DBAPIConnection

@checkForTable(DBTableType.TRAIT)
def __addTraitToDB(APIConn:DBAPIConnection, trait:Trait):
    conn = APIConn.getDBConn()
    cursor = conn.cursor()
    cursor.execute('''
                       REPLACE INTO trait (id, rarity, name, desc)
                       VALUES (?,?,?,?)
                        ''', (trait.id, trait.rarity.value, trait.name, trait.desc))
    conn.commit()
    conn.close()

@checkForTable(DBTableType.TRAIT)
def findTrait(APIConn:DBAPIConnection, traitID:int, traitRarity:Optional[TraitRarity] = None) -> Trait:
    r = APIConn.findInDB(traitID, 'trait')
    if r is not None: return Trait(r[0], TraitRarity(r[1]), r[2], r[3])
    else: 
        rawData = APIConn.scrapeTraitData(traitID)
        trait = Trait(traitID, traitRarity, rawData['name'], rawData['desc'])
        __addTraitToDB(APIConn, trait)
        return trait

def parseTraits(apiConn:DBAPIConnection, traitStr:str) -> list[Trait]:
    splitList = traitStr.split(' || ')
    return [[findTrait(apiConn, t) for t in subStr.split(' && ') if t is not ''] for subStr in splitList]

def dictedTraits(apiConn:DBAPIConnection, traitStr:str) -> list[dict]:
    parsedList = parseTraits(apiConn, traitStr)
    traits = []
    for tr in parsedList:
        if type(tr) == list:
            traits.append([{'id': t.id, 'name': t.name, 'rarity': t.rarity.value} for t in tr])
        else:
            traits.append({'id': tr.id, 'name': tr.name, 'rarity': tr.rarity.value})
    return traits