.. title: What Is Blosc?
.. slug: blosc-in-depth
.. date: 2021-05-06 06:43:07 UTC
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

Watch this introductory video about the main features of Blosc:

.. .. raw:: html

..    <embed>
..        <script src="https://fast.wistia.com/embed/medias/s6rdj9nbjp.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><div class="wistia_responsive_padding" style="padding:56.25% 0 0 0;position:relative;"><div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%;"><div class="wistia_embed wistia_async_s6rdj9nbjp videoFoam=true" style="height:100%;position:relative;width:100%"><div class="wistia_swatch" style="height:100%;left:0;opacity:0;overflow:hidden;position:absolute;top:0;transition:opacity 200ms;width:100%;"><img src="https://fast.wistia.com/embed/medias/s6rdj9nbjp/swatch" style="filter:blur(5px);height:100%;object-fit:contain;width:100%;" alt="" aria-hidden="true" onload="this.parentNode.style.opacity=1;" /></div></div></div></div>
..    </embed>

.. .. youtube:: HdscCz97mNs
.. youtube:: vIj-Z3sUKdo
   :width: 75%
   :align: center



Why it works?
-------------

Blosc uses the **blocking technique** (as described in this `article
<http://www.blosc.org/docs/StarvingCPUs-CISE-2010.pdf>`_) to reduce
activity on the memory bus as much as possible.  In short, the
blocking technique works by dividing datasets in blocks that are small
enough to fit in the caches of modern processor and perform
compression/decompression there. It also leverages *SIMD* (SSE2)
and *multi-threading* capabilities present in nowadays multi-core
processors so as to accelerate the compression/decompression process
to a maximum.

To whet your appetite look at the kind of speed that Blosc can reach for BloscLZ,
its default codec using synthetic data:

.. |blosclz-c| image::   /images/blosclz-comp.png
.. |blosclz-d| image::   /images/blosclz-decomp.png

+--------------+--------------+
| |blosclz-c|  | |blosclz-d|  |
+--------------+--------------+

And here its the speed for summing up a vector of real data of float32 values
for a variety of codecs that come with Blosc2:

.. figure:: /images/sum_openmp-rainfall.png
   :width: 75%
   :align: center

There you can see how compressing with Blosc allows to accelerate real computations
if you throw enough cores at the task.  This plot has been made on a mid-sized workstation with an `Intel CoreX with 14 cores
<https://ark.intel.com/content/www/us/en/ark/products/198014/intel-core-i9-10940x-x-series-processor-19-25m-cache-3-30-ghz.html>`_,
with 4 memory channels (around 56 GB/s read bandwidth), Clear Linux and GCC 11.
In particular, note how the compressed computation can go beyond the read bandwidth of this box (85 GB/s vs 56 GB/s).
For a more in deep explanation, see `this blog entry <https://www.blosc.org/posts/breaking-memory-walls/>`_.

You can see more benchmarks in `our blog <https://www.blosc.org>`_.
Also, you may want to check out this article on `Breaking Down Memory Walls
<http://www.blosc.org/docs/Breaking-Down-Memory-Walls.pdf>`_.
Also, check `Blosc2 <https://github.com/Blosc/c-blosc2>`_, the next generation of Blosc.

.. raw:: html

   <hr width=50 size=10>

.. figure:: /images/numfocus-sponsored-project.png
   :width: 40%
   :align: center

   Blosc is a fiscally sponsored project of `NumFOCUS <https://numfocus.org>`_,
   a nonprofit dedicated to supporting the open source scientific computing community.
   If you like Blosc and want to support our mission, please consider making a
   `donation <https://numfocus.org/project/blosc>`_ to support our efforts.

Meta-Compression And Other Advantages Over Existing Compressors
---------------------------------------------------------------

Blosc is not like other compressors: it should rather be called a
*meta-compressor**.  This is so because it can use different
codecs (libraries that can reduce the size of inputs) and filters
(libraries that generally improve compression ratio) under the hood.
At any rate, it can also be called a compressor because it ships
with different codecs out of the box.

