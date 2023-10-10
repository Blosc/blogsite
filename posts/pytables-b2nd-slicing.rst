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

Direct chunk access and two-level partitioning
----------------------------------------------

You may remember that the previous version of PyTables (3.8.0) already got support for optimized access to Blosc2-compressed chunks (bypassing the HDF5 filter pipeline), with two-level partitioning of chunks into smaller blocks (allowing for fast access to small slices with big chunks). You may want to read Óscar and Francesc's post `Blosc2 Meets PyTables <https://www.blosc.org/posts/blosc2-pytables-perf/>`_ to see the great performance gains provided by these techniques.

.. image:: /images/blosc2_pytables/block-slice.png
  :width: 66%
  :align: center

However, these enhancements only applied to tabular datasets, i.e. one-dimensional arrays of a uniform, fixed set of fields (columns) with heterogeneous data types as illustrated above. Multi-dimensional compressed arrays of homogeneous data (another popular feature of PyTables) still used plain chunking going through the HDF5 filter pipeline, and flat chunk compression. Thus, they suffered from the high overhead of the very generic pipeline and the inefficient decompression of small slices in the case of big chunks.

Now, you may have also read the post by the Blosc Development Team about `Blosc2 NDim support <https://www.blosc.org/posts/blosc2-ndim-intro/>`_ (`b2nd`), first included in C-Blosc 2.7.0. It introduces the generalization of Blosc2's two-level partitioning to multi-dimensional arrays as shown below. This makes arbitrary slicing of such arrays across any dimension very efficient (as better explained in the post about `Caterva <https://www.blosc.org/posts/caterva-slicing-perf/>`_, the origin of `b2nd`), when the right chunk and block sizes are chosen.

.. image:: /images/blosc2-ndim-intro/b2nd-2level-parts.png
  :width: 66%
  :align: center

This `b2nd` support was the missing piece to extend PyTables' chunking and slicing optimizations from tables to uniform arrays.

Choosing adequate chunk and block sizes
---------------------------------------

Let us try a benchmark very similar to that in the post introducing `Blosc2 NDim support`_, which slices a 50x100x300x250 floating-point array (2.8 GB) along its four dimensions, but this time using PyTables with flat slicing (via the HDF5 filter mechanism), PyTables with b2nd slicing (optimized via direct chunk access), and h5py (which also uses the HDF5 filter).

TODO
