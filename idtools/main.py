# -*- coding: utf-8 -*-
"""
    idtools.main
    ~~~~~~~~~~~~

    Main entry point for command line invocation.

    :copyright: (c) 2016 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""
import sys
from itertools import zip_longest

import click
import requests

from . import __version__
from .utils import get_handle

__all__ = []


@click.group()
@click.version_option(__version__)
@click.option("--idx", default=1,
              help="Column index (1-based) of the identifiers. Default: 1.")
@click.option("--sep", default="\t",
              help="Column separator. Default: (the tab character).")
@click.option("--num-ignore", default=1,
              help="The number of lines from the header to ignore for ID "
                   "conversion. Default: 1.")
@click.option("--fallback", default="NA",
              help="String to use when ID can not be mapped. Default: 'NA'.")
@click.option("--enclosing-chars", default="",
              help="Characters enclosing the identifiers which will be "
              "discarded. Default: (the empty string).")
@click.pass_context
def cli(ctx, idx, sep, num_ignore, fallback, enclosing_chars):
    """"""
    ctx.params["idx"] = idx
    ctx.params["sep"] = sep
    ctx.params["num_ignore"] = num_ignore
    ctx.params["fallback"] = fallback
    ctx.params["enclosing_chars"] = enclosing_chars


## From the Python docs
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.File("w"), default="-")
@click.pass_context
def ensg2sym(ctx, input, output):
    """"""
    id_idx = ctx.parent.params["idx"]
    encl = ctx.parent.params["enclosing_chars"]
    len_encl = len(encl)
    sep = ctx.parent.params["sep"]
    fallback = ctx.parent.params["fallback"]

    ignored, processed = [], []
    with get_handle(input) as src:
        for lineno, line in enumerate(src, start=0):
            if lineno < ctx.parent.params["num_ignore"]:
                ignored.append(line.strip())
                continue
            cols = line.strip().split(sep)

            raw_id = cols[id_idx - 1]
            raw_id = raw_id[len_encl:-len_encl]

            processed.append({
                "pre": sep.join(cols[:id_idx-1]),
                "id": raw_id,
                "post": sep.join(cols[id_idx:]),
            })

    raw_ids = set([x["id"] for x in processed])
    id_items = []

    n_processed = 0
    for id_group in (filter(None, x) for x in grouper(raw_ids, 1000)):
        ids = list(id_group)
        if not n_processed:
            print("Starting ID processing ...", file=sys.stderr)
        r = requests.post("http://rest.ensembl.org/lookup/id/homo_sapiens",
                          json={"ids": ids})
        if r.status_code != 200:
            print(r.content, file=sys.stderr)
        id_items.extend(list(r.json().items()))
        n_processed += len(ids)
        print("Processed {0}/{1} IDs ...".format(n_processed, len(raw_ids)),
              file=sys.stderr)

    id_map = dict(id_items)

    for ignored_line in ignored:
        print(ignored_line)
    for item in processed:
        id_entry = id_map.get(item["id"])
        sym = fallback
        if id_entry is not None:
            sym = id_entry.get("display_name", fallback)
        print(sep.join(filter(None, [item["pre"], encl + sym + encl,
                                     item["post"]])))
