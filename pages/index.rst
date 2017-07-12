.. title: Blosc, an extremely fast, multi-threaded, meta-compressor library
.. slug: index
.. date: 2014-06-16 16:43:07 UTC
.. tags:
.. link:
.. description:
.. type: text
.. template: story.tmpl

.. class:: jumbotron col-md-6

What Can Blosc Do For You?
--------------------------

.. class:: lead

Plain and simple: it allows you to compress |--| but especially |--|
decompress your data, *fast*.

**What Makes Blosc Different?**

* High performance compressor, optimized for **binary** data (but text is fine too).
* Designed to transmit data to the processor cache **faster than a memcpy()**
  OS call.  Achieving that will obviously depend on the dataset, but that is the *goal*.
* Leverages **SIMD (SSE2, AVX2) and multi-threading** capabilities present in modern
  multi-core processors.
* APIs for **C, Python, Julia and more**.
* It **can use different, very fast compressors**.
  Just write your code once and get access to an amazing range of
  compressors, like BloscLZ, LZ4, LZ4HC, Snappy, Zlib or Zstd.

.. raw:: html

   <ul>
   <li><a class="btn btn-danger btn-lg" href="https://github.com/Blosc/c-blosc/releases">
       <i class="glyphicon glyphicon-download-alt"></i> Get c-blosc</a></li>
   <li><a class="btn btn-danger btn-lg" href="https://github.com/Blosc/python-blosc/releases">
       <i class="glyphicon glyphicon-download-alt"></i> Get python-blosc</a></li>
   <li><a class="btn btn-danger btn-lg" href="https://github.com/Blosc/bloscpack/releases">
       <i class="glyphicon glyphicon-download-alt"></i> Get bloscpack</a></li>
   <li><a class="btn btn-danger btn-lg" href="https://github.com/Blosc/bcolz/releases">
       <i class="glyphicon glyphicon-download-alt"></i> Get bcolz</a></li>
   </ul>

**Want to contribute to the Blosc ecosystem?**

We are eager to hear about ideas and code contributions (via `Pull Requests <https://github.com/Blosc>`_ preferably)!
If you don't have time to contribute code and you would like us to do the job, you can `contract us <http://www.blosc.org/professional-services.html>`_.

-------------------

**Enjoy data!**

.. class:: col-md-4

Why different compressors?
--------------------------

There is a reason why such a huge variety of compressors exist: each
one has its own strengths for different scenarios.  `Blosc is all about
speed <http://alimanfoo.github.io/2016/09/21/genotype-compression-benchmark.html>`_,
so it has integrated some of the fastest ones available, as
well as some achieving an excellent speed/compression ratio:

.. class:: nav-list

* `BloscLZ <https://github.com/Blosc/c-blosc/blob/master/blosc/blosclz.h>`_:
  internal default compressor, heavily based on `FastLZ <http://fastlz.org/>`_.
* `LZ4 <http://fastcompression.blogspot.com/p/lz4.html>`_: a compact,
  very popular and fast compressor.
* `LZ4HC <http://fastcompression.blogspot.com/p/lz4.html>`_: a tweaked
  version of LZ4, produces better compression ratios at the expense of
  speed.
* `Snappy <https://code.google.com/p/snappy>`_: a popular compressor used in
  many places.
* `Zlib <http://www.zlib.net/>`_: a classic; somewhat slower than
  the previous ones, but achieving better compression ratios.
* `Zstd <http://www.zstd.net>`_: an extremely well balanced codec; it provides the best
  compression ratios among the others above, and at reasonably fast speed.


**Compression pre-filters**

.. image::   /images/shuffle.png

In some situations, using filters before doing the actual compression may
improve both performance and/or compression ratio.  Blosc comes with a
couple of filters (also called pre-conditioners) called `shuffle <https://speakerdeck.com/francescalted/new-trends-in-storing-large-data-silos-in-python>`_
and `bitshuffle <http://blosc.org/blog/new-bitshuffle-filter.html>`_
which rearrange bytes and bits in a clever way for the compression stage
to work more efficiently and specially, faster.

.. TODO: link to a description of the shuffle filter.

.. class:: col-md-4

Professional services
---------------------

**NEW:** We are providing `professional services <http://www.blosc.org/professional-services.html>`_ for Blosc and its ecosystem.

.. |--| unicode:: U+2013   .. en dash

