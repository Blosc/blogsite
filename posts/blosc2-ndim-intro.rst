.. title: Introducing Blosc2 NDim
.. author: The Blosc Development Team
.. slug: blosc2-ndim-intro
.. date: 2023-02-21 10:32:20 UTC
.. tags: blosc2 ndim performance
.. category:
.. link:
.. description:
.. type: text

One of the latest and more exciting additions in recently released C-Blosc2 2.7.0 is the `Blosc2 NDim layer <https://www.blosc.org/c-blosc2/reference/b2nd.html>`_ (or `b2nd` for short).  It allows to create *and* read n-dimensional datasets in an extremely efficient way thanks to a completely general n-dim 2-level partitioning, allowing to slice and dice arbitrary large (and compressed!) data in a more fine-grained way.

This capability was formerly part of `Caterva <https://github.com/Blosc/caterva>`_, and now we are including it in C-Blosc2 for convenience.  As a consequence, the Caterva and `Python-Caterva <https://github.com/Blosc/python-caterva>`_ projects are now officially deprecated and all the action will happen in the `C-Blosc2 <https://github.com/Blosc/c-blosc2>`_ / `Python-Blosc2 <https://github.com/Blosc/python-blosc2>`_ side of the things.

Going multidimensional in the first *and* the second partition
--------------------------------------------------------------

Blosc (both Blosc1 and Blosc2) has always had a two-level partition schema to leverage the different cache levels in modern CPUs and make compression happen as quickly as possible.  With Blosc2 NDim we are taking a step further and both partitions, known as chunks and blocks, are gaining multidimensional capabilities meaning that one can split some dataset (`super-chunk` in Blosc2 parlance) in such a n-dim pieces:

.. image:: /images/blosc2-ndim-intro/b2nd-2level-parts.png
  :width: 75%

With these more fine-grained partitions, it is possible to retrieve arbitrary n-dim slices more rapidly because you don't have to decompress data that would be necessary for the coarse-grained partitions typical in other libraries.

Remember that having a second partition means that we have better flexibility to fit the different partitions at the different CPU cache levels; typically the first partition (aka chunks) should be made to fit in L3 cache, whereas the second partition (aka blocks) should rather fit in L2/L1 caches (depending on whether compression ratio or speed is desired).

For example, for a 4-d array with a shape of (50, 100, 300, 250) with `float64` items, we can choose a chunk with shape (10, 25, 50, 50) and a block with shape (3, 5, 10, 20) which makes for about 5 MB and 23 KB respectively.  This way, a chunk fits comfortably on a L3 cache in most of modern CPUs, and a block in a L1 cache (we are tuning for speed here).  With that configuration, the NDArray object in the Python-Blosc2 package can slice the array as shown below:

.. image:: /images/blosc2-ndim-intro/Read-Partial-Slices-B2ND.png
  :width: 75%

The advantage of the second partition is very apparent here.  Above we have been using the Zstd codec with compression level 1 (the fastest inside Blosc2) + the Shuffle filter for all the libraries.  The box used was an Intel 13900K CPU with 32 GB of RAM and using an up-to-date `Clear Linux <https://clearlinux.org>`_ distro.

Of course, the double partitioning comes with some overhead during the creation of the partitions: more data moves and computations need to be done in order to place the data in the correct positions.  However, the Blosc2 team has done its best in order to do do as little data movement as possible and keep it under a minimum.  Below we can see how the creation (write) of an array from anew is still quite competitive:

.. image:: /images/blosc2-ndim-intro/Complete-Write-Read-B2ND.png
  :width: 75%

On the other hand, one can see that when reading the complete array, the double partitioning overhead is not really noticeable, and actually, it benefits Blosc2 NDArray somewhat (but very little, and probably due to the decompression happening at L1 level).

Conclusion
----------

We have seen how, when sensibly chosen, the double partition can provide a formidable boost in retrieving arbitrary slices in potentially large multidimensional arrays.  When this is combined with the excellent compression capabilities of Blosc2, we are getting a first class data container for many kinds of (mainly numerical) data.

We are still in the process of releasing the new `NDArray` object in Python-Blosc2.  This fully leverages this great combination of 2-level partition, compression and sensible use of CPU caches.  We expect to have production ready version very soon, and we would be grateful if you can help us in testing the new functionality.

If you regularly store and process large datasets and need advice to partition your data, or choosing the best combination of codec, filters, chunk and block sizes, or many other aspects of compression, do not hesitate to contact the Blosc team at `contact (at) blosc.org`.  We have more than 30 years of cumulative experience in data handling systems like HDF5, Blosc and efficient I/O in general; but most importantly, we have the ability to integrate these innovative technologies quickly into your products, enabling a faster access to these innovations.
