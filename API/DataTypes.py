from typing import NamedTuple

from enum import IntEnum
from API.FlagTypes import page_root

#region API-Typing
class API_CONFIG(NamedTuple):
    asset_rel_root: str
    db_last_updated: str

class DB_CONFIG(NamedTuple):
    TRAIT: dict
    EQUIP: dict
    CHARS: dict

class SCRAPER_CONFIG(NamedTuple):
    rootURL: str
    page_roots: dict[page_root, str]
#endregion

#region DBL-Items
class TraitRarity(IntEnum):
    standard = 0
    bronze = 1
    silver = 2
    gold = 3
    ultra = 4

class Trait(NamedTuple):
    id: int
    rarity: TraitRarity
    name: str
    desc: str

class EquipRarity(IntEnum):
    iron = 0
    bronze = 1
    silver = 2
    gold = 3
    unique = 4
    platinum = 5
    event = 6

    awakenedBronze = 10
    awakenedSilver = 20
    awakenedGold = 30
    awakenedUnique = 40

class Equipment(NamedTuple):
    id: int
    name: str
    rarity: EquipRarity
    img_path: str
    is_ToP: bool
    conditions: str
    effect1: str
    effect2: str
    effect3: str

#endregion