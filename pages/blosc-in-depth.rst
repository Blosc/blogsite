.. title: What Is Blosc?
.. slug: blosc-in-depth
.. date: 2021-05-06 06:43:07 UTC
.. tags:
.. link:
.. description:
.. type: text
.. .. template: story.tmpl


Blosc is a high-performance compressor that has been optimized for binary data. Its design allows for faster transmission of data to the processor cache than the traditional, non-compressed, direct memory fetch approach through an `memcpy()` OS call. This can be useful not only in reducing the size of large datasets, but also in accelerating I/O, be either on-disk or in-memory (both are supported).

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

You can also check out the `slides that explain the highlights of Blosc2 NDim, specially when dealing with highly sparse, multidimensional datasets that appear when exploring the Milky Way <https://www.blosc.org/docs/Exploring-MilkyWay-SciPy2023.pdf>`_.  There it is also discussed `Btune <https://btune.blosc.org>`_, a tool that helps you finding the best Blosc2 configuration for your data.

When Blosc2 is used in combination with other libraries, magic can happen. For example, when used with HDF5/PyTables, Blosc2 can help to query tables with `100 trillion rows in human time frames <https://www.blosc.org/posts/100-trillion-baby/>`_.  Read more on this in these `slides on the latest developments of Blosc2 <https://www.blosc.org/docs/Blosc2-WP7-LEAPS-Innov-2023.pdf>`_.

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

Blosc2 also applies more advanced techniques to improve the compression ratio on sparse datasets, and a larger diversity of filters such as `bytedelta <https://www.blosc.org/posts/bytedelta-enhance-compression-toolset/>`_.  This makes Blosc2 a very versatile compressor that can be used in a wide range of situations.

Performance
-----------

Blosc2 is also designed to be efficient when retrieving blocks and chunks in multidimensional datasets.  For comparison purposes, see below the speed that BloscLZ, one of the fastest codecs available in Blosc, can achieve when combined with different libraries supporting Blosc(1)/Blosc2 when accessing a 7.3 TB dataset:

.. figure:: /images/slicing-speed-blosclz-libraries.png
   :width: 75%
   :align: center

Note how BloscLZ does not need a lot of threads to reach its performance.  Such a low requirement on CPU core count makes it ideal for running on small laptops while guaranteeing reasonable performance.

And below is the compression ratio that BloscLZ, and also Zstd (the codec that can typically achieve better compression ratios in Blosc), can achieve when combined with different libraries supporting Blosc(1)/Blosc2:

.. figure:: /images/filesizes-blosc1-vs-blosc2.png
   :width: 75%
   :align: center

See how Blosc2 can make better use of the space required to store the compressed data and internal indices, specially when dealing with sparse datasets (as is the case above).  More info in `these slides <https://www.blosc.org/docs/Exploring-MilkyWay-SciPy2023.pdf>`_.

You can find more benchmarks on `our blog <https://www.blosc.org>`_.  Additionally, you may be interested in reading this article on `Breaking Down Memory Walls <http://www.blosc.org/docs/Breaking-Down-Memory-Walls.pdf>`_.  Finally, make sure to check out `Blosc2 <https://github.com/Blosc/c-blosc2>`_, the next generation of Blosc, with support for n-dimensional data as well as more efficient handling of sparse data.

Blosc as a Meta-Compressor
--------------------------

Blosc is not like other compressors; it should rather be called a *meta-compressor*. This is because it can use different codecs (libraries that reduce the size of inputs) and filters (libraries that improve compression ratio) under the hood. Nonetheless, it can still be referred to as a compressor because it includes several codecs conveniently packaged and made accessible for you.

