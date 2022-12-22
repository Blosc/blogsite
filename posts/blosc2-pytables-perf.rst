.. title: Blosc2 Meets PyTables: Helping HDF5 Achieving Extremely High I/O Performance
.. author: Oscar Guiñon, Francesc Alted
.. slug: blosc2-pytables-perf
.. date: 2022-12-13 12:32:20 UTC
.. tags: blosc2 pytables performance
.. category:
.. link:
.. description:
.. type: text


`PyTables <http://www.pytables.org>`_ lets users to easily handle data tables and array objects in a hierarchical structure. It supports a variety of different data compression libraries through `HDF5 filters <https://docs.hdfgroup.org/hdf5/develop/_f_i_l_t_e_r.html>`_.  Now, the Blosc Development Team is pleased to announce the availability of Blosc2, not only as another HDF5 filter, but also as an advanced partition tool that complements the existing HDF5 chunking schema.

When Blosc2 is used as an additional partition tool (referred ahead as 'optimized Blosc2' too), it can bypass the HDF5 pipeline for writing and for reading.  This, combined with the capability to read the small data blocks (in which the chunk is split internally), makes that small data slices can be read without having to read (and decompress) the whole chunk.  This is actually an additional partition level on top of the existing chunking level in HDF5, and offers a completely new way to structure your data without adding overhead to the HDF5 layer.

Also, by providing support for a second partition in HDF5, the chunks (aka the first partition) can be made larger, ideally fitting in cache level 3 in modern CPUs (see below for advantages of this).  Meanwhile, Blosc2 will use its internal blocks (aka the second partition) as the minimum amount of data that should be read and decompressed during data retrieval, no matter how small the hyperslice to be read is.  This brings another degree of freedom in the choosing of different internal I/O buffers, which is of extraordinary importance in terms of performance and/or resource saving.


Meant for Big Chunking
======================

Blosc2 in PyTables is meant for compressing data in big chunks (typically in the range of level 3 caches in modern CPUs, that is, 10 ~ 1000 MB).  This has some interesting advantages:

- It allows to reduce the number of entries in the HDF5 hash table. This means less resource consumption in the HDF5 side, so PyTables can handle larger tables using less resources.

- It improves compression ratios, since compression blocks can be larger and hence, codecs have more opportunities to find duplications.

- It speeds-up compression and decompression even more because the Blosc2 multithreading works better with more blocks. Remember that you can specify the number of threads to use by using the `MAX_BLOSC_THREADS <http://www.pytables.org/usersguide/parameter_files.html?highlight=max_blosc_threads#tables.parameters.MAX_BLOSC_THREADS>`_ parameter, or by using the `BLOSC_NTHREADS <https://www.blosc.org/c-blosc2/reference/blosc1.html?highlight=blosc_nthreads#blosc1-api>`_ environment variable.

.. image:: /images/blosc2_pytables/block-slice.png
  :width: 70%
  :align: center

The traditional drawback of having large chunks is that getting small slices takes long times because the whole chunk has to be read completely and decompressed.  And this is how Blosc2 surmounts the difficulty: it asks HDF5 where chunks start on-disk (via `H5Dget_chunk_info() <https://docs.hdfgroup.org/hdf5/v1_12/group___h5_d.html#title12>`_), and then it access to the internal blocks independently instead of decompressing the entire chunk.  This allows the use of large chunks without penalizing access to small data slices.


Benchmarks
==========

The data used in the benchmarks below have been fetched from `ERA5 database <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5>`_, which provides hourly estimates of a large number of atmospheric, land and oceanic climate variables.  To build the tables used for reading and writing operations, there have been fetched five different ERA5 datasets with the same shape (100 x 720 x 1440) and the same variables (latitude, longitude and time).  Then, there has been defined a table with a column for each variable and each dataset. Finally, there have been written 100 x 720 x 1440 rows to this table (more than 100 million rows), for a total size of 3.1 GB.

Next, we present different scenarios when comparing resource usage for writing and reading between the Blosc and Blosc2 filters, including the Blosc2 optimized versions.  First scenario is when PyTables choose the chunkshape automatically (the default); as Blosc2 is meant towards large chunks, PyTables has been tuned to produce far larger chunks for Blosc2 in this scenario (Blosc and other filters will remain as larger as usual). Second, we will visit the case where the chunkshape is equal for both Blosc and Blosc2.  We will see how Blosc2 behaves well (and sometimes *much beter*) in both scenarios.


Memory and time usage in in-kernel searches
-------------------------------------------

We start by performing queries where the chunkshape for the table is chosen automatically by the PyTables machinery.  This is different for Blosc, Zlib and uncompressed cases (16384 rows, or about 512 KB), whereas for Blosc2 the computed chunkshape is quite larger (1179648 rows, about 36 MB; this actually depends on the size of the L3 cache, which is automatically queried in real-time and it turns out to be exactly 36 MB for our CPU, an Intel i9-13900K).

Now, we are going to analyze a plot comparing the memory and time use of performing six `inkernel searches <http://www.pytables.org/usersguide/optimization.html?highlight=kernel#in-kernel-searches>`_, which means scanning the full table six times, in different cases:

- With no compression; table size is 3,1 GB.
- Using HDF5 with ZLIB + Shuffle; table size is 407 MB.
- Using Blosc filter with BloscLZ codec + Bitshuffle; table size is 468 MB.
- Using Blosc2 filter with BloscLZ codec + Bitshuffle; the table size is 421 MB.
- Using Blosc2 filter with Zstd codec + Bitshuffle; the table size is 341 MB.

.. image:: /images/blosc2_pytables/inkernel-nocomp-zlib-blosc-zstd.png
  :width: 125%
  :align: center

As we can see, the queries with no compression do not take much time or memory consumption, but it requires storing a 3.1 GB table. When using ZLIB, which is the HDF5 default, it does not require much memory either, but it takes a much more time (about 10x more), but the table is more than 6x smaller. When using Blosc, the resource consumption is much more contained, but it still takes more time (1.66x more) and uses a bit more memory than the no compression case; in addition, the compression ratio is close to the ZLIB case.

However, the big jump comes using Blosc2 with BloscLZ, since it uses just a little more memory than Blosc (a consequence of using larger chunks), but in exchange it is quite faster (actually 1.3x faster than using no compression) while achieving a noticeably better compression ratio.  Finally, in case we want to improve compression further, Blosc2 can be used with ZSTD compressor, which achieves the best compression ratio here, in exchange for a slightly slower time (but still 1.15x faster than not using compression).


Inkernel vs pandas queries
--------------------------

Now that we have seen how Blosc2 can help PyTables in getting great query performance, we are going to compare it against pandas queries; to make things more interesting, we will be using the same NumExpr engine in both PyTables (where it is used in inkernel queries) and pandas.

For this benchmark, we have been exploring the best configuration for speed, so we will be using 16 threads (for both Blosc2 and NumExpr) and the Shuffle filter instead of Bitshuffle; this leads to slightly less compression ratios (see below), but now the goal is speed, not storage (keep in mind that Pandas stores data in-memory without compression).

Here it is how PyTables and pandas behave when doing the same 6 queries than in the previous section:

.. image:: /images/blosc2_pytables/inkernel-pandas.png
  :width: 125%
  :align: center


As we can see, the queries using Blosc2 + LZ4 get nearly as good times as using Pandas, while the memory consumption is much smaller with Blosc2 (as much as 20x less in this case).  This is quite a feat actually, as this means that compression results in acceleration that almost compensates for all the additional layers in PyTables (the disk subsystem and the HDF5 library itself)

And in case you wonder how much compression ratio we have lost by switching from Bitshuffle to Shuffle, not much actually:

.. image:: /images/blosc2_pytables/shuffle-bitshuffle-ratios.png
  :width: 70%
  :align: center


All in all, and when used correctly, compression can make out-of-core queries go as fast as pure in-memory ones (even when using a high performance tool-set like pandas + NumExpr).


Writing and reading speed: automatic chunkshape
-----------------------------------------------

In this section, chunkshape is chosen automatically by the PyTables machinery, and is different for Blosc and Blosc2, being 16384 rows (about 512 KB) for Blosc and 1179648 rows (about 36 MB) for Blosc2.

.. image:: /images/blosc2_pytables/append-expectedrows.png
  :width: 70%
  :align: center

First, this plot compares the speed of Blosc and Blosc2 to write a table. Optimized Blosc2 is able to write the table faster and get better compression ratios because of a combination of facts:

1) It uses bigger chunks/blocks to better find duplications.

2) It uses the `HDF5 direct chunking machinery <https://docs.hdfgroup.org/archive/support/HDF5/doc/Advanced/DirectChunkWrite/index.html>`_ for avoiding the HDF5 pipeline overhead.

