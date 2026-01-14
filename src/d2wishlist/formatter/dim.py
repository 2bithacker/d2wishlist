import itertools

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


class DIMFormatter(object):
    def __init__(self, wishlist, output_file):
        self.wishlist = wishlist
        self.output_file = output_file
        self.written_perks = set()

    def write(self):
        with open(self.output_file, "w") as fh:
            fh.write(f"title:{self.wishlist.title}\n")
            fh.write(f"description:{self.wishlist.description}\n\n")

            for item in self.wishlist.wishlist:
                for roll in item.rolls:
                    self._write_roll(fh, item, roll, item._inventory_item)
                    for variant in item._variants:
                        self._write_roll(fh, item, roll, variant)

    def _write_roll(self, fh, item, roll, inv_item):
        tags = sorted(roll.tags, key=tag_sort)
        tag_string = " / ".join([TAG_MAP.get(t, f"??? {t} ???") for t in tags])

        # note_tags is the tags to put after the author in the notes section
        # dim_tags is the tags to put after the notes for DIM to process
        note_tags = dim_tags = ""
        if tag_string:
            note_tags = f" ({tag_string})"
            dim_tags = f"|tags:{','.join(tags)}"

        masterwork = ""
        if roll.masterwork:
            masterwork = f" Recommended MW: {', '.join(roll.masterwork)}."

        fh.write(f"// {inv_item.name} (Season {item.season})\n")
        fh.write(
            f'//notes:{self.wishlist.author}{note_tags}: "{roll.text}"{masterwork}{dim_tags}\n'
        )

        for perk_combo in itertools.product(*roll._perk_items):
            perk_string = ",".join([p.hash for p in perk_combo])
            roll_string = f"item={inv_item.hash}&perks={perk_string}"
            if roll_string not in self.written_perks:
                self.written_perks.add(roll_string)
                fh.write(f"dimwishlist:{roll_string}\n")

        fh.write("\n")
