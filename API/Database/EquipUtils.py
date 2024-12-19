from __future__ import annotations
from typing import TYPE_CHECKING

import os

from API.DataTypes import Equipment, EquipRarity, TraitRarity
from API.FlagTypes import page_root

if TYPE_CHECKING:
    from API.utils import DBAPIConnection

def isToP(equipName:str) -> bool:
    if equipName.strip().startswith('[ToP]'): return True
    else: return False

def equipDBCheck(APIConn:DBAPIConnection, equipID:int) -> bool:
    r = APIConn.findInDB(equipID, 'equip')
    if r is not None: return True
    else: return False

def __getEquipTags(APIConn:DBAPIConnection, equipID:int) -> Equipment:
    soup = APIConn.loadPageData(page_root.EQUIP, equipID)
    conDivs = soup.find_all(class_="trait-container-equip mb-4 ms-4")
    if len(soup.find_all(class_="trait-container mb-4 ms-4")) != 0: conDivs.insert(1, soup.find(class_="trait-container mb-4 ms-4"))

    conList = []
    conditions = ''
    if len(conDivs) != 0:
        for conDiv in conDivs:
            cons = conDiv.find_all(class_="trait-thumb traitzoom my-3")
            conList.append([(c.get('href', 'No href attribute').removeprefix('/traits/'), c.find('div', class_=lambda cl: 'title' in cl).get('class')[1]) for c in cons])

        for i, con in enumerate(conList):
            if type(con) == list:
                for j, c in enumerate(con):
                    r = c[1]
                    c = c[0]
                    APIConn.findTrait(c, TraitRarity[r])
                    if j < len(con) - 1:
                        conditions += f'{c} && '
                    else: 
                        if i < len(conList) - 1: conditions += f'{c} || '
                        else: conditions += f'{c}'
            else:
                APIConn.findTrait(con[0], TraitRarity[con[1]])
                if i < len(conList) - 1:
                    conditions += f'{con[0]} || '
                else:
                    conditions += f'{con[0]}'

    effectsList = soup.find_all(class_="card text-white bg-dark mb-3")
    effects = []
    for i, effect in enumerate(effectsList):
        effects.append(effect.text.replace(' - OR - ', '||'))
    
    return {'conditions': conditions, 'effects': effects}

def awakenCheck(soup) -> EquipRarity:
    baseRarity = int(soup.get('data-rarity', 'No rarity attribute'))
    if 'awakened' in soup.find('div', class_='equip-thumb equip-item').get('data-rarity', 'No rarity attribute'): baseRarity *= 10
    return EquipRarity(baseRarity)

def downloadEquipData(APIConn:DBAPIConnection) -> list[Equipment]:
    soup = APIConn.loadPageData(page_root.EQUIPS_ROOT)
    baseRawEquipList = soup.find_all(class_="equip-list equip-listing equipzoom")
    rawEquipList = soup.find_all(class_="equip-thumb equip-item")
    imgEquipList = soup.find_all(class_="art")
    equipList = []

    for i in range(len(baseRawEquipList) - 1):
        baseRef = baseRawEquipList[i]
        rawRef = rawEquipList[i]
        id = baseRef.get('href', 'No href attribute').removeprefix('/equip/')
        if equipDBCheck(APIConn, id) is True:
            APIConn.equipImgConfirm(id, imgEquipList[i].get('src', 'No src attribute').removeprefix('assets/'))
            continue
        name = rawRef.get('title', 'No title attribute').strip()
        rarity = awakenCheck(baseRef)
        if isToP(name) is True:
            name = name.strip().removeprefix('[ToP]').strip()
            is_ToP = True
        else: is_ToP = False
        img_path = APIConn.buildRelAssetPath(f'equips{os.sep}{id}.png')
        eData = __getEquipTags(APIConn, id)
        conditions = eData['conditions']
        effect1 = eData['effects'][0].strip()
        effect2 = eData['effects'][1].strip()
        effect3 = eData['effects'][2].strip()

        APIConn.equipImgConfirm(id, imgEquipList[i].get('src', 'No src attribute').removeprefix('assets/'))

        equipList.append(Equipment(id, name, rarity, img_path, is_ToP, conditions, effect1, effect2, effect3))
    return equipList
