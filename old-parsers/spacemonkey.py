#!/usr/bin/env python3

import argparse
import itertools
import re

import bs4

import d2wishlist.manifest as manifest
import d2wishlist.dim_additional as dim_additional

TAGMAP = {
    "pvp": "PvP",
    "pve": "PvE",
    "god-pve": "God-PvE",
    "mkb": "M+KB",
    "controller": "Controller",
    "dps": "DPS",
    "gambit": "Gambit",
}
TAGORDER = tuple(TAGMAP.keys())


def tagsort(x):
    return TAGORDER.index(x)


class LookupError(Exception):
    pass


class Recommendation(object):
    def __init__(self):
        self.tags = []
        self.perks = []
        self.masterwork = None

    def __str__(self):
        return f"tags={','.join(self.tags)} masterwork={self.masterwork}"

    def print_wishlist(self, parser, item, season, description):
        # sort and pretty up the tags
        tags = sorted(self.tags, key=tagsort)
        tag_string = " / ".join([TAGMAP.get(t, f"??? {t} ???") for t in tags])

        tagstr = ""
        tagstag = ""
        if tag_string:
            tagstr = f" ({tag_string})"
            tagstag = f"|tags:{','.join(tags)}"

        mw = ""
        if self.masterwork:
            mw = f" Recommended MW: {self.masterwork}."

        # translate perks to their hashes
        hashes = []
        for slot in self.perks:
            perkhashes = []
            for perk in slot:
                perkhash = None

                for sock in item.sockets:
                    try:
                        perkhash = [p for p in sock.values() if p.name == perk][0]
                    except IndexError:
                        continue
                    else:
                        break

                if perkhash:
                    perkhashes.append(perkhash)
                else:
                    raise LookupError(f"Could not find hash for perk {perk} on {item}!")
            hashes.append(perkhashes)

        print(f"// {item.name} (Season {season})")
        print(f'//notes:{parser.reviewer}{tagstr}: "{description}"{mw}{tagstag}')

        for roll in itertools.product(*hashes):
            perk_string = ",".join([p.hash for p in roll])
            print(f"dimwishlist:item={item.hash}&perks={perk_string}")

        print("")


class Weapon(object):
    def __init__(self, item):
        self.item = item
        self.variants = []
        self.recs = []
        self.description = []
        self.season = dim_additional.get_season(self.item)

    def find_variants(self):
        dupe_hashes = manifest.find_duplicates(self.item)
        for item_hash in dupe_hashes:
            item_hash = item_hash[0]
            if int(item_hash) == int(self.item.hash):
                continue
            item = manifest.InventoryItem(item_hash)
            season = dim_additional.get_season(item)
            if self.season == season:
                self.variants.append(item)

    def condense_pvp(self):
        pvp_rolls = [r for r in self.recs if "pvp" in r.tags]

        if len(pvp_rolls) != 2:
            return

        if pvp_rolls[0].masterwork != pvp_rolls[1].masterwork:
            return

        for i in range(len(pvp_rolls[0].perks)):
            l1 = pvp_rolls[0].perks[i]
            l2 = pvp_rolls[1].perks[i]
            if l1 != l2:
                return

        # Add unique tags from the second roll to the first
        tags = [t for t in pvp_rolls[1].tags if t not in pvp_rolls[0].tags]
        pvp_rolls[0].tags.extend(tags)

        self.recs.remove(pvp_rolls[1])

    def finish(self, parser):
        self.condense_pvp()
        self.find_variants()
        index = 0
        try:
            for r in self.recs:
                try:
                    descr = self.description[index]
                except IndexError:
                    descr = self.description[0]
                r.print_wishlist(parser, self.item, self.season, descr)
                for variant in self.variants:
                    r.print_wishlist(parser, variant, self.season, descr)
                index += 1
        except LookupError as e:
            print(f"Error while printing {self.item}: {e}")
            raise