Currently, Blosc uses **BloscLZ** by default, a codec heavily
based on `FastLZ <http://fastlz.org/>`_. Blosc also includes support for `LZ4 and LZ4HC
<https://github.com/lz4/lz4>`_, `Zlib
<https://github.com/zlib-ng/zlib-ng>`_ and
`Zstd <https://github.com/facebook/zstd>`_.  Also,
it comes with highly optimized **shuffle** and **bitshuffle** filters. These can use SSE2, AVX2 (Intel), NEON (ARM) or VMX/AltiVec/VSX (PowerPC) instructions (if available).

Blosc is in charge of coordinating the codecs and filters
so that they can leverage the blocking technique (described above) as
well as multi-threaded execution (if several cores are available)
automatically. That makes that every codec and filter
will work at very high speeds, even if it was not initially designed
for doing blocking or multi-threading. For example, Blosc allows to use the ``LZ4`` codec, but in a multi-threaded way.

Other advantages of Blosc are:

* **Meant for binary data**: can take advantage of the type size
  meta-information for improved compression ratio (using the
  integrated shuffle and bitshuffle filters).

* **Small overhead on non-compressible data**: only a maximum of 32
  (16 for Blosc1) additional bytes over the source buffer length
  are needed to compress *every* input.

* **Super-chunks**: in Blosc2 we are introducing these as a way to
  overcome the limitations of chunks (which can be up to 2^31 bytes in size).
  Super-chunks can host data that is up to 2^63 bytes in size.

* **Frames**: these allow for serializing data either in-memory or
  on-disk.  They provide an efficient way to persist or transmit the data
  in compressed format.

But there is much more.  For an updated list of features, see our
`ROADMAP <https://github.com/Blosc/c-blosc2/blob/main/ROADMAP.md>`_.
When taken together, all these features set Blosc apart from other
similar solutions.


Where Can Blosc Be Used?
------------------------

Applications using Blosc are expected to allow I/O performance to go beyond
expected physical limits.  For example, see this
`study from one of the Zarr authors <http://alimanfoo.github.io/2016/09/21/genotype-compression-benchmark.html>`_
to see the benefits of Blosc on accessing compressed data (please note that
this benchmark is a bit dated, and that new hardware and recent versions of Blosc might enhance performance well beyond what is shown there).


Adapt Blosc to your needs
--------------------------

We know that every user has her own needs, so we made possible to `register your own codecs and filters <https://www.blosc.org/posts/registering-plugins/>`_ so that you can better adapt Blosc to different scenarios. In addition, you can ask them to be included in the main C-Blosc2 library, which not only allows for much easier deployment, but also contributes to create a richer and more useful ecosystem. 


Is It Ready For Production Use?
-------------------------------

Yup, it is!

Blosc is being used in different libraries, compressing data at a rate
that probably exceeds several Petabytes per month.  Fortunately, we haven't
received many reports of failures created by Blosc itself, and when
that happens we strive to `respond as fast as possible
<https://www.blosc.org/posts/new-forward-compat-policy/>`_.

Also, and after a long period of testing, C-Blosc2 entered production stage in 2.0.0, and both the API and the format have been frozen, and that means that there is guarantee that your programs will continue to work with future versions of the library, and that next releases will be able to read from persistent storage generated from previous releases (as of 2.0.0).

Git repository, downloads and ticketing
---------------------------------------

The home of the git repository for all Blosc-related libraries is
located at:

https://github.com/Blosc

You can download the sources and file tickets there too.

Twitter feed
------------

Keep informed about the latest developments by following the @Blosc2 twitter account:

https://twitter.com/Blosc2

Mailing list
------------

There is an official Blosc blosc mailing list at:

http://groups.google.com/group/blosc

Python wrapping
---------------

The official Python wrappers can be found at:

http://github.com/Blosc/python-blosc
http://github.com/Blosc/python-blosc2

Want To Contribute?
-------------------

Your contribution is very important to make Blosc as solid as possible.  If
you detect a bug or wish to propose an enhancement, feel free to open a new
ticket or make yourself heard on the mailing list.  Also, please note that
we have a `Code of Conduct <https://github.com/Blosc/community/blob/master/code_of_conduct.md>`_
that you should make sure to read before contributing in any way.

Blosc License
-------------

Blosc is free software and released under the terms of the very
permissive `BSD license <https://en.wikipedia.org/wiki/BSD_licenses>`_,
so you can use it in almost any way you want!

-- The Blosc Development Team
