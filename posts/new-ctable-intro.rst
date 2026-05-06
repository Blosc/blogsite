.. title: CTable: a Blosc2-based columnar table
.. author: Jorge Albiol, Francesc Alted
.. slug: ctable-blosc2-columnar-table
.. date: 2026-05-06 9:00:00 UTC
.. tags: blosc2
.. category: posts
.. link:
.. description:
.. type: text



Motivation
----------

Working with large structured datasets in Python often means choosing between
speed and simplicity. CTable was born out of the need for a columnar store that
compresses data on the fly, stays close to NumPy, and does not require an
external database engine.

How it works
------------

CTable stores each column as an independent ``blosc2.NDArray``, compressed in
chunks. Column types are defined through a schema — a plain Python dataclass
where each field is annotated with a Blosc2 type spec such as ``b2.int64()``,
``b2.float32(ge=0)``, or ``b2.string()``. Specs can carry constraints (e.g.
``ge=0`` for non-negative values) and are compiled into a schema that validates
every row on insert, either one at a time via Pydantic or in bulk via vectorized
NumPy checks.

Rows are tracked with a boolean tombstone mask: deleting a row simply flips its
entry in the mask to ``False``, with no data movement at all. The actual space is
reclaimed lazily when you call ``compact()``. Appending is also efficient because
the underlying arrays are pre-allocated up front — they only grow when the
pre-allocated capacity is exhausted, so there is no resize on every single insert.

Because the data lives in Blosc2 chunks, many queries can skip full chunks
entirely. When a chunk's stored metadata (min/max) rules out any match, it is
never decompressed. This is where a lot of the query speed comes from, and it is
also why explicit indexes (described in Features below) can push performance
even further.

Since ``blosc2.NDArray`` stores fixed-width binary data, ``null`` has no natural
representation for integers, floats, or booleans. CTable solves this by letting
you declare a sentinel value as the null marker for a column. For example, if
you are storing ages and sometimes the value is unknown, you can set ``-1`` as
the null value since ages are never negative. Aggregates such as ``.mean()`` or
``.std()`` skip those rows automatically, and helper methods like ``.is_null()``
and ``.null_count()`` make it easy to work with them.



Features
--------

- **Creation**: A CTable can be created in several ways. The most direct is
  declaring a typed schema as a dataclass and passing it to the constructor.
  You can also build a CTable from existing data — ``from_arrow()`` and
  ``from_csv()`` import Arrow tables and CSV files respectively, inferring or
  mapping types automatically. Finally, ``copy()`` produces a new independent
  CTable from an existing one, already compacted.

- **Modification**: Appending a single row uses ``append()``, while bulk
  insertion uses ``extend()``. Deleting rows sets their mask entry to ``False``
  and is essentially free. Columns can be added with a default value or dropped
  and renamed at any time. Beyond stored columns, CTable also supports two kinds
  of virtual columns: *computed columns* are evaluated on-the-fly from an
  expression over other columns and never touch storage; *materialized columns*
  look like stored columns but are auto-filled automatically during every
  ``extend()``.

- **Querying**: ``where(expr)`` filters rows and returns a *view* — a new
  CTable object that shares the same column arrays as the parent but carries its
  own mask. No data is copied; only the mask is computed. Views block structural
  changes (adding/dropping columns, deleting rows) but do allow writing values
  to existing cells. ``select(cols)`` gives a column-projection view in the same
  spirit. Both can be made into a fully independent mutable table with
  ``copy()``. Aggregates (``sum()``, ``mean()``, ``std()``, ``min()``,
  ``max()``, ...) and ``sort_by()`` also work on views and respect the mask.

- **Indexing**: For workloads that repeatedly query the same column, CTable
  supports three index flavors: ``FULL`` (sorted positions array, best for range
  and comparison queries), ``BUCKET`` (hash-based, best for equality lookups),
  and ``PARTIAL`` (a lighter-weight sorted structure). Once an index is created,
  ``where()`` uses it automatically when the query can benefit from it. Indexes
  are persisted alongside the table and survive ``.b2z`` round-trips.

- **Persistence**: Tables can live fully in memory or be backed by files on
  disk. ``save()`` writes an in-memory table to a directory or ``.b2z`` archive.
  ``CTable.open()`` attaches directly to an on-disk table for reading or
  writing without loading everything into RAM. ``CTable.load()`` copies the
  on-disk table fully into memory for faster subsequent access. Both ``.b2d``
  directories and ``.b2z`` zip archives are supported transparently.

Mini benchmarks
---------------

Early numbers show that indexed range queries on a 10 M-row table run 2–3× faster
than a full scan, and bulk ``extend`` throughput is competitive with raw NumPy
array writes thanks to Blosc2's block-level compression pipeline.

AI use
------

Several parts of CTable — docstrings, test scaffolding, and this very blog post
draft — were written with the help of Claude Code. The AI was particularly useful
for boilerplate-heavy tasks while the algorithmic core was hand-crafted and
reviewed manually.

Conclusions
-----------

CTable brings together compression, schema validation, and query acceleration in
a self-contained Python package. It is still young, but the architecture is solid
and the feature set already covers most common analytical workflows.
