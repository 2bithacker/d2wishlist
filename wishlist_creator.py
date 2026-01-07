#!/usr/bin/env python3

import itertools

import click
import yaml

import destiny_manifest
import dim_additional

TAG_MAP = {
    "pvp": "PvP",
    "pve": "PvE",
    "god-pve": "God-PvE",
    "god-pvp": "God-PvP",
    "mkb": "M+KB",
    "controller": "Controller",
    "dps": "DPS",
    "gambit": "Gambit",
}
TAG_ORDER = tuple(TAG_MAP.keys())


def tag_sort(x):
    return TAG_ORDER.index(x)


class LookupError(Exception):
    pass


class Recommendation(object):
    def __init__(self):
        self.tags = []
        self.perks = []
        self.masterwork = None
        self.description = None

    def __str__(self):
        return f"tags={','.join(self.tags)} masterwork={self.masterwork}"

    def write_wishlist(self, fh, wishlist, item_def, item):
        # sort and pretty up the tags
        tags = sorted(self.tags, key=tag_sort)
        tag_string = " / ".join([TAG_MAP.get(t, f"??? {t} ???") for t in tags])

        tag_str = ""
        tags_tag = ""
        if tag_string:
            tag_str = f" ({tag_string})"
            tags_tag = f"|tags:{','.join(tags)}"

        mw = ""
        if self.masterwork:
            mw = f" Recommended MW: {self.masterwork}."

        # translate perks to their hashes
        hashes = []
        for slot in self.perks:
            perk_hashes = []
            for perk in slot:
                perk_hash = None

                for sock in item.sockets:
                    try:
                        perk_hash = [p for p in sock.values() if p.name == perk][0]
                    except IndexError:
                        continue
                    else:
                        break

                if perk_hash:
                    perk_hashes.append(perk_hash)
                else:
                    raise LookupError(f"Could not find hash for perk {perk} on {item}!")
            hashes.append(perk_hashes)

        fh.write(f"// {item.name} (Season {item_def.season})\n")
        fh.write(
            f'//notes:{wishlist.author}{tag_str}: "{self.description}"{mw}{tags_tag}\n'
        )

        for roll in itertools.product(*hashes):
            perk_string = ",".join([p.hash for p in roll])
            roll_string = f"item={item.hash}&perks={perk_string}"
            if roll_string not in item_def.written_perks:
                item_def.written_perks.add(roll_string)
                fh.write(f"dimwishlist:{roll_string}\n")

        fh.write("\n")


class ItemDefinition(object):
    def __init__(self, item_hash):
        self.item = destiny_manifest.InventoryItem(item_hash)
        self.variants = []
        self.recs = []
        self.season = dim_additional.get_season(self.item)
        self.written_perks = set()

    def find_variants(self):
        dupe_hashes = destiny_manifest.find_duplicates(self.item)
        for item_hash in dupe_hashes:
            item_hash = item_hash[0]
            if int(item_hash) == int(self.item.hash):
                continue
            item = destiny_manifest.InventoryItem(item_hash)
            season = dim_additional.get_season(item)
            if self.season == season:
                self.variants.append(item)

    def write_wishlist(self, fh, wishlist):
        self.find_variants()
        for roll in self.recs:
            roll.write_wishlist(fh, wishlist, self, self.item)
            for variant in self.variants:
                roll.write_wishlist(fh, wishlist, self, variant)


class Wishlist(object):
    def __init__(self, input, output):
        self.input_file = input
        self.output_file = output
        self.data = None
        self.items = []

        self.title = None
        self.description = None
        self.author = None

    def run(self):
        self._read_input()

        with click.progressbar(
            self.data["wishlist"], label="Creating objects..."
        ) as bar:
            for item in bar:
                self._process_item(item)

        with click.open_file(self.output_file, "w") as fh:
            fh.write(f"title:{self.title}\n")
            fh.write(f"description:{self.description}\n\n")

            with click.progressbar(self.items, label="Writing wishlist...") as bar:
                for item in bar:
                    self._write_output(fh, item)

    def _read_input(self):
        click.echo(f"Reading in {click.format_filename(self.input_file)}...")
        with click.open_file(self.input_file, "r") as fh:
            self.data = yaml.load(fh, Loader=yaml.Loader)

        self.title = self.data["title"]
        self.description = self.data["description"]
        self.author = self.data["author"]

        click.echo(
            f"{self.description} by {self.author} with {len(self.data['wishlist'])} items."
        )

    def _process_item(self, item_data: dict):
        if isinstance(item_data["hash"], int):
            item_def = ItemDefinition(item_data["hash"])
        else:
            item_def = ItemDefinition(item_data["hash"][0])
            item_def.variants.extend(
                [destiny_manifest.InventoryItem(hash) for hash in item_data["hash"][1:]]
            )
        for roll_data in item_data["rolls"]:
            roll = Recommendation()
            roll.tags = roll_data["tags"]
            for perk_data in roll_data["perks"]:
                roll.perks.append(perk_data)
            roll.masterwork = ", ".join(roll_data["masterwork"])
            roll.description = roll_data["text"]
            item_def.recs.append(roll)
        self.items.append(item_def)

    def _write_output(self, fh, item_def):
        item_def.write_wishlist(fh, self)


@click.command()
@click.argument("filename")
@click.option("--output", prompt="Output file", help="File to write wishlist to")
def main(filename: str, output: str):
    wishlist = Wishlist(filename, output)
    wishlist.run()


if __name__ == "__main__":
    main()
