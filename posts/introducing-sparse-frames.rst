.. title: Introducing Sparse Frames
.. author: Marta Iborra
.. slug: introducing-sparse-frames
.. date: 2021-02-08 7:32:20 UTC
.. tags: blosc2 sparse frame format
.. category: posts
.. link:
.. description:
.. type: text


Overview
--------

The `new sparse frame implementation <https://github.com/Blosc/c-blosc2/pull/176>`_
allows the storage of Blosc2 super-chunk data chunks sparsely on-disk, using the filesystem as a key/value storage.
This mimics existing formats like `bcolz <https://github.com/Blosc/bcolz/blob/master/DISK_FORMAT_v1.rst>`_
or `Zarr <https://zarr.readthedocs.io/en/stable/spec/v2.html>`_.

For the sparse implementation we are making use of the existing `contiguous frame
<https://github.com/Blosc/c-blosc2/blob/master/README_CFRAME_FORMAT.rst>`_,
in order to store the metadata and the index for accessing the different chunks.
Here you can see the new sparse format compared with the existing contiguous frame:

.. image:: /images/sparse-frames/cframe-vs-sframe.png
  :width: 70%
  :align: center

As can be seen in the image above, the contiguous frame file is made of
a header, a chunks section and a trailer.
The header contains information needed to decompress the chunks and the
trailer contains a user meta data chunk.
The chunks section for a contiguous frame is made of all the data chunks plus the index chunk.
The latter contains the offset where each chunk begins inside the contiguous frame.
All these pieces are stored sequentially, without any empty spaces between them.

However, in a sparse frame the chunks are stored somewhere as independent binary files.
But there is still the need to store the information to decompress the chunks as well as
a place to store the user meta data.  All this goes to the `chunks.b2frame`, which is
actually a contiguous frame file with the difference that its chunks section contains only
the index chunk.  This index chunk stores the ID of each chunk (an integer from 0 to 2^32-1).
The name of the chunk file is built by expressing the chunk ID in hexadecimal,
padded with zeros (until 8 characters) and adding the `.chunk` extension.
For example, if the index chunk is 46 (2E in hexadecimal) the chunk file name would
be `0000002E.chunk`.


Advantages
----------

The big advantage of the sparse frame compared with the contiguous one is
avoiding empty spaces resulting when updating a chunk.

To better illustrate this, let's imagine that the set of the data chunks in
a contiguous frame is stored like in the
`Jenga board game tower <https://en.wikipedia.org/wiki/Jenga>`_, a tower
built with wood blocks.  But in constrast to the genuine
`Jenga board game`, not all the blocks have the same size (the uncompressed
size of a the chunks is the same, but not the compressed one):

.. figure:: /images/sparse-frames/jenga3.png
  :width: 50%
  :align: center

Above it is shown the initial structure of such a tower. If the yellow piece
is updated (changed by another piece) there are two possibilities.
The first one is that the new piece fits into the empty space left where
the old piece was. In that case, the new piece is put in the previous space
without any problem and we have no empty spaces left.  However, if the new piece
does not fit into the empty space, the new piece has to be placed at the
top of the tower (like in the game), leaving an empty space where the old piece was.

On the other hand, the chunks of an sparse frame can be seen as books on a shelf, where
each book is a different chunk:

.. image:: /images/sparse-frames/bookshelf.png
  :width: 50%
  :align: center

If one needs to update one book with
the new, taller edition, one only has to grab the old edition and replace it by the new one.
As there is no limit in the height of the books, the yellow book can be replaced with a
larger book without creating empty spaces, and making a better use of space.

Example of use
--------------

Creating a sparse frame in C-Blosc2 is easy; just specifify the name of the directory where
you want to store your chunks and you are done::

  blosc2_storage storage = {.urlpath="dir1.b2frame"};
  schunk = blosc2_schunk_new(storage);
  for (nchunk = 0; nchunk < NCHUNKS; nchunk++) {
      blosc2_schunk_append_buffer(schunk, data, isize);
  }

The above will create NCHUNKS of chunks in the "dir.b2frame".  After that, you can open and read
the frame with::

  schunk = blosc2_schunk_open("dir1.b2frame");
  for (nchunk = 0; nchunk < NCHUNKS; nchunk++) {
      blosc2_schunk_decompress_chunk(schunk, nchunk, data_dest, isize);
  }

Simple and effective.

You can have a look at a `more complete example here 
<https://github.com/Blosc/c-blosc2/blob/master/examples/sframe_simple.c>`_.


Future work
-----------

We think that this implementation opens the door to several interesting possibilities.

For example, by introducing networking code in Blosc2,
the chunks could be stored in another machine and accessed remotely.
That way, with just the metadata (the contiguous frame) we could
access all the data chunks in the sparse frame.

For example, let's suppose that we have a sparse frame with 1 million chunks.
The total size of the data chunks from this sparse frame is 10 TB, but the
contiguous frame size can be as small as 10 KB.  So, with just sending an
small object of 10 KB, any worker could access the whole 10 TB of data.

The remote stores could be typical networked key/value databases. The key is the identifier
for each element of the database, whereas the value is the information that is associated
to each key (similar to a set of unique keys and a set of doors). In this case, the key would
be built from the metadata (e.g. a URL) plus the index of the chunk, and the value would be
the data chunk itself.

This can lead to a whole new range of applications, where data can be spread in the
cloud and workers can access to it by receiving small amounts of serialized buffers (the
contiguous frame).  This way, arbitrarily large data silos could be created and accessed
via the C-Blosc2 library (plus a key/value network store).

*Note by Francesc*: The implementation of sparse frames has been done by Marta Iborra, who
is the main author of this blog too.  Marta joined the Blosc team a few months ago as a student,
and the whole team is very pleased with the quality of her contribution; we would be thrilled
to continue having her among us for the next months (but this requires some budget indeed).
If you like where we are headed, please consider making a donation
to the Blosc project via the NumFOCUS Foundation: https://blosc.org/pages/donate.  Thank you!
