.. title: Caterva slicing performance
.. author: Oscar Guiñon, Francesc Alted
.. slug: caterva-slicing-perf
.. date: 2021-07-26 4:32:20 UTC
.. tags: caterva slicing perf
.. category:
.. link:
.. description:
.. type: text


.. image:: /images/cat_slicing/caterva.png
  :width: 70%
  :align: center

Caterva is a C library for handling multi-dimensional, chunked, compressed datasets in an easy and fast way.
Caterva can be used for a lot of different situations. However, where it really stands out is for extracting multidimensional slices of compressed datasets, thanks to the partitioning schema that it implements, the amount of data that has to decompress so as to get the slice is minimized, making things (usually) faster.

Accordingly, for cases where general slicing performance is important, Caterva turns out to be a good alternative to other solutions like Zarr or HDF5.


Double partitioning
-------------------

.. image:: /images/cat_slicing/cat_vs_zarr,hdf5.png
  :width: 70%
  :align: center

Some libraries like HDF5 or Zarr store data into multidimensional chunks. This makes slice extraction from compressed datasets more efficient than using monolithic compression, since only the chunks containing the interesting slice are decompressed instead of the entire array.

In addition, Caterva introduces a new level of partitioning.  Within each chunk, the data is re-partitioned into smaller multidimensional sets called blocks.  This generally improves the slice extraction, since it allows to decompress only the blocks containing the slice instead of the whole chunks.


Slice extraction with Caterva, HDF5 and Zarr
--------------------------------------------

Now we are going to compare the ability to extract multidimensional slices from compressed data of Caterva, HDF5 and Zarr. 
The examples below consists in extracting some hyper-planes from chunked arrays with different properties and see how Caterva performs compared with other solutions.


2-dimensional array
-------------------

This is a 2-dimensional array and has the following properties, defined to optimize slice extraction from the second dimension:

.. code-block:: console

    shape = (8_000, 8_000)
    chunkshape = (4_000, 100)
    blockshape = (500, 25)

.. image:: /images/cat_slicing/dim0.png
  :width: 70%

.. image:: /images/cat_slicing/dim1.png
  :width: 70%

Here we can see that the ratio between chunkshape and blockshape is 8x in dimension 0 and 4x in dimension 1.

Now we are going to extract some planes from the chunked arrays, and will plot the performance. For dimension 0 we extract a hyperplane of shape {1, 8000}, and for dimension 2 it has a {8000, 1} shape.

.. image:: /images/cat_slicing/2dim.png
  :width: 70%
  :align: center

Here we see that the slicing times are similar in the dimension 1. However, Caterva performs better in the dimension 0. This is because with double partitioning you only have to decompress the blocks containing the slice instead of the whole chunk.

In fact, Caterva is around 12x faster than HDF5 and 9x faster than Zarr for slicing the dimension 0, which makes sense since Caterva decompresses 8x less data.
For the dimension 1, Caterva is approximately 3x faster than HDF5 and Zarr; in this case Caterva has to decompress 4x less data.

To sum up, we have seen that the difference of slice extraction speed depends largely on the difference between the chunk size and the block size. Therefore, for slices where the chunks that contain the slice also have many elements that do not belong to it, the existence of blocks (the second partition) allows to significantly reduce the amount of data to decompress.


Overhead of the second partition
--------------------------------

Let's see a new case of a 3-dimensional array with the following parameters:

.. code-block:: console

    shape = (800, 600, 300)
    chunkshape = (200, 100, 80)
    blockshape = (20, 100, 10)

Here it is shown that in the dimensions 0 and 2 the difference between shape and chunkshape is not too big and the difference between chunkshape and blockshape is remarkable.

However, for the dimension 1, there is not a difference at all between chunkshape and blockshape.  This means that in dimension 1 the Caterva machinery will make extra work because of the double partitioning, but it will not get any advantage of it since the block size is going to be equal to the chunk size.

The slices we are going to extract will have the shapes {1, 600, 300}, {800, 1, 300} or {800, 600, 1}. Let's see the execution times for slicing these planes:

.. image:: /images/cat_slicing/3dim.png
  :width: 70%
  :align: center

As we can see, in the dimension 1 the performance is around the same order than HDF5 and Zarr (Zarr being a bit faster actually), but difference is not large, so that means that the overhead introduced by the second partition is not that important.
However, in the other dimensions Caterva still outperforms (by far) Zarr and HDF5.  This is because the two level partitioning works as intended here.


A last hyper-slicing example
---------------------------

This is a 4-dimensional array and has the following parameters:

.. code-block:: console

    shape = (400, 80, 100, 50)
    chunkshape = (100, 40, 10, 50)
    blockshape = (30, 5, 2, 10)

.. image:: /images/cat_slicing/4dim.png
  :width: 70%
  :align: center

Here the last dimension (3) is not optimized for getting hyper-slices, specially in containers with just single partitioning (Zarr and HDF5).  However, Caterva should still perform well in this situation because of the double partitioning.

The slices we are going to extract will have the shapes {1, 80, 100, 50}, {400, 1, 100, 50}, {400, 80, 1, 50} or {400, 80, 100, 1}. Let's see the execution times for slicing these hyper planes:

.. image:: /images/cat_slicing/4dim.png
  :width: 70%
  :align: center

As we can see, in this case Caterva outperforms Zarr and HDF5 in all dimensions.  However, the advantage is not that important for the last dimension.  The reason is that in this last dimension Caterva has a noticeably lower ratio between its shape and blockshape than in the other dimensions.


Final thoughts
--------------

We have seen that adding a second partition is beneficial for slicing performance in general.  Of course, there are some situations where the overhead of the second partition can be noticeable, but the good news is that such an overhead does not get too large when compared with containers with only one level of partitioning.

Finally, we can conclude that Caterva usually obtains better results due to its second partitioning, but when it shines the most is when the two levels of partitioning are well balanced with respect to the shape of the container.

For more a more interactive experience, have a look at `our Caterva poster <https://github.com/Blosc/caterva-scipy21>`_.
