from dataclasses import dataclass, field, fields, replace


@dataclass
class BaseItem:
    item_type: str = "base"
    source_domain: str | None = None
    name: str = None
    price: str = None
    currency: str | None = None
    url: str = None
    brand: str | None = None
    country: str | None = None
    subtype: str | None = None
    description: str | None = None
    full_description: str | None = None
    characteristics: list[str] = field(default_factory=list)
    additional_info: str | None = None
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
