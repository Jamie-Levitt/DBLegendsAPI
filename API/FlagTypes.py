from enum import Flag

class ConfigType(Flag):
    API = "API"
    SCRAPER = "Scraper"
    DB = "Database"

class DBTableType(Flag):
    TRAIT = "TRAIT"
    EQUIP = "EQUIP"

class page_root(Flag):
    ROOT = "ROOT"
    TRAIT = "TRAIT"
    CHARS_ROOT = "CHARS_ROOT"
    CHAR = "CHAR"
    EQUIPS_ROOT = "EQUIPS_ROOT"
    EQUIP = "EQUIP"

    @classmethod
    def is_pr(cls, col) -> bool:
        if isinstance(col, cls): col = col.value
        if not col in cls.__members__: return False
        else: return True