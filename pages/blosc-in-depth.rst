.. title: What Is Blosc?
.. slug: blosc-in-depth
.. date: 2021-05-06 06:43:07 UTC
.. tags:
.. link:
.. description:
.. type: text
.. .. template: story.tmpl


Blosc is a high-performance compressor that has been optimized for binary data. Its design allows for faster transmission of data to the processor cache than the traditional, non-compressed, direct memory fetch approach through an `memcpy()` OS call. This can be useful not only in reducing the size of large datasets on-disk or in-memory, but also in accelerating memory-bound computations, which is typical in vector-vector operations.

Watch this introductory video to learn more about the main features of Blosc:

.. .. raw:: html

..    <embed>
..        <script src="https://fast.wistia.com/embed/medias/s6rdj9nbjp.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><div class="wistia_responsive_padding" style="padding:56.25% 0 0 0;position:relative;"><div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%;"><div class="wistia_embed wistia_async_s6rdj9nbjp videoFoam=true" style="height:100%;position:relative;width:100%"><div class="wistia_swatch" style="height:100%;left:0;opacity:0;overflow:hidden;position:absolute;top:0;transition:opacity 200ms;width:100%;"><img src="https://fast.wistia.com/embed/medias/s6rdj9nbjp/swatch" style="filter:blur(5px);height:100%;object-fit:contain;width:100%;" alt="" aria-hidden="true" onload="this.parentNode.style.opacity=1;" /></div></div></div></div>
..    </embed>

.. .. youtube:: HdscCz97mNs
.. .. youtube:: vIj-Z3sUKdo
.. .. youtube:: m7xrxFI4WSg
.. youtube:: ER12R7FXosk
   :width: 75%
   :align: center

Blosc2 is the new iteration of the Blosc 1.x series, which adds more features and `better documentation <https://www.blosc.org/c-blosc2/c-blosc2.html>`_. You can also check out the `slides that explain the highlights of Blosc2 <https://www.blosc.org/docs/blosc2-intro-LEAPS-Innov-2021.pdf>`_.

Blosc2 also includes `NDim, a container with multi-dimensional capabilities <https://www.blosc.org/posts/blosc2-ndim-intro/>`_. In particular, Blosc2 NDim excels at reading multi-dimensional slices, thanks to its innovative pineapple-style partitioning. To learn more, watch the video `Why slicing in a pineapple-style is useful <https://www.youtube.com/watch?v=LvP9zxMGBng>`_.

.. Although this is nice, the format below shows the video in a more consistent way with the above one
.. .. image:: /images/slicing-pineapple-style.png
..   :width: 75%
..   :align: center
..   :alt: Slicing a dataset in pineapple-style
..   :target: https://www.youtube.com/watch?v=LvP9zxMGBng

.. youtube:: LvP9zxMGBng
   :width: 75%
   :align: center

When Blosc2 is used in combination with other libraries, magic can happen. For example, when used with HDF5/PyTables, Blosc2 can help to query tables with `100 trillion rows in human time frames <https://www.blosc.org/posts/100-trillion-baby/>`_.  Read more on the `latest developments of Blosc2 <https://www.blosc.org/docs/Blosc2-WP7-LEAPS-Innov-2023.pdf>`_.

.. raw:: html

   <hr width=50 size=10>

.. figure:: /images/numfocus-sponsored-project.png
   :width: 40%
   :align: center

   Blosc is a fiscally sponsored project of `NumFOCUS <https://numfocus.org>`_,
   a nonprofit dedicated to supporting the open source scientific computing community.
   If you like Blosc and want to support our mission, please consider making a
   `donation <https://numfocus.org/project/blosc>`_ to support our efforts.

Why it works?
-------------

Blosc uses the **blocking technique** (as `described here <http://www.blosc.org/docs/StarvingCPUs-CISE-2010.pdf>`_) to reduce activity on the memory bus as much as possible.  The blocking technique divides datasets into blocks small enough to fit in the caches of modern processors and performs compression/decompression there. It also leverages SIMD (SSE2) and multi-threading capabilities present in modern multi-core processors to accelerate the compression/decompression process to the maximum.

To get an idea of the kind of speed that BloscLZ, Blosc's default codec for synthetic data, can achieve, take a look at the following:

.. |blosclz-c| image::   /images/blosclz-comp.png
.. |blosclz-d| image::   /images/blosclz-decomp.png

+--------------+--------------+
| |blosclz-c|  | |blosclz-d|  |
+--------------+--------------+

Here is the speed for summing up a vector of real float32 data using a variety of codecs that come with Blosc2:

.. figure:: /images/sum_openmp-rainfall.png
   :width: 75%
   :align: center

Using Blosc compression can accelerate real computations when enough cores are dedicated to the task. The plot above was generated on a mid-sized workstation with an Intel 10940X processor with 14 cores, 4 memory channels (around 56 GB/s read bandwidth), Clear Linux and GCC 11. Notably, the compressed computation can exceed the read bandwidth of this system (85 GB/s vs 56 GB/s). For a more detailed explanation, see `this blog entry <https://www.blosc.org/posts/breaking-memory-walls/>`_.

