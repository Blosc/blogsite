.. title: Optimized Hyper-slicing in PyTables with Blosc2 NDim
.. author: Ivan Vilata-i-Balaguer
.. slug: pytables-b2nd-slicing
.. date: 2023-10-11 11:00:00 UTC
.. tags: pytables blosc2 ndim performance
.. category:
.. link:
.. description:
.. type: text

The recent and long-awaited `PyTables 3.9 release <https://groups.google.com/g/pytables-users/c/JTtZrw8sUEc>`_ carries `many goodies <https://www.pytables.org/release-notes/RELEASE_NOTES_v3.9.x.html>`_, including a particular one which makes us at the PyTables and Blosc teams very excited: optimized HDF5 hyper-slicing that leverages the two-level partitioning schema in Blosc2 NDim. This development was funded by a `NumFOCUS <https://numfocus.org/>`_ grant and the Blosc project.

I (Ivan) carried on with the work that Marta started, with very valuable help from her and Francesc. I was in fact a core PyTables developer quite a few years ago (2004-2008) while working with Francesc and Vicent at Cárabos Coop. V. (see the `20 year anniversary post <https://www.blosc.org/posts/pytables-20years/>`_ for more information), and it was an honour and a pleasure to be back at the project. It took me a while to get back to grips with development, but it was a nice surprise to see the code that we worked so hard upon live through the years and get better and more popular. My heartfelt thanks to everybody who made that possible!

**Update (2023-11-23):** We redid the benchmarks described further below with some fixes and the same versions of Blosc2 HDF5 filter code for both PyTables and h5py. Results are more consistent and easier to interpret now.

**Update (2023-12-04):** We extended benchmark results with the experimental application of a similar optimization technique to h5py.

Direct chunk access and two-level partitioning
----------------------------------------------

You may remember that the previous version of PyTables (3.8.0) already got support for direct access to Blosc2-compressed chunks (bypassing the HDF5 filter pipeline), with two-level partitioning of chunks into smaller blocks (allowing for fast access to small slices with big chunks). You may want to read Óscar and Francesc's post `Blosc2 Meets PyTables <https://www.blosc.org/posts/blosc2-pytables-perf/>`_ to see the great performance gains provided by these techniques.

.. image:: /images/blosc2_pytables/block-slice.png
  :width: 66%
  :align: center

However, these enhancements only applied to tabular datasets, i.e. one-dimensional arrays of a uniform, fixed set of fields (columns) with heterogeneous data types as illustrated above. Multi-dimensional compressed arrays of homogeneous data (another popular feature of PyTables) still used plain chunking going through the HDF5 filter pipeline, and flat chunk compression. Thus, they suffered from the high overhead of the very generic pipeline and the inefficient decompression of whole (maybe big) chunks even for small slices.

Now, you may have also read the post by the Blosc Development Team about `Blosc2 NDim <https://www.blosc.org/posts/blosc2-ndim-intro/>`_ (`b2nd`), first included in C-Blosc 2.7.0. It introduces the generalization of Blosc2's two-level partitioning to multi-dimensional arrays as shown below. This makes arbitrary slicing of such arrays across any dimension very efficient (as better explained in the post about `Caterva <https://www.blosc.org/posts/caterva-slicing-perf/>`_, the origin of b2nd), when the right chunk and block sizes are chosen.

.. image:: /images/blosc2-ndim-intro/b2nd-2level-parts.png
  :width: 66%
  :align: center

This b2nd support was the missing piece to extend PyTables' chunking and slicing optimizations from tables to uniform arrays.

Choosing adequate chunk and block sizes
---------------------------------------

Let us try a benchmark very similar to the one in the post introducing `Blosc2 NDim`_, which slices a 50x100x300x250 floating-point array (2.8 GB) along its four dimensions, but this time with 64-bit integers, and using PyTables 3.9 with flat slicing (via the HDF5 filter pipeline), PyTables 3.9 with b2nd slicing (optimized, via direct chunk access), and h5py 3.10 (with support for Blosc2 in the HDF5 filter pipeline via hdf5plugin 4.3).

According to the aforementioned post, Blosc2 works better when blocks have a size which allows them to fit both compressed and uncompressed in each CPU core’s L2 cache. This of course depends on the data itself and the compression algorithm and parameters chosen. Let us choose LZ4+shuffle since it offers a reasonable speed/size trade-off, and try to find the different compression levels that work well with our CPU (level 8 seems best in our case).

With the benchmark's default 10x25x50x50 chunk shape, and after experimenting with the ``BLOSC_NTHREADS`` environment variable to find the number of threads that better exploit Blosc2's parallelism (6 for our CPU), we obtain the results shown below:

.. image:: /images/pytables-b2nd-slicing/b2nd_getslice_small.png
  :width: 75%
  :align: center

The optimized b2nd slicing of PyTables already provides some speedups (although not that impressive) in the inner dimensions, in comparison with flat slicing based on the HDF5 filter pipeline (which performs similarly for PyTables and h5py). As explained in `Blosc2 Meets PyTables`_, HDF5 handling of chunked datasets favours big chunks that reduce in-memory structures, while Blosc2 can further exploit parallel threads to handle the increased number of blocks. Our CPU's L3 cache is 36MB big, so we may still grow the chunksize to reduce HDF5 overhead (without hurting Blosc2 parallelism).

Let us raise the chunkshape to 10x25x150x100 (28.6MB) and repeat the benchmark (again with 6 Blosc2 threads):

.. image:: /images/pytables-b2nd-slicing/b2nd_getslice_big.png
  :width: 75%
  :align: center

Much better! Choosing a better chunkshape not just provides up to 10x speedup for the PyTables optimized case, it also results in 4x-5x speedups compared to the performance of the HDF5 filter pipeline.

Conclusions and future work
---------------------------

The benchmarks above show how optimized Blosc2 NDim's two-level partitioning combined with direct HDF5 chunk access can yield considerable performance increases when slicing multi-dimensional Blosc2-compressed arrays under PyTables. However, the usual advice holds to invest some effort into fine-tuning some of the parameters used for compression and chunking for better results. We hope that this article also helps readers find those parameters.

It is worth noting that these techniques still have some limitations: they only work with contiguous slices (that is, with step 1 on every dimension), and on datasets with the same byte ordering as the host machine. Also, although results are good indeed, there may still be room for implementation improvement, but that will require extra code profiling and parameter adjustments.

Finally, as mentioned in the `Blosc2 NDim`_ post, if you need help in `finding the best parameters <http://btune.blosc.org/>`_ for your use case, feel free to reach out to the Blosc team at `contact (at) blosc.org`.

Enjoy data!
