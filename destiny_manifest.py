#!/usr/bin/env python3

import sqlite3
import json

from functools import lru_cache

manifest = sqlite3.connect("manifest.sqlite3")

# Table names
INVITEMDEF = "DestinyInventoryItemDefinition"
PLUGSETDEF = "DestinyPlugSetDefinition"

# socketCategories[].socketCategoryHash for weapon perks
WEAPON_PERKS = 4241085061
ARMOR_PERKS = 2518356196

# Some items, like Exotic Class Items, don't have a plug set in the manifest to define
# the available options, so we can specify them here to override the manifest
# SOCKET_OVERRIDES[itemHash][socket][perkHash]
SOCKET_OVERRIDES = {
    # Stoicism
    266021826: {
        10: [
            1476923952,
            1476923953,
            1476923954,
            3573490509,
            3573490508,
            3573490511,
            3573490510,
            3573490505,
        ],
        11: [
            1476923955,
            1476923956,
            1476923957,
            3573490504,
            3573490507,
            3573490506,
            3573490501,
            3573490500,
        ],
    },
    # Solipsism
    2273643087: {
        10: [
            1476923952,
            1476923953,
            1476923954,
            183430248,
            183430255,
            183430252,
            183430253,
            183430250,
        ],
        11: [
            1476923955,
            1476923956,
            1476923957,
            183430251,
            183430254,
            183430249,
            183430246,
            183430247,
        ],
    },
    # Relativism
    2809120022: {
        10: [
            1476923952,
            1476923953,
            1476923954,
            3751917999,
            3751917998,
            3751917997,
            3751917996,
            3751917995,
        ],
        11: [
            1476923955,
            1476923956,
            1476923957,
            3751917994,
            3751917993,
            3751917992,
            3751917991,
            3751917990,
        ],
    },
}


@lru_cache(maxsize=128)
def query_manifest(table, hash):
    id = sql_id(hash)
    c = manifest.cursor()
    r = c.execute(f"SELECT json FROM {table} WHERE id = ?", (id,))
    row = r.fetchone()
    if not row:
        raise LookupError(f"No {table} for {hash}")
    itemdef = json.loads(row[0])
    return itemdef


def sql_id(hash):
    id = int(hash)
    if (id & (1 << (32 - 1))) != 0:
        id = id - (1 << 32)
    return id


class LookupError(Exception):
    pass


class PlugSet(object):
    def __init__(self, hash):
        self.hash = str(hash)
        self.definition = query_manifest(PLUGSETDEF, hash)

    def reusable_plug_items(self):
        return [
            InventoryItem(p["plugItemHash"])
            for p in self.definition["reusablePlugItems"]
        ]


class InventoryItem(object):
    def __init__(self, hash):
        self.hash = str(hash)
        self.definition = query_manifest(INVITEMDEF, hash)
        self.name = self.definition["displayProperties"]["name"]
        self.sockets = []
        self.load_sockets()

    def __str__(self):
        return f"{self.name} [{self.hash}]"

    def __repr__(self):
        return f"{self.name} [{self.hash}]"

    def pprint(self):
        print(self)
        for s in self.sockets:
            print("  - socket:")
            for perk in s:
                print(f"    - {s[perk]}")

    def load_sockets(self):
        if "sockets" not in self.definition:
            return

        # Load override perks if available
        if int(self.hash) in SOCKET_OVERRIDES:
            sockets = SOCKET_OVERRIDES[int(self.hash)]
            for s in sockets:
                plugs = dict()
                for perk in sockets[s]:
                    plugitem = InventoryItem(perk)
                    plugs[plugitem.hash] = plugitem
                self.sockets.append(plugs)
            return

        # Find sockets for weapon perks
        socket_indexes = [
            s["socketIndexes"]
            for s in self.definition["sockets"]["socketCategories"]
            if s["socketCategoryHash"] in (WEAPON_PERKS, ARMOR_PERKS)
        ][0]
        for i in socket_indexes:
            plugs = dict()
            entry = self.definition["sockets"]["socketEntries"][i]

            # plug options specified directly in the item definition
            for plug in entry["reusablePlugItems"]:
                plugitem = InventoryItem(plug["plugItemHash"])
                plugs[plugitem.hash] = plugitem

            # plug options specified via plug sets (either randomized or reusable)
            plug_type = None
            for t in ("randomizedPlugSetHash", "reusablePlugSetHash"):
                if t in entry:
                    plug_type = t
                    break

            if plug_type:
                plugset = PlugSet(entry[plug_type])
                for plugitem in plugset.reusable_plug_items():
                    plugs[plugitem.hash] = plugitem

            self.sockets.append(plugs)
