from dataclasses import dataclass, field, replace, fields
from typing import List, Optional


@dataclass
class BaseItem:
    item_type: str = "base"
    source_domain: Optional[str] = None
    name: str = None
    price: str = None
    currency: Optional[str] = None
    url: str = None
    brand: Optional[str] = None
    country: Optional[str] = None
    subtype: Optional[str] = None
    description: Optional[str] = None
    full_description: Optional[str] = None
    characteristics: List[str] = field(default_factory=list)
    additional_info: Optional[str] = None
    update_status: str = None

    def copy(self):
        return replace(self)
    
    def fields(self):
        return fields(self)

@dataclass
class MaltItem(BaseItem):
    item_type: str = "malt"

@dataclass
class HopItem(BaseItem):
    item_type: str = "hop"

@dataclass
class YeastItem(BaseItem):
    item_type: str = "yeast"