class SpaceMonkey(object):
    def __init__(self, args):
        self.filename = args.filename
        self.heading = None
        self.reviewer = "SpaceMonkey"
        self.weapon = None

    def run(self):
        with open(self.filename, "r") as fh:
            soup = bs4.BeautifulSoup(fh, "html.parser")

        for node in soup.find_all(name="a", attrs={"href": re.compile("light.gg")}):
            item_id = re.match(
                r".*light.gg/db/items/([0-9]+)/.*", node.get("href")
            ).group(1)
            try:
                item = manifest.InventoryItem(item_id)
            except manifest.LookupError as e:
                print(f"ERROR: {e}")
                continue
            weapon = self.process_item(item, node)
            weapon.finish(self)

    def process_item(self, item, node):
        god_roll = Recommendation()
        rec_roll = Recommendation()
        rec_roll.tags = ["pve"]
        god_roll.tags = ["pve", "god-pve"]

        weapon = Weapon(item)
        weapon.recs.append(god_roll)
        weapon.recs.append(rec_roll)

        # The node we're passed is the <a> for the item link
        # The perks should be in the next <ul> after the <a>'s
        # parent <p>.
        perk_node = node.find_parent("p").find_next_sibling("ul")

        for socket_node in perk_node.find_all("li"):
            spans = socket_node.find_all("span")
            column_text = spans[0].get_text()
            god_perks = []
            rec_perks = []

            for span in spans[1:]:
                my_perks = rec_perks
                if len(span.get("class")) == 2:
                    my_perks = god_perks

                perk_text = (
                    re.sub(
                        " +",
                        " ",
                        span.string.replace(".", ",")
                        .replace("\n", "")
                        .strip()
                        .strip(","),
                    )
                    .replace("’", "'")
                    .replace("&", "and")
                    .replace("*", "")
                )
                if perk_text == "":
                    continue
                perks = [p.strip() for p in perk_text.split(",")]
                my_perks.extend(perks)

            if "Masterwork" in column_text:
                if god_perks and rec_perks:
                    god_roll.masterwork = ", ".join(god_perks)
                    rec_roll.masterwork = ", ".join(rec_perks)
                elif god_perks:
                    god_roll.masterwork = ", ".join(god_perks)
                    rec_roll.masterwork = ", ".join(god_perks)
                else:
                    god_roll.masterwork = ", ".join(rec_perks)
                    rec_roll.masterwork = ", ".join(rec_perks)
            else:
                if god_perks and rec_perks:
                    god_roll.perks.append(god_perks)
                    rec_roll.perks.append(rec_perks)
                elif god_perks:
                    god_roll.perks.append(god_perks)
                    rec_roll.perks.append(god_perks)
                else:
                    god_roll.perks.append(rec_perks)
                    rec_roll.perks.append(rec_perks)

        # The roll description text should be in a <span> of
        # a <p> following our <ul>
        description = None
        for p_node in perk_node.find_next_siblings("p", limit=5):
            for span_node in p_node.find_all("span"):
                if len(span_node.get_text()) > 10:
                    description = span_node.get_text()
                    break
            if description:
                break

        description = re.sub(" +", " ", description.replace("\n", "").strip())
        weapon.description.append(description)

        return weapon

    def process_line(self, rawline):
        line = rawline.strip()

        # Start of section, should probably split into separate output files
        if line.startswith("###"):
            self.heading = line[3:]
            return

        # Start of a new item section
        if line.startswith("**["):
            m = re.match(r".*light.gg/db/items/([0-9]+)/.*", line)
            item = InventoryItem(m.group(1))

            if self.weapon:
                if self.weapon.recs:
                    # We have a weapon already, and it has recommendations
                    # so finish it up and make a new one
                    self.weapon.finish(self)
                    self.weapon = Weapon(item)
                else:
                    # We have a weapon, but it has no recommendations
                    # so this is a variant item, usually an Adept
                    self.weapon.variants.append(item)
            else:
                # We have no weapon, so start one
                self.weapon = Weapon(item)

            return

        if line.startswith("Recommended"):
            rec = Recommendation()

            if "PvE" in line:
                rec.tags = ["pve", "mkb", "controller"]
            if "Controller PvP" in line:
                rec.tags = ["pvp", "controller"]
            if "MnK PvP" in line:
                rec.tags = ["pvp", "mkb"]

            self.weapon.recs.append(rec)

            return

        for perktype in ("Barrel:", "Sights:", "Magazine:", "Perk 1:", "Perk 2:"):
            if perktype in line:
                m = re.match(r".*: (.*)$", line)
                if "Eyes Up, Guardian" == m.group(1):
                    perks = ["Eyes Up, Guardian"]
                else:
                    perks = [p.strip() for p in m.group(1).rstrip(",").split(",")]
                self.weapon.recs[-1].perks.append(perks)
                return

        if "Masterwork:" in line:
            m = re.match(r".*Masterwork: ?(.*)$", line)
            self.weapon.recs[-1].masterwork = m.group(1)

            return

        if line.startswith(("Source:", "Curated Roll:", "- ")):
            return

        if self.weapon and len(line) > 10:
            self.weapon.description.append(line)
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser("SpaceMonkey Wishlist Translator")
    parser.add_argument("filename")
    args = parser.parse_args()

    wishlist = SpaceMonkey(args)
    wishlist.run()
