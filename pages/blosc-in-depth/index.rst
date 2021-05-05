.. title: What Is Blosc?
.. slug: blosc-in-depth
.. date: 2021-05-05 06:43:07 UTC
.. tags:
.. link:
.. description:
.. type: text
.. .. template: story.tmpl


Blosc is a **high performance compressor optimized for binary
data**. It has been designed to transmit data to the processor cache
faster than the traditional, non-compressed, direct memory fetch
approach via a ``memcpy()`` OS call.  This can be useful not only
to reduce the size of large datasets on-disk or in-memory, but also to
accelerate memory-bound computations (which is typical in vector-vector
operations).

It uses the **blocking technique** (as described in this `article
<http://www.blosc.org/docs/StarvingCPUs-CISE-2010.pdf>`_) to reduce
activity on the memory bus as much as possible.  In short, the
blocking technique works by dividing datasets in blocks that are small
enough to fit in L1 cache of modern processor and perform
compression/decompression there. It also leverages *SIMD* (SSE2)
and *multi-threading* capabilities present in nowadays multi-core
processors so as to accelerate the compression/decompression process
to a maximum.

To whet your appetite look at the kind of speed that Blosc can reach for BloscLZ,
its default codec:

.. |blosclz-c| image::   /images/blosclz-comp.png
.. |blosclz-d| image::   /images/blosclz-decomp.png

+--------------+--------------+
| |blosclz-c|  | |blosclz-d|  |
+--------------+--------------+

And here for LZ4, a well known and very fast codec that comes integrated
(with other codecs too) with Blosc:

.. |lz4-c| image::   /images/lz4-comp.png
.. |lz4-d| image::   /images/lz4-decomp.png

+--------------+--------------+
| |lz4-c|      | |lz4-d|      |
+--------------+--------------+

You can see more benchmarks in  `our blog <https://www.blosc.org>`_.  Also, you may want to check out this article on `Breaking Down Memory Walls <http://www.blosc.org/docs/Breaking-Down-Memory-Walls.pdf>`_. Also, check `Blosc2 <https://github.com/Blosc/c-blosc2>`_, the next generation of Blosc.

.. raw:: html

   <hr width=50 size=10>

.. figure:: /images/numfocus-sponsored-project.png
   :width: 40%
   :align: center

   Blosc is a fiscally sponsored project of `NumFOCUS <https://numfocus.org>`_, a nonprofit dedicated to supporting the open source scientific computing community. If you like Blosc and want to support our mission, please consider making a `donation <https://numfocus.org/project/blosc>`_ to support our efforts.


Meta-Compression And Other Advantages Over Existing Compressors
---------------------------------------------------------------

Blosc is not like other compressors: it should rather be called a
*meta-compressor**.  This is so because it can use different
codecs (libraries that can reduce the size of inputs) and filters
(libraries that generally improve compression ratio) under the hood.
At any rate, it can also be called a compressor because it ships
with different codecs out of the box.

Currently, Blosc uses **BloscLZ** by default, a codec heavily
based on `FastLZ <http://fastlz.org/>`_. From version 1.3 onwards,
Blosc also includes support for `LZ4 and LZ4HC
<https://github.com/lz4/lz4>`_, `Zlib
<https://github.com/zlib-ng/zlib-ng>`_ and
`Zstd <https://github.com/facebook/zstd>`_.  Also,
it comes with a highly optimized (it can use SSE2, AVX2 or NEON
instructions, if available) **shuffle** and **bitshuffle** filters.

Of course, almost every user has her own needs, and in Blosc2 we are
working on making possible for her to register different codecs
and filters so that they can fine tune Blosc for different scenarios.

Blosc is in charge of coordinating the codecs and filters
so that they can leverage the blocking technique (described above) as
well as multi-threaded execution (if several cores are available)
automatically. That makes that every codec and filter
will work at very high speeds, even if it was not initially designed
for doing blocking or multi-threading. For example, Blosc allows you
to use the ``LZ4`` codec, but in a multi-threaded way.

Other advantages of Blosc are:

* **Meant for binary data**: can take advantage of the type size
  meta-information for improved compression ratio (using the
  integrated shuffle and bitshuffle filters).

* **Small overhead on non-compressible data**: only a maximum of (32
  + 4 * nblocks_used) additional bytes over the source buffer length
  are needed to compress *every* input.

* **Super-chunks**: in Blosc2 we are introducing these as a way to
  overcome the limitations of chunks (which can be up to 2^31 bytes in size).
  Super-chunks can host data that is up to 2^63 bytes in size.

* **Frames**: these allow for serializing data either in-memory or
  on-disk.  They provide an efficient way to persist or transmit the data
  in compressed format.

When taken together, all these features set Blosc apart from other
similar solutions.


Where Can Blosc Be Used?
------------------------

Blosc was initially developed for the needs of the `PyTables
<http://www.pytables.org>`_ database and the `bcolz
<https://github.com/Blosc/bcolz>`_ project, and it is the default
compressor for the popular `Zarr <https://github.com/zarr-developers/zarr-python>`_
package; but of course it can be used in any situation where a fast compressor is
needed.

Applications using Blosc are expected to allow I/O performance to go beyond
expected physical limits.  For example, see this
`study from one of the Zarr authors <http://alimanfoo.github.io/2016/09/21/genotype-compression-benchmark.html>`_
to see the benefits of Blosc on accessing compressed data (please note that
this example is a bit dated, and that new hardware and recent versions of Blosc
will make the benefits to be better now in the next future.


Is It Ready For Production Use?
-------------------------------

Yup, it is!

Blosc is being used in different libraries, compressing data at a rate
that probably exceeds several Petabytes per month.  Fortunately, we haven't
received many reports of failures created my Blosc itself, and when
that happened we try to `respond as fast as possible
<https://www.blosc.org/posts/new-forward-compat-policy/>`_.

Moreover, with the introduction of Blosc 2.0.0 RC1, it has been declared
stable, and both the **API and the format have been frozen**, so you
should expect a large degree of stability for your Blosc2-powered
applications.

Git repository, downloads and ticketing
---------------------------------------

The home of the git repository for all Blosc-related libraries is
located at:

https://github.com/Blosc

You can download the sources and file tickets there too.

Mailing list
------------

There is an official Blosc blosc mailing list at:

http://groups.google.com/group/blosc

Python wrapping
---------------

You can find a Python package that wraps Blosc at:

http://github.com/Blosc/python-blosc
http://github.com/Blosc/python-blosc2

Want To Contribute?
-------------------

Your contribution is very important to make Blosc as solid as possible.  If
you detect a bug or wish to propose an enhancement, feel free to open a new
ticket or make yourself heard on the mailinglist.  Also, please note that
we have a `Code of Conduct <https://github.com/Blosc/community/blob/master/code_of_conduct.md>`_
that you should make sure to read before contributing in any way.

Blosc License
-------------

Blosc is free software and released under the terms of the very
permissive `BSD license <https://en.wikipedia.org/wiki/BSD_licenses>`_,
so you can use it in almost any way you want!