Currently, Blosc uses **BloscLZ** by default, a codec heavily based on `FastLZ <http://fastlz.org/>`_. Blosc also includes support for `LZ4 and LZ4HC <https://github.com/lz4/lz4>`_, `Zlib <https://github.com/zlib-ng/zlib-ng>`_ and `Zstd <https://github.com/facebook/zstd>`_ right out-of-the-box.  Also, it comes with highly optimized **shuffle**, **bitshuffle**, **bytedelta** and precision **truncation** filters. These can use SSE2, AVX2 (Intel), NEON (ARM) or VMX/AltiVec/VSX (PowerPC) instructions (if available).

Blosc is responsible for coordinating codecs and filters to leverage the blocking technique (described above) and multi-threaded execution (when several cores are available), while making minimal use of temporary buffers. This ensures that every codec and filter can operate at high speeds, even if it was not initially designed for blocking or multi-threading. For instance, Blosc allows the use of the LZ4 codec in a multi-threaded manner by default.

Other Advantages over Existing Compressors
------------------------------------------

* **Meant for binary data**: Can take advantage of the type size meta-information to improve the compression ratio by using the integrated shuffle and bitshuffle filters.

* **Small overhead on non-compressible data**: Only a maximum of 32 for Blosc2 (16 for Blosc1) of additional bytes per data chunk are needed on non-compressible data.

* **63-bit containers**: In Blosc2, we have introduced super-chunks as a way to overcome the limitations of chunks, which can only be up to 2^31 bytes in size. Super-chunks, on the other hand, can host data up to 2^63 bytes in size.

* **Frames**: Blosc2 also has introduced a way to serialize data either in-memory or on-disk. `Frames <https://github.com/Blosc/c-blosc2/blob/main/README_CFRAME_FORMAT.rst>`_ provide an efficient way to persist or transmit the data in a compressed format.

However, there is much more to Blosc. For an updated list of features, please refer to our `ROADMAP <https://github.com/Blosc/c-blosc2/blob/main/ROADMAP.rst>`_. When combined, these features distinguish Blosc from other similar solutions.

Where Can Blosc Be Used?
------------------------

Provided that data is compressible enough, applications that use Blosc are expected to surpass expected physical limits for I/O performance, either for network, disk, or in-memory storage, simply because applications needs to transmit less (compressed) data, and compression/decompression is very fast and usually happens entirely in CPU caches. For instance, see `how Blosc can break down memory walls <https://www.blosc.org/posts/posts/breaking-down-memory-walls/>`_.

Blosc2 also adds support for sparse and multi-dimensional datasets, which are common in scientific applications.  See an example on how Blosc can make an `efficient access to much larger datasets than the available memory <https://www.blosc.org/docs/Exploring-MilkyWay-SciPy2023.pdf>`_.

Currently, there is support for using Blosc in `Zarr <https://zarr.readthedocs.io>`_, h5py (via `hdf5plugin <https://github.com/silx-kit/hdf5plugin>`_) or `PyTables <http://www.pytables.org>`_; all of these projects have binary packages, so it is easy to start using it.

Adapt Blosc to your needs
--------------------------

We understand that every user has unique needs, so we have made it possible to `register your own codecs and filters <https://www.blosc.org/posts/registering-plugins/>`_ to better adapt Blosc to different scenarios. Additionally, you can request that they be included in the main C-Blosc2 library, which not only allows for easier deployment, but also contributes to creating a richer and more useful ecosystem.

Additionally, we have created `Btune <https://btune.blosc.org>`_, an innovative AI tool that can automatically determine the best compression parameters for your specific use case. The Blosc Development Team is continuously working on improving it to meet your needs.

Is Blosc Ready for Production Use?
----------------------------------

Yes, it is!

Blosc is currently being used in various libraries and is able to compress data at a rate that exceeds several petabytes per month worldwide. Fortunately, there haven't been many reports of failures caused by Blosc itself, but we strive to `respond as quickly as possible when such issues do arise <https://www.blosc.org/posts/new-forward-compat-policy/>`_.

After a long period of testing, C-Blosc2 has entered the production stage in version 2.0.0. Additionally, all new releases are guaranteed to read from persistent storage generated from previous releases (as of 2.0.0).

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

Python wrappers
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
