#!/usr/bin/env python3

import click
from pydantic_yaml import parse_yaml_raw_as

from wishlist.formatter.dim import DIMFormatter
from wishlist.models import Wishlist


@click.command()
@click.argument("filename")
@click.option("--output", prompt="Output file", help="File to write wishlist to")
def main(filename: str, output: str):
    click.echo(f"Reading in YAML from {filename} and building models...")
    with click.open_file(filename) as fh:
        wl = parse_yaml_raw_as(Wishlist, fh.read())

    click.echo(f"Writing out DIM wishlist to {output}...")
    dim = DIMFormatter(wl, output)
    dim.write()

    click.echo("Done.")


if __name__ == "__main__":
    main()
