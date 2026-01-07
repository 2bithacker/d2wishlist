#!/usr/bin/env python3

import fileinput
import urllib.parse

from rich.console import Console

from destiny_manifest import InventoryItem, LookupError

console = Console()


class ValidationError(Exception):
    pass


class DIMWishlist(object):
    def __init__(self):
        self.last_item = None
        self.lineno = 0

    def validate(self, item, perks):
        roll = dict()
        perk_items = dict()

        for perkhash in perks:
            try:
                perk_items[perkhash] = InventoryItem(perkhash)
            except LookupError as e:
                raise ValidationError(f"Perk {perkhash} doesn't exit in manifest: {e}")

        perks_to_find = perks.copy()

        for slot in range(0, len(item.sockets)):
            socket = item.sockets[slot]
            for perk in perks_to_find:
                if perk in socket:
                    roll[slot] = socket[perk]
                    perks_to_find.remove(perk)
                    break

        if perks_to_find:
            raise ValidationError(
                f"Unable to find socket for perks: {', '.join([str(perk_items[x]) for x in perks_to_find])}"
            )

        if len(perks) > len(roll):
            r = set([str(x.hash) for x in roll.values()])
            missing = [perk_items[x] for x in perks if x not in r]
            raise ValidationError(
                f"Perks not in manifest: {', '.join([str(x) for x in missing])}"
            )

        return roll

    def process_item(self, line):
        # dimwishlist:item=3969379530&perks=839105230,1087426260,3619207468,3047969693
        itemdict = urllib.parse.parse_qs(line[12:])
        itemhash = itemdict["item"][0]

        try:
            if self.last_item and self.last_item.hash == itemhash:
                item = self.last_item
            else:
                item = InventoryItem(itemhash)
                self.last_item = item

            self.validate(item, itemdict["perks"][0].split(","))

        except ValidationError as e:
            console.print(f"{self.lineno} [blue]{item}[/blue] [red]Error![/red] {e}")
        except LookupError as e:
            console.print(
                f"{self.lineno} [blue]{itemhash}[/blue] [red]Error![/red] {e}"
            )

    def process_line(self, rawline):
        line = rawline.strip()
        self.lineno += 1

        if line == "":
            return
        if line.startswith("//"):
            return

        if line.startswith("title:"):
            console.print(f"[bold blue]{line[6:]}[/bold blue]")
            return
        if line.startswith("description:"):
            console.print(f"[blue]{line[12:]}[/blue]")
            return

        if line.startswith("dimwishlist:"):
            if "#" in line:
                (line, notes) = line.split("#", 1)
            try:
                self.process_item(line)
            except:
                console.print(f"[red]Error[/red] while processing line {self.lineno}")
                console.print(line)
                raise
            return

        print(f"Unhandled line: {line}")


if __name__ == "__main__":
    parser = DIMWishlist()
    for line in fileinput.input(encoding="utf-8"):
        parser.process_line(line)