**Note**: the standard Blosc2 filter cannot use HDF5 direct chunking, but it still has an advantage when using bigger chunks because it allows for more threads and hence, improved parallel (de-)compression.  However, when retrieving small data slices, this comes as a disadvantage, and using the previous Blosc filter is recommended instead.

.. image:: /images/blosc2_pytables/inkernel-queries-expectedrows.png
  :width: 70%
  :align: center


The plot above is comparing the speed of Blosc and Blosc2 to perform six inkernel queries. Optimized Blosc2 is able to read the table faster because it bypasses HDF5 pipeline in order to access the blocks (chunks partitions) and decompress them in parallel. We can see how the advantage grows and we use more threads.

.. image:: /images/blosc2_pytables/slice-read-expectedrows.png
  :width: 70%
  :align: center

Here we can see a plot comparing the mean times of Blosc and Blosc2 to read a small slice. In this case, Blosc chunkshape is small, so it is not much slower than optimized Blosc2 for reading the slice even if Blosc2 uses blocking, since these Blosc2 blocks are similar in size to these Blosc chunks.


Writing and reading speed: same chunkshape
------------------------------------------

In this case, we have chosen the chunkshape to be 720 x 1440 rows (about 32 MB) for both Blosc and Blosc2.

.. image:: /images/blosc2_pytables/append-chunklen.png
  :width: 70%
  :align: center

The plot above compares the speed of Blosc and Blosc2 to write a table. In this case, optimized Blosc2 is still manages to write the table faster mainly because of the bypass of the HDF5 direct chunking machinery, but the advantage is smaller in this case.

.. image:: /images/blosc2_pytables/inkernel-queries-chunklen.png
  :width: 70%
  :align: center

Regarding inkernel searches, above is a plot comparing the speed of Blosc and Blosc2 to perform six inkernel queries. The optimized Blosc2 is able to read the table slightly faster because of fine-tune blocking and the bypass of the HDF5 pipeline, but this time the advantage is becoming small as we add more threads, probably because Blosc has less overhead during data decompression (Blosc2 needs to use a frame for serializing the chunk, which represents an additional storage layer, and its associated overhead shows up here).

.. image:: /images/blosc2_pytables/slice-read-chunklen.png
  :width: 70%
  :align: center

Above we can see a plot comparing the mean times of Blosc and Blosc2 to read a small slice. In this case, since chunkshapes are equal and big, optimized Blosc2 is much faster than the others because it only decompresses the internal blocks instead of the whole chunks.  However, Blosc and the Blosc2 filter, need to decompress the whole chunk.


Final remarks
=============

After considering these results, we can conclude that Blosc2 provides a great improvement in the HDF5 I/O speed, specially when using big chunks.  That means that you can do queries of large compressed datasets and still get very good speed, and typically faster than using no compression, even when using in memory data.  And for on-disk datasets with machines with much less RAM than the size of the datasets, compression can represent even a larger advantage, as it means less data has to travel the (slow) path from disk to memory.

Of course, there are situations where using big chunks would not be acceptable; for example, when using other HDF5 apps that do not support the optimized Blosc2 partition, and they need to use the plain Blosc2 filter. In that case, one can keep using the regular Blosc, since it has less overhead for smaller chunks (as shown above).

Please note that in the current implementation, we have just provided optimized Blosc2 paths for the `Table <http://www.pytables.org/usersguide/libref/structured_storage.html?highlight=table#tables.Table>`_ object in PyTables.  Starting with Table objects makes sense because it is the most important object in PyTables.  Other chunked objects in PyTables (like 'EArray' or 'CArray') could be optimized too to be used through Blosc2, but that would be for another go.

We have also added some documentation about Blosc2 in the 'Optimization tips' chapter of the `PyTables User's Guide <http://www.pytables.org/usersguide/optimization.html>`_ that you may want to check (although most of it can be found here).  For low-level details about the Blosc2 implementation (including the new HDF5 Blosc2 filter), `use the source <https://github.com/PyTables/PyTables/pull/969>`_.

Last but not least, we would like to thank NumFOCUS and other PyTables donors for providing the funds required to implement Blosc2 support in PyTables.  If you like what we are doing, and would like our effort to continue developing well, you can support our work by donating to `PyTables project <https://numfocus.org/project/pytables>`_ or `Blosc project <https://numfocus.org/project/blosc>`_ teams. Thank you!
