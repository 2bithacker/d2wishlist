import typer
from pydantic_yaml import parse_yaml_raw_as
from typing_extensions import Annotated

from d2wishlist.formatter.dim import DIMFormatter
from d2wishlist.models import Wishlist


def create(
    filename: Annotated[
        str, typer.Argument(help="Filename of YAML-formatted wishlist to process")
    ],
    output: Annotated[
        str, typer.Option(help="Filename to use for DIM-format wishlist output")
    ],
):
    print(f"Reading in YAML from {filename} and building models...")
    with open(filename) as fh:
        wl = parse_yaml_raw_as(Wishlist, fh.read())

    print(f"Writing out DIM wishlist to {output}...")
    dim = DIMFormatter(wl, output)
    dim.write()

    print("Done.")
