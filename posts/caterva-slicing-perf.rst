.. title: Caterva slicing performance
.. author: Oscar Guiñon
.. slug: caterva-slicing-perf
.. date: 2021-07-26 4:32:20 UTC
.. tags: caterva slicing perf
.. category:
.. link:
.. description:
.. type: text


.. image:: /images/cat_slicing/caterva.png
  :width: 30%
  :align: center

Caterva is a C library for handling multi-dimensional, chunked, compressed datasets in an easy and fast way.
Caterva can be used for a lot of different situations. However, where it really stands out is for extracting multidimensional slices of compressed datasets because, and thanks to the partitioning schema that it implements, it minimizes the amount of data that has to decompress so as to get the slice, making things faster.
Accordingly, for cases where the slicing performance is important, Caterva turns out to be a good alternative to other solutions like Zarr or HDF5.


Double partitioning
-------------------

.. image:: /images/cat_slicing/cat_vs_zarr,hdf5.png
  :width: 70%
  :align: center

Some chunking libraries like HDF5 or Zarr store data into multidimensional chunks. This makes slices extraction from compressed datasets more efficient since only the chunks containing the slices are decompressed instead of the entire array.

In addition, Caterva introduces a new level of partitioning. Within each chunk, the data is repartitioned into smaller multidimensional sets called blocks.
This improves even more the slices extration, since it allows to decompress only the blocks that contain the slice instead of the whole chunks.


Slice extraction with Caterva, HDF5 and Zarr
--------------------------------------------

Now we are going to compare the ability to extract multidimensional slices from compressed data of Caterva, HDF5 and Zarr. 
The example we are going to work with consists of extracting some hyperplanes from chunked arrays created with the different containers.


2-dimensional array
-------------------

This is a 2-dimensional array and has the following parameters, defined to optimize the hyperslices extraction from the second dimension:

.. code-block:: console

    shape = (8_000, 8_000)
    chunkshape = (4_000, 100)
    blockshape = (500, 25)

.. image:: /images/cat_slicing/dim0.png
  :width: 70%

.. image:: /images/cat_slicing/dim1.png
  :width: 70%

Then we can see that the difference between chunkshape and blockshape is of a factor 8 in dimension 0 and factor 4 in dimension 1. 

Now some hyperplanes from the chunked arrays are extracted, and the performance speed is measured using the *memprofiler* plugin for Jupyter.

.. image:: /images/cat_slicing/2dim.png
  :width: 70%
  :align: center

Here it is shown that the slicing times are similar in the optimized dimension (1). However, Caterva performs better in the non-optimized dimension (0). This is because with double partitioning you only have to decompress the blocks containing the slice instead of the whole chunk.

In fact, Caterva is approximately 12 times faster than HDF5 and 9 times faster than Zarr for slicing the first dimension, which makes sense since Caterva decompresses 8 times less data.
For the second dimension, Caterva is approximately 3 times faster than HDF5 and Zarr decompressing 4 times less data.

To sum up, we have seen that the difference of hyperplanes extraction speed depends largely on the difference between the chunk size and the block size. Therefore, for slices where the chunks that contain the slice also have many elements that do not belong to it, the appearance of blocks allows to significantly reduce the amount of data to decompress.


3-dimensional array
-------------------

This is a 3-dimensional array and has the following parameters:

.. code-block:: console

    shape = (800, 600, 300)
    chunkshape = (200, 100, 80)
    blockshape = (20, 100, 10)

Here it is shown that in the dimensions 0 and 2 the difference between shape and chunkshape is not too big and the difference between chunkshape and blockshape is remarkable. 
However, the dimension 1 is optimized for Zarr and HDF5, since it has a big difference between shape and chunkshape and not difference between chunkshape and blockshape. 
This means that in dimension 1 Caterva machinery will make extra work because of the double partitioning but will not obtain any advantage of it since blocks will be equals to chunks.

Let's see the execution times for slicing some hyperplanes:

.. image:: /images/cat_slicing/3dim.png
  :width: 70%
  :align: center

As we can see, in the optimized dimension (1) the performance is similar and Zarr has even better time than Caterva, but difference is not big even in this bad situation for Caterva. 
However, in the other dimensions Caterva overperforms by far Zarr and HDF5. This is due to the two level partitioning in the Caterva arrays.

In this example, while Zarr and HDF5 have to decompress all the chunks of the arrays in the non-optimized dimenisons, Caterva only has to decompress the blocks that contain data from the slice, obtaining better results.


4-dimensional array
-------------------

This is a 4-dimensional array and has the following parameters:

.. code-block:: console

    shape = (400, 80, 100, 50)
    chunkshape = (100, 40, 10, 50)
    blockshape = (30, 5, 10, 10)

.. image:: /images/cat_slicing/4dim.png
  :width: 70%
  :align: center

Here it is shown that the dimension 2 is optimized for Zarr and HDF5 (like the dimension 1 was in the previous example) and the dimension 3 has a not convenient chunkshape, so Caterva has an advantage in front of the other containers.
Theorically, Caterva should perform the best in the last dimension (3) compared to Zarr and HDF5 because they are on disadvantage.

Let's see the execution times for slicing some hyperplanes:

.. image:: /images/cat_slicing/4dim.png
  :width: 70%
  :align: center

As we can see, in the optimized dimension (2) the performance is similar and Caterva has the worst time, but again difference is not big even in this bad situation for Caterva. 
On the other hand, in the other dimensions Caterva overperforms Zarr and HDF5 again with more difference. 
However, the dimension where Caterva worst overperforms them is the last one (3), where it supposedly has the biggest advantage.
The reason for this is that in dimension 3 Caterva has less difference between its shape and blockshape than in dimensions 0 and 1. 

Therefore, we can conclude that Caterva obtains better results in these situations because of its second partitioning, but but when it performs best is when the two levels are correctly combined. That is, when the chunk and block sizes are appropriate. 



