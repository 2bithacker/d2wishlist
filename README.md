# d2wishlist

Create and validate DIM-style wishlists

## Usage

This project is using [uv](https://docs.astral.sh/uv/), so initial setup is `uv sync`.

Next, you'll need a copy of the Destiny 2 Manifest, this can be fetched using `fetch_manifest.sh`:

```
$ ./fetch_manifest.sh
Current manifest version: 229199.24.10.30.2000-1-bnet.57522
=== Fetching manifest archive...
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 23.4M  100 23.4M    0     0  45.5M      0 --:--:-- --:--:-- --:--:-- 45.5M
=== Extracting manifest database...
Archive:  manifest.sqlite.zip
 extracting: world_sql_content_cd9d69b569421ae2921a88739507f991.content
```

You'll also need DIM's [d2-additional-info](https://github.com/DestinyItemManager/d2-additional-info) repo checked out in here, as we use their JSON data to figure some stuff out.

Finally, you need a wishlist definition in YAML. The format goes something like this:

```(yaml)
---
title: SpaceMonkey's Weapon Guide - Dawning 2025
description: https://docs.google.com/document/d/1KGxePntz2loCYlAhdKm0fJyyf_YURJ1Zd7L1smsu4-c/edit?usp=sharing
author: SpaceMonkey
wishlist:
  - name: Permafrost
    hash: 2316331767
    rolls:
      - tags: [pve, god-pve]
        perks:
          - [Volatile Launch, Confined Launch]
          - [High-Velocity Rounds]
          - [Attrition Orbs, Rimestealer]
          - [Crystalline Corpsebloom]
        masterwork: [Reload, Blast Radius]
        text: >-
          This is about two or three years too late. A great looking add clear and utility GL,
          held back by the fact that area denial frames exist and invalidate this thing's entire
          purpose. Honestly, this still ticks a lot of boxes for me personally, so I'll be going
          for one in the hopes that the archetype can make a comeback.
```

Now, you can run `wishlist_creator.py` on that post to generate the wishlist:

```
$ uv run wishlist_creator.py --output=output/s28-dawning.txt ~/wishlist/spacemonkey/yaml/s28-dawning.yaml
Reading in /home/chip/wishlists/spacemonkey/yaml/s28-dawning.yaml...
https://docs.google.com/document/d/1KGxePntz2loCYlAhdKm0fJyyf_YURJ1Zd7L1smsu4-c/edit?usp=sharing by SpaceMonkey with 3 items.
Creating objects...  [####################################]  100%
Writing wishlist...  [####################################]  100%
$ head output/s28-dawning.txt
title:SpaceMonkey's Weapon Guide - Dawning 2025
description:https://docs.google.com/document/d/1KGxePntz2loCYlAhdKm0fJyyf_YURJ1Zd7L1smsu4-c/edit?usp=sharing

// Permafrost (Season 28)
//notes:SpaceMonkey (PvE / God-PvE): "This is about two or three years too late. A great looking add clear and utility GL, held back by the fact that area denial frames exist and invalidate this thing's entire purpose. Honestly, this still ticks a lot of boxes for me personally, so I'll be going for one in the hopes that the archetype can make a comeback." Recommended MW: Reload, Blast Radius.|tags:pve,god-pve
dimwishlist:item=2316331767&perks=1478423395,2822142346,243981275,2922950962
dimwishlist:item=2316331767&perks=1478423395,2822142346,1955165503,2922950962
dimwishlist:item=2316331767&perks=1844523823,2822142346,243981275,2922950962
dimwishlist:item=2316331767&perks=1844523823,2822142346,1955165503,2922950962
```
