.. title: Optimized Hyper-slicing in PyTables with Blosc2 NDim
.. author: Ivan Vilata-i-Balaguer
.. slug: pytables-b2nd-slicing
.. TODO use actual date
.. date: 2023-10-08 12:34:56 UTC
.. tags: pytables blosc2 ndim performance
.. category:
.. link:
.. description:
.. type: text

The recent and long-awaited PyTables 3.9 release carries many goodies, including a particular one which makes us at the PyTables and Blosc teams very excited: optimized HDF5 hyper-slicing that leverages the double partition schema in Blosc2 NDim. This development was funded by a `NumFOCUS <https://numfocus.org/>`_ grant and the Blosc project.

I (Ivan) carried on with the work that Marta started, with very valuable help from her and Francesc. I was in fact a core PyTables developer quite a few years ago (2004-2008) while working with Francesc and Vicent at Cárabos Coop. V. (see the `20 year anniversary post <https://www.blosc.org/posts/pytables-20years/>`_ for more info), and it was an honour and a pleasure to be back at the project. It took me a while to get back to grips with development, but it was a nice surprise to see the code that we worked so hard upon live through the years and get better and more popular. My heartfelt thanks to everybody who made that possible!

You may remember that the previous version of PyTables (3.8.0) already got support for optimized HDF5 chunk access, and fast decompression of small slices in big chunks using Blosc2's two-level partitioning. If not, make sure to read Óscar and Francesc's great post `Blosc2 Meets PyTables <https://www.blosc.org/posts/blosc2-pytables-perf/>`_ to see the great performance gains provided by these techniques.

However, these enhancements only applied to tabular datasets, i.e. one-dimensional arrays of a uniform, fixed set of fields (columns) with heterogeneous data types. Multi-dimensional compressed arrays of homogeneous data (another popular feature of PyTables) still used plain chunking going through the HDF5 filter pipeline, and flat chunk compression. Thus, they suffered from the high overhead of the very generic pipeline and the inefficient decompression of small slices in the case of big chunks.

TODO
