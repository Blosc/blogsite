<!--
.. title: Common Interface for Remote and Local Datasets
.. slug: remote-local-objects
.. date: 2026-09-30 10:45:00 UTC
.. tags: remote, ctable, parquet, zarr, hdf5, pytables, Blosc2, cache, arrow
.. category: posts
.. link:
.. description: Python-Blosc2 4.14 brings a common streaming and caching interface to remote and local Parquet, Zarr, HDF5, PyTables, and Blosc2 datasets.
.. type: text
.. author: Francesc Alted
-->


I am happy to announce that the new **Python-Blosc2 4.14** brings a common interface to remote Parquet tables, Zarr and HDF5 arrays, PyTables tables, and indeed, native Blosc2 containers.
Most interestingly, a local cache keeps fetched data available for the next request/query; moreover, if cache is persistent, you can reuse the downloaded data throughout different sessions.

## TL;DR

- **One opener for everything**: `blosc2.open()` provides a unified interface across remote Parquet, Zarr, HDF5, PyTables, and native Blosc2 datasets over HTTP, S3, or any `fsspec` filesystem.
- **Zero full downloads**: Stream only the exact chunks, row groups, or physical columns your queries touch—no need to pull gigabytes of data to inspect a slice.
- **Smart persistent caching**: Passing `cache_dir=...` automatically caches fetched data locally across sessions and processes, eliminating redundant network roundtrips.
- **Index-accelerated remote queries**: Remote queries automatically exploit persisted PyTables and Blosc2 indexes without fetching entire columns or rebuilding indexes locally.
- **Ecosystem interoperability**: Combine remote arrays across different formats directly in lazy expressions (`b + z * h5`), or stream Arrow batches into DuckDB and Polars.

