.. title: What Is Blosc?
.. slug: blosc-in-depth
.. date: 2025-07-11 11:11:07 UTC
.. tags:
.. link:
.. description:
.. type: text
.. .. template: story.tmpl


Blosc2 is a high-performance compressor and data format optimized for binary data. As the successor to the original Blosc library, it is designed for speed by leveraging multi-threading and SIMD instructions (SSE2, AVX2, AVX512, NEON, ALTIVEC). It uses a **blocking technique** to divide datasets into blocks that fit in CPU caches, dramatically reducing memory bus activity and `breaking down memory walls <https://www.blosc.org/posts/posts/breaking-down-memory-walls/>`_.

With a `large diversity of codecs and filters <https://www.blosc.org/posts/bytedelta-enhance-compression-toolset/>`_, Blosc2 allows developers to fine-tune the balance between compression speed and ratio. It is a mature, open-source project with over 60 contributors and 3500+ commits, and is integrated into many popular scientific computing libraries, such as `PyTables <https://www.pytables.org>`_, `h5py <https://www.h5py.org>`_ (via `hdf5plugin <https://hdf5plugin.readthedocs.io>`_), and `Zarr <https://zarr.dev>`_.

Watch this introductory video to learn more about the main features of Blosc:

.. youtube:: ER12R7FXosk
   :width: 50%
   :align: center

.. raw:: html

   <br><br>

Key Features
------------

Blosc2 offers several advantages that make it a compelling choice for high-performance applications:

* **Optimized for Binary Data**: Uses shuffle and bit-shuffle filters (among others) that leverage data type information to improve compression ratios. It also has minimal overhead (max 32 bytes per chunk) on non-compressible data.

* **Multi-platform**: Supports a wide range of platforms, including Linux, macOS, Windows, and WebAssembly (WASM). It is `written in C <https://www.blosc.org/c-blosc2>`_, with `bindings available for Python <https://www.blosc.org/python-blosc2>`_.

* **Multi-Dimensional Data (NDim)**: Provides native support for n-dimensional datasets through its `NDim container <https://www.blosc.org/posts/blosc2-ndim-intro/>`_. This container uses an innovative partitioning scheme that enables highly efficient slicing operations, even on `sparse datasets <https://www.blosc.org/docs/Exploring-MilkyWay-SciPy2023.pdf>`_.

.. youtube:: LvP9zxMGBng
   :width: 50%
   :align: center

* **Large Containers**: Supports data sizes up to 2^62 bytes (4 exabytes) through its super-chunk implementation, overcoming the 2 GB limitation of Blosc1.

* **Persistent Storage**: Includes `Frames <https://github.com/Blosc/c-blosc2/blob/main/README_CFRAME_FORMAT.rst>`_, a container format for serializing data in-memory or on-disk.

* **Advanced Computing with Python**: The `Python-Blosc2 <https://www.blosc.org/python-blosc2>`_ package is more than a wrapper. It provides a powerful computing engine for performing `lazy evaluations <https://ironarray.io/blog/compute-bigger>`_ on compressed data, including reductions, broadcasting and support for many NumPy functions, avoiding the need to decompress data before processing. This is particularly useful for large datasets, as it allows you to work with data that doesn't fit in memory.

.. figure:: /images/blosc2-vs-others-compute.png
   :width: 75%
   :align: center

For a complete list of features, please refer to our `ROADMAP <https://github.com/Blosc/c-blosc2/blob/main/ROADMAP.rst>`_ and recent `progress reports <https://www.blosc.org/docs/Blosc2-HDF5-LEAPS-INNOV-Meeting-2024-04-08.pdf>`_.

Open and Extensible
-------------------

Blosc2 is an `open and fully documented format <https://github.com/Blosc/c-blosc2/blob/main/README.rst#open-format>`_, ensuring you are not locked into a proprietary solution. The specification is concise and easy to implement.

We understand that every use case is unique. You can `register your own codecs and filters <https://www.blosc.org/posts/registering-plugins/>`_ to adapt Blosc2 to your specific needs. Furthermore, `Btune <https://ironarray.io/btune>`_, a machine learning tool, can automatically find the optimal compression parameters for your data.

Get Involved
------------

The home for all Blosc-related libraries is on GitHub. You can download the source code, file tickets, and contribute to the project there.

* **GitHub**: https://github.com/Blosc
* **C-Blosc2 Documentation**: https://www.blosc.org/c-blosc2
* **Python-Blosc2 Documentation**: https://www.blosc.org/python-blosc2

Stay informed about the latest developments by following us on our social networks:

* **LinkedIn**: https://www.linkedin.com/company/blosc
* **Mastodon**: https://fosstodon.org/@Blosc2
* **BlueSky**: https://bsky.app/@blosc.org
* **Mailing List**: http://groups.google.com/group/blosc

.. _support-blosc:

Support Blosc for a Sustainable Future
---------------------------------------

Blosc is the result of countless hours of effort by dedicated developers and the generous backing of organizations like `NumFOCUS <https://numfocus.org>`_ and `ironArray SLU <https://ironarray.io>`_. Financial contributions are critical for the long-term sustainability of open-source projects like Blosc.

Your support helps us continue development, maintenance, and innovation. Here are some ways you can contribute financially:

1. **NumFOCUS**: Blosc is a `fiscally sponsored project of NumFOCUS <https://numfocus.org/project/blosc>`_, a nonprofit supporting open-source scientific computing.
2. **ironArray**: `ironArray SLU <https://ironarray.io>`_ was instrumental in developing Blosc2 and offers `commercial support and consulting services <https://ironarray.io/services>`_.
3. **GitHub Sponsorship**: Support us directly by clicking the `"Sponsor" button <https://github.com/sponsors/FrancescAlted>`_ on GitHub.

Thank you for helping us build a sustainable future for the Blosc ecosystem!

-- The Blosc Development Team
