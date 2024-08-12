.. title: Peaking compression performance in PyTables with direct chunking
.. author: Ivan Vilata-i-Balaguer
.. slug: pytables-direct-chunking
.. date: 2024-08-2X 11:00:00 UTC
.. tags: pytables performance
.. category:
.. link:
.. description:
.. type: text

It took a while to put things together, but after many months of hard work by maintainers, developers and contributors, `PyTables 3.10 <https://groups.google.com/g/pytables-users/c/XXXXTODOXXXX>`_ finally saw the light, full of `enhancements and fixes <https://www.pytables.org/release-notes/RELEASE_NOTES_v3.10.x.html>`_.  Thanks to a `NumFOCUS <https://numfocus.org/>`_ Small Development Grant, we were able to include a new feature that can help you squeeze considerable performance improvements when using compression: the direct chunking API.

In a `previous post about optimized slicing <https://www.blosc.org/posts/pytables-b2nd-slicing/>`_ we saw the advantages of avoiding the overhead introduced by the HDF5 filter pipeline, in particular when working with `multi-dimensional arrays compressed with Blosc2 <https://www.blosc.org/posts/pytables-b2nd-slicing/>`_.  This is achieved by specialized, low-level code in PyTables which understands the structure of the compressed data in each chunk and accesses it directly, with the least possible intervention of the HDF5 library.

However, there are many reasons to exploit direct chunk access in your own code, from customizing compression with parameters not allowed by the PyTables `Filters` class, to using yet-unsupported compressors or even helping you develop new plugins for HDF5 to support them (you may write compressed chunks in Python while decompressing transparently in a C filter plugin, or vice versa).  And of course, as we will see, skipping the HDF5 filter pipeline with direct chunking may fulfill the extreme I/O performances required in scenarios like continuous collection or extraction of data.

PyTables' new direct chunking API is the extra step that gives you access to these possibilities.  Keep in mind though that this is a very low-level functionality that may help you largely customize and accelerate access to your datasets, but may also break them.  In this post we'll try to show how to use it to get the best results.

TODO
