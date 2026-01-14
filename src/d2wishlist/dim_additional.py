#!/usr/bin/env python3

import json


def get_season(item: object) -> int:
    if "iconWatermark" in item.definition and item.iconWatermark in D2SeasonFromOverlay:
        return D2SeasonFromOverlay[item.iconWatermark]
    if (
        "collectibleHash" in item.definition
        and item.collectible().sourceHash in D2SeasonFromSource
    ):
        return D2SeasonFromSource[item.collectible().sourceHash]
    if item.hash and item.hash in D2Season:
        return D2Season[item.hash]
    return None


with open("d2-additional-info/output/watermark-to-season.json") as fh:
    D2SeasonFromOverlay = json.load(fh)
with open("d2-additional-info/output/source-to-season-v2.json") as fh:
    D2SeasonFromSource = json.load(fh)
with open("d2-additional-info/output/seasons.json") as fh:
    D2Season = json.load(fh)
