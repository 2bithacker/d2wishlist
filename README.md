# Destiny 2 Wishlist Tools

Create and validate [Destiny Item Manager](https://destinyitemmanager.com/)-style wishlists

## Installation

Recommended installation is with `pipx`:

```(shell)
# pipx install .
  installed package d2wishlist 1.0.0, installed using Python 3.12.3
  These apps are now globally available
    - d2wishlist_creator
done! ✨ 🌟 ✨
```

In order to run `d2wishlist_creator` you'll also need to download the Destiny 2 Manifest and checkout the [d2-additional-info](https://github.com/DestinyItemManager/d2-additional-info). The `fetch_manifest.sh` script is provided to help with grabbing the manifest.

## Usage

To create a DIM-style wishlist, you'll need a YAML-formatted mostly human-readable wishlist to start with. An example [wishlist.yaml](examples/wishlist.yaml) is provided as a starting point.

Once a YAML file has been crafted, it can be converted like so:

```(shell)
$ d2wishlist_creator --output examples/wishlist.txt examples/wishlist.yaml
Reading in YAML from examples/wishlist.yaml and building models...
Writing out DIM wishlist to examples/wishlist.txt...
Done.
$ head examples/wishlist.txt
title:Example Wishlist
description:Just an example of the YAML wishlist format

// Duty Bound (Season 28)
//notes:2bithacker (PvE): "This is a block of descriptive text about this particular roll, it's freeform, but will be collapsed into a single line in the final output." Recommended MW: Range, Reload.|tags:pve
dimwishlist:item=260532765&perks=839105230,1431678320,3828510309,1226351311
dimwishlist:item=260532765&perks=839105230,1431678320,3828510309,3400784728
dimwishlist:item=260532765&perks=839105230,1431678320,2387244414,1226351311
dimwishlist:item=260532765&perks=839105230,1431678320,2387244414,3400784728
dimwishlist:item=260532765&perks=839105230,3177308360,3828510309,1226351311
```