You can find more benchmarks on `our blog <https://www.blosc.org>`_.  Additionally, you may be interested in reading this article on `Breaking Down Memory Walls <http://www.blosc.org/docs/Breaking-Down-Memory-Walls.pdf>`_.  Finally, make sure to check out `Blosc2 <https://github.com/Blosc/c-blosc2>`_, the next generation of Blosc.

Meta-Compression and Other Advantages over Existing Compressors
---------------------------------------------------------------

Blosc is not like other compressors; it should be called a *meta-compressor*. This is because it can use different codecs (libraries that reduce the size of inputs) and filters (libraries that improve compression ratio) under the hood. Nonetheless, it can still be referred to as a compressor because it comes with different codecs out of the box.

Currently, Blosc uses **BloscLZ** by default, a codec heavily based on `FastLZ <http://fastlz.org/>`_. Blosc also includes support for `LZ4 and LZ4HC <https://github.com/lz4/lz4>`_, `Zlib <https://github.com/zlib-ng/zlib-ng>`_ and `Zstd <https://github.com/facebook/zstd>`_.  Also, it comes with highly optimized **shuffle** and **bitshuffle** filters. These can use SSE2, AVX2 (Intel), NEON (ARM) or VMX/AltiVec/VSX (PowerPC) instructions (if available).

Blosc is responsible for coordinating codecs and filters to leverage the blocking technique (described above) and multi-threaded execution (when several cores are available). This ensures that every codec and filter can operate at high speeds, even if it was not initially designed for blocking or multi-threading. For instance, Blosc allows the use of the ``LZ4`` codec in a multi-threaded manner by default.

Other advantages of Blosc are:

* **Meant for binary data**: Can take advantage of the type size meta-information to improve the compression ratio by using the integrated shuffle and bitshuffle filters.

* **Small overhead on non-compressible data**: To compress **every** input, only a maximum of 32 (16 for Blosc1) additional bytes beyond the source buffer length are needed.

* **Super-chunks**: In Blosc2, we are introducing super-chunks as a way to overcome the limitations of chunks, which can only be up to 2^31 bytes in size. Super-chunks, on the other hand, can host data up to 2^63 bytes in size.

* **Frames**: These allow for serializing data either in-memory or on-disk. They provide an efficient way to persist or transmit the data in a compressed format.

However, there is much more to Blosc. For an updated list of features, please refer to our `ROADMAP <https://github.com/Blosc/c-blosc2/blob/main/ROADMAP.rst>`_. When combined, these features distinguish Blosc from other similar solutions.

Where Can Blosc Be Used?
------------------------

Applications that use Blosc are expected to exceed expected physical limits for I/O performance. For instance, you can see the benefits of Blosc on accessing compressed data in this `study from one of the Zarr authors <http://alimanfoo.github.io/2016/09/21/genotype-compression-benchmark.html>`_. Please note that this benchmark is somewhat outdated, and that new hardware and recent versions of Blosc may enhance performance beyond what is shown there.

Adapt Blosc to your needs
--------------------------

We understand that every user has unique needs, so we have made it possible to `register your own codecs and filters <https://www.blosc.org/posts/registering-plugins/>`_ to better adapt Blosc to different scenarios. Additionally, you can request that they be included in the main C-Blosc2 library, which not only allows for easier deployment, but also contributes to creating a richer and more useful ecosystem.

Additionally, we are creating `BTUNE <https://btune.blosc.org>`_, an innovative AI tool that can automatically determine the best compression parameters for your specific use case. The Blosc Development Team is working on adapting it to meet your needs. Interested? Contact us at contact@blosc.org.

Is Blosc Ready for Production Use?
----------------------------------

Yes, it is!

Blosc is currently being used in various libraries and is able to compress data at a rate that exceeds several petabytes per month worldwide. Fortunately, there haven't been many reports of failures caused by Blosc itself, but we strive to `respond as quickly as possible when such issues do arise <https://www.blosc.org/posts/new-forward-compat-policy/>`_. 

After a long period of testing, C-Blosc2 has entered the production stage in version 2.0.0. Both the API and format have been frozen, meaning there is a guarantee that your programs will continue to work with future releases of the library. Additionally, next releases will be able to read from persistent storage generated from previous releases (as of 2.0.0).

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

Your contribution is crucial to making Blosc as solid as possible. If you detect a bug or wish to propose an enhancement, feel free to open a new ticket or make yourself heard on the mailing list. Also, please note that we have a `Code of Conduct <https://github.com/Blosc/community/blob/master/code_of_conduct.md>`_ that you should read before contributing in any way.

Blosc License
-------------

Blosc is a free software released under the permissive `BSD license <https://en.wikipedia.org/wiki/BSD_licenses>`_. This means that you can use it in almost any way you want!

-- The Blosc Development Team