To whet your appetite, here is a practical tour using public datasets on Backblaze B2 (which is fully compatible with S3).
Here we are going to exercise the HTTP path, but all the protocols supported by [fsspec](https://filesystem-spec.readthedocs.io/en/latest/index.html) (like S3, GDrive, GCS, SFTP and many others) should be supported too.

<!-- TEASER_END -->

The examples below need the `fsspec`, `parquet`, `zarr`, and `hdf5` extras installed.
They run locally; the server only serves files and byte ranges.

## Open a remote (or local) table in parquet format

```python
import blosc2

BASE = "https://f001.backblazeb2.com/file/blosc2"
# BASE = "."   # uncomment this for local files

with blosc2.open(f"{BASE}/readings-large.parquet", cache_dir="cache-dir") as t:
    print(t)
    print(t["temperature"][:5])
```

This table has **two million rows and ten columns**, including nulls, strings, lists, and dictionary-encoded regions.
`print(t)` shows a truncated preview; most importantly, it **does not materialize** the whole table.

The same opener handles native Blosc2 tables and PyTables tables inside HDF5:

```python
with blosc2.open(f"{BASE}/readings-large.b2z", cache_dir="cache-dir") as t:
    print(t[:5])

with blosc2.open(
    f"{BASE}/pt-readings-large.h5", path="readings", cache_dir="cache-dir"
) as t:
    print(t[:5])
```

All three return a `RemoteCTable`.
The PyTables example contains seven fixed-width columns, while the Parquet and Blosc2 versions include richer types and nulls, so their results are not identical, although this is not important for demonstration purposes.

Note how you can open either remote or local files.
The new interface abstracts the details for the `urlpath` passed to `blosc2.open()` and does the right thing automatically.

## Querying remote tables

One of the most appealing aspects of the new feature is that queries can be made without the need to download everything.
For example, let’s select readings table (in parquet format here) from station 42 with humidity above 90, then keep just the columns we want to inspect:

```python
with blosc2.open(f"{BASE}/readings-large.parquet", cache_dir="cache-dir") as t:
    selected = t.where("(station_id == 42) & (humidity > 90)")
    print(selected.select(["id", "temperature", "humidity"])[:5])
```

This query needs the predicate columns across the table; displaying five matches does not mean that only five source rows were read. Parquet access works in physical-column/row-group units, so even a small slice can require a whole row group for each requested column.

Furthermore, existing indexes can reduce that work.
For example, our smaller, 200,000-row PyTables example has an index on `humidity`:

```python
with blosc2.open(
    f"{BASE}/pt-readings-idx.h5", path="readings", cache_dir="cache-dir"
) as t:
    print(t.info)  # includes the available humidity index
    result = (
        t.where("humidity > 99")
        .group_by("status")
        .agg(count=("*", "size"), mean_temperature=("temperature", "mean"))
    )
    print(result)
```

Blosc2 can use supported persisted PyTables indexes automatically, downloading only the needed index structures on demand.
That means much faster query results **without the need of recreating indexes locally**.

## Browse hierarchies, compute with different arrays on them

For containers holding groups and datasets (quite typical for HDF5 and Zarr datasets), `blosc2.open()` returns a `RemoteStore`:

```python
for suffix in ("b2z", "h5", "zarr"):
    with blosc2.open(f"{BASE}/hierarchy.{suffix}", cache_dir="cache-dir") as s:
        print(s.info)
        print(s["d0/a1"][:10])
```

`.info` lists the hierarchy and cache details without opening every array.
Again, the important thing is that different formats can be opened using the same `blosc2.open()` interface.

Selecting an array `path` in the hierarchy returns a `RemoteArray`:

```python
with (
    blosc2.open(f"{BASE}/hierarchy.h5", path="d0/d1/d2/a1", cache_dir="cache-dir") as h5,
    blosc2.open(f"{BASE}/hierarchy.zarr", path="d0/d1/a1", cache_dir="cache-dir") as z,
    blosc2.open(f"{BASE}/hierarchy.b2z", path="d0/a1", cache_dir="cache-dir") as b,
):
    expr = b + z * h5
    print(expr[:10])         # evaluate a slice, returning NumPy values
    result = expr.compute()  # evaluate the full expression into a local NDArray
```

These leaves all have shape `(10000,)`.
Now, it comes something interesting: as the remote objects do have the same interface, Blosc2 can use them as regular operands in expressions.
Indeed, the expression above combines formats through the same array interface, fetching source data as evaluation needs it.
This is essentially lazy evaluation at work, but local caching makes it very useful for distributed/remote data.

## What happens under the hood?

![What happens under the hood](/images/remote-objects-diagram.png)

Transfers follow the source layout: Parquet row groups, Zarr chunks, or supported HDF5/Blosc2 chunks and blocks. Small containers may be downloaded in full. Streaming avoids requiring a complete local copy before starting; it does not mean every operation reads only a handful of bytes or uses constant memory.

You can inspect cache reuse directly:

```python
for run in (1, 2):
    with blosc2.open(f"{BASE}/readings-large.parquet", cache_dir="cache-check") as t:
        values = t["temperature"][:5]
        print(run, t.traffic.requests, t.traffic.nbytes)
```

With a fresh `cache-check` dir, the first run fetches data; the second reuses the retained metadata and converted column group.
The counters report source reads and bytes, rather than every HTTP exchange.
A preview warms only the columns it displays: a later `t[0]` may still fetch hidden columns.

## Feed another engine when needed

Remote tables also support Arrow batches.
For a streaming consumer, select the columns explicitly and process each batch as it arrives:

```python
with blosc2.open(f"{BASE}/readings-large.b2z", cache_dir="cache-dir") as t:
    rows = 0
    for batch in t.iter_arrow_batches(columns=["station_id", "temperature"]):
        rows += batch.num_rows  # replace with your batch processing
    print(rows)
```

DuckDB can consume a table's Arrow stream directly, and Polars can materialize it as a DataFrame.
Export and conversion still cost time, but choosing the needed columns helps.

Two details matter when publishing your own sources.
Keep cached sources immutable, or call `refresh()` after replacing them and obtain fresh child handles.
Also, for Zarr browsing over HTTP without directory listings, you can get better times by publishing consolidated metadata; our example uses `zarr.consolidate_metadata("hierarchy.zarr")` before uploading the updated metadata.

Try a preview first, then a narrow query or array slice.
Done.

## Final thoughts

The traditional workflow—downloading multi-gigabyte files to local disk before opening a notebook—is slow, wasteful, and expensive in cloud egress.
By marrying on-demand byte-range streaming with persistent, transparent local caching, Blosc2 gives you the interactive responsiveness of local files alongside the flexibility of remote object storage.
You touch only what you need, and once cached, warm reads run at full local speed.

In our previous post, [Not an island: bringing compression to the tabular ecosystem](https://blosc.org/posts/not-an-island-tabular-ecosystem/), we outlined a core philosophy for Python-Blosc2: a compression framework should not attempt to be everything.
With these new features we continue our commitment to complement the existing ecosystem, while bringing value in the form of better usability and efficiency.

Whether you are evaluating lazy expressions across mixed array formats (Blosc2, HDF5, Zarr), accelerating queries with pre-computed remote indexes, or feeding column batches into DuckDB and Polars, this release opens new doors for responsive, out-of-core data workflows.

Give it a spin today:

```bash
pip install "blosc2[fsspec,parquet,zarr,hdf5]" --upgrade
```

Try it on your own datasets and share your feedback on [GitHub](https://github.com/Blosc/python-blosc2) or [Mastodon](https://fosstodon.org/@Blosc2).

And this interoperability process has just started; we have big plans to make data handling even more uniform and efficient in the future, reaching more programming languages, while improving safety and speed.
Stay tuned!

Compress Better, Compute Bigger, Share Faster
