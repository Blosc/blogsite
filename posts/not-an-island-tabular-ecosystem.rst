.. title: Not an island: bringing compression to the tabular ecosystem
.. author: Francesc Alted
.. slug: not-an-island-tabular-ecosystem
.. date: 2026-07-17 12:00:01 UTC
.. tags: ctable arrow pandas interop compression
.. category: posts
.. link:
.. description:
.. type: text

A compression library can go one of two ways: try to be everything (its own dataframe, its own query engine, its own format that nothing else reads), or be a fast, compact layer that slots underneath the tools you already use. Python-Blosc2 has initially leaned toward the first path, but this is changing quite dramatically.  During the past year, we put a lot of effort in making Python-Blosc2 as much compatible as possible with the `array API initiative <https://data-apis.org/array-api/latest/>`_.

And today's 4.9.1 release pushes compatibility with the tabular library ecosystem further than ever: `CTable <https://blosc.org/python-blosc2/reference/ctable.html>`_, our compressed table container, now plugs straight into Arrow, pandas, Polars and DuckDB.

Speaking Arrow
--------------

The star of this release is support for the `Arrow PyCapsule protocol <https://arrow.apache.org/docs/format/CDataInterface/PyCapsuleInterface.html>`_ — the lingua franca of modern tabular tools. In plain terms: any Arrow-aware tool can now read a ``CTable`` directly, streaming it in small batches, without you converting anything first. Here is the same query — average fare per taxi company — asked five different ways, all against the same compressed file:

.. code-block:: python

    import blosc2

    t = blosc2.CTable.open("trips.b2z")

    # With Blosc2 itself...
    t.group_by("company").mean("fare")

    # ...or in SQL, with DuckDB reading the compressed table directly
    import duckdb
    duckdb.sql("SELECT company, avg(fare) FROM t GROUP BY company").show()

    # ...or with Polars
    import polars as pl
    pl.DataFrame(t).group_by("company").agg(pl.col("fare").mean())

    # ...or with pandas >= 3.0
    import pandas as pd
    pd.DataFrame.from_arrow(t).groupby("company")["fare"].mean()

    # ...or with plain pyarrow
    import pyarrow as pa
    pa.table(t).group_by("company").aggregate([("fare", "mean")])

Pick whichever syntax you like best — the data stays compressed on disk either way.

And it works the other way around too — hand ``CTable.from_arrow()`` a Polars dataframe, a pyarrow table or a Parquet reader, and you get a compressed table back:

.. code-block:: python

    import polars as pl

    pdf = pl.DataFrame({"ticker": ["AAPL", "GOOG"], "close": [184.2, 140.8]})
    t2 = blosc2.CTable.from_arrow(pdf)

Blosc2 isn't inventing anything here — it just implements a protocol the whole ecosystem already agreed on.

Strings that everyone understands
---------------------------------

Text columns used to force an awkward choice in Blosc2: fixed-width strings (fast, but every value pays for the longest one) or variable-length strings (flexible, but slow to query). The new ``blosc2.utf8()`` column type ends that dilemma: it stores text in the exact same layout Arrow uses, so every row costs only what it needs — up to 13x less memory than fixed-width on free-form text — and data flows to and from Arrow tools with no translation.

.. code-block:: python

    from dataclasses import dataclass
    import blosc2

    @dataclass
    class Place:
        name: str = blosc2.field(blosc2.utf8())
        visitors: int = blosc2.field(blosc2.int64())

    t = blosc2.CTable(Place, new_data={
        "name": ["café", "O'Hare", "日本語のテキスト", "zürich"],
        "visitors": [120, 85_000, 42, 300],
    })

And yes, it is fast: reading a full 10-million-row column requires just a fraction of a second; filtering is fast too, and ``utf8()`` even beats fixed-width strings as a ``group_by()`` key. Filters, sorting and grouping all work on it out of the box. However, sometimes you may still want to use ``string()`` / ``vlstring()`` for specific use cases; see the `"Choosing a string column type" guide <https://blosc.org/python-blosc2/reference/ctable.html#choosing-a-string-column-type>`_ if you want the details.

Feeling at home for pandas users
--------------------------------

``CTable`` also picked up more of pandas' vocabulary this cycle, so familiar idioms now just work — chaining with ``assign()`` and ``col()``, proper missing-data handling with ``fillna()`` and ``dropna()``, and custom aggregation functions in ``group_by()``:

.. code-block:: python

    from blosc2 import col

    (t.assign(profit=col("revenue") - col("cost"))
      [col("profit") > 0]
      .sort_by("profit", ascending=False)
      .head(10))

And if you'd rather stay in pandas entirely, you can still bring Blosc2's compute engine with you: ``df.apply(func, engine=blosc2.jit)`` now works correctly inside pandas 3, and ``Series.map()`` supports it too. See the `"Using Blosc2 as a pandas engine" guide <https://blosc.org/python-blosc2/guides/pandas_engine.html>`_.

Cooperation, not completeness
-----------------------------

Although ``CTable`` object comes with powerful machinery, it doesn't need to replace DuckDB, Polars or pandas to be useful; it just needs to hand them data in the shape they already expect — while doing the compression and fast querying underneath. If interoperating with the tools you already love sounds like the right job for a compression library, this is the release that makes the case.

Install it with::

    pip install blosc2 --upgrade

Full release notes: https://github.com/Blosc/python-blosc2/releases

Enjoy data!
