from typing import Optional

from pydantic import BaseModel, PrivateAttr, model_validator
from typing_extensions import Self

import destiny_manifest
import dim_additional


class Roll(BaseModel):
    tags: list[str]
    perks: list[list[str]]
    masterwork: list[str]
    text: str
    _perk_items: list = PrivateAttr(default_factory=list)

    def validate_perks(self, inv_item: destiny_manifest.InventoryItem) -> Self:
        """
        Loads the Destiny Manifest definitions for this roll's perks and
        confirms they fit correctly on the given inv_item.
        """
        for perk_set in self.perks:
            # Each set of perks should fall in the same socket of the
            # item definition, so let's use the first perk to find the
            # matching socket, then match the rest of the perks against
            # that.
            perk_set_socket = None
            for socket in inv_item.sockets:
                for socket_item in socket.values():
                    if socket_item.name.casefold() == perk_set[0].casefold():
                        perk_set_socket = socket
                        break
                if perk_set_socket:
                    break
            if not perk_set_socket:
                raise LookupError(
                    f"Could not find '{perk_set[0].casefold()}' on {inv_item}"
                )

            perk_item_map = {
                perk_set_socket[p].name.casefold(): perk_set_socket[p]
                for p in perk_set_socket
            }
            perk_set_items = []
            for perk in perk_set:
                try:
                    perk_set_items.append(perk_item_map[perk.casefold()])
                except KeyError:
                    raise LookupError(
                        f"Could not find '{perk.casefold()}' on {inv_item} socket: {perk_item_map.keys()}"
                    )
            self._perk_items.append(perk_set_items)

        return self


class Item(BaseModel):
    name: str
    hash: int | list[int]
    rolls: list[Roll]
    season: Optional[int] = None
    _inventory_item: destiny_manifest.InventoryItem
    _variants: list = PrivateAttr(default_factory=list)

    @model_validator(mode="after")
    def validate_inventory_item(self) -> Self:
        """Loads the Destiny Manifest definition for this item and checks the rolls for valid perks."""
        # if hash was given a list, convert the first one to our hash
        # and make the rest into variants
        if isinstance(self.hash, list):
            primary = self.hash[0]
            for variant in self.hash[1:]:
                item = destiny_manifest.InventoryItem(variant)
                self._variants.append(item)
            self.hash = primary

        self._inventory_item = destiny_manifest.InventoryItem(self.hash)

        for roll in self.rolls:
            roll.validate_perks(self._inventory_item)

        if not self.season:
            self.season = dim_additional.get_season(self._inventory_item)

        dupe_hashes = destiny_manifest.find_duplicates(self._inventory_item)
        for item_hash in dupe_hashes:
            item_hash = item_hash[0]
            item = destiny_manifest.InventoryItem(item_hash)
            season = dim_additional.get_season(item)
            if self.season == season:
                self._variants.append(item)

        return self


class Wishlist(BaseModel):
    title: str
    description: str
    author: str
    wishlist: list[Item]
