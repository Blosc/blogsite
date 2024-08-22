.. title: Peaking compression performance in PyTables with direct chunking
.. author: Ivan Vilata-i-Balaguer
.. slug: pytables-direct-chunking
.. date: 2024-08-2X 11:00:00 UTC
.. tags: pytables performance
.. category:
.. link:
.. description:
.. type: text

It took a while to put things together, but after many months of hard work by maintainers, developers and contributors, `PyTables 3.10 <https://groups.google.com/g/pytables-users/c/3giLIxT6Jq4>`_ finally saw the light, full of `enhancements and fixes <https://www.pytables.org/release-notes/RELEASE_NOTES_v3.10.x.html>`_.  Thanks to a `NumFOCUS <https://numfocus.org/>`_ Small Development Grant, we were able to include a new feature that can help you squeeze considerable performance improvements when using compression: the direct chunking API.

In a `previous post about optimized slicing <https://www.blosc.org/posts/pytables-b2nd-slicing/>`_ we saw the advantages of avoiding the overhead introduced by the HDF5 filter pipeline, in particular when working with `multi-dimensional arrays compressed with Blosc2 <https://www.blosc.org/posts/blosc2-ndim-intro/>`_.  This is achieved by specialized, low-level code in PyTables which understands the structure of the compressed data in each chunk and accesses it directly, with the least possible intervention of the HDF5 library.

However, there are many reasons to exploit direct chunk access in your own code, from customizing compression with parameters not allowed by the PyTables `Filters` class, to using yet-unsupported compressors or even helping you develop new plugins for HDF5 to support them (you may write compressed chunks in Python while decompressing transparently in a C filter plugin, or vice versa).  And of course, as we will see, skipping the HDF5 filter pipeline with direct chunking may be instrumental to reach the extreme I/O performance required in scenarios like continuous collection or extraction of data.

PyTables' new direct chunking API is the machinery that gives you access to these possibilities.  Keep in mind though that this is a very low-level functionality that may help you largely customize and accelerate access to your datasets, but may also break them.  In this post we'll try to show how to use it to get the best results.

Using the API
-------------

The direct chunking API consists of three operations: get information about a chunk (`chunk_info()`), write a raw chunk (`write_chunk()`), and read a raw chunk (`read_chunk()`).  They are supported by chunked datasets (`CArray`, `EArray` and `Table`), which have their data split into fixed-size chunks of the same dimensionality as the dataset (maybe padded at its boundaries) that are processed by filters like compressors.

`chunk_info()` returns an object with useful information about the chunk containing the item at the given coordinates.  Let's create a simple 100x100 array with 10x100 chunks compressed with Blosc2+Zstd and get info about a chunk::

    >>> import tables, numpy
    >>> h5f = tables.open_file('test.h5', mode='w')
    >>> filters = tables.Filters(complib='blosc2:zstd', complevel=5)
    >>> data = numpy.arange(100 * 100).reshape((100, 100))
    >>> carray = h5f.create_carray('/', 'carray', chunkshape=(10, 100),
                                   obj=data, filters=filters)
    >>> coords = (42, 23)
    >>> cinfo = carray.chunk_info(coords)
    >>> cinfo
    ChunkInfo(start=(40, 0), filter_mask=0, offset=6807, size=615)

So the item at coordinates (42, 23) is stored in a chunk of 615 bytes (compressed) which starts at coordinates (40, 0) in the array and byte 6807 in the file.  The latter offset may be used to let other code access the chunk directly on storage.  For instance, since Blosc2 was the only filter used to process the chunk, let's open it directly::

    >>> import blosc2
    >>> h5f.flush()
    >>> b2chunk = blosc2.open(h5f.filename, mode='r', offset=cinfo.offset)
    >>> b2chunk.shape, b2chunk.dtype, data.itemsize
    ((10, 100), dtype('V8'), 8)

Since Blosc2 does understand the structure of data (thanks to `b2nd <https://www.blosc.org/posts/blosc2-ndim-intro/>`_), we can even see that the chunk shape and the data item size are correct.  The data type is opaque to the HDF5 filter which wrote the chunk, hence the `V8` dtype.  Let's check that the item at (42, 23) is indeed in that chunk::

    >>> chunk = numpy.ndarray(b2chunk.shape, buffer=b2chunk[:],
                              dtype=data.dtype)  # Use the right type.
    >>> ccoords = tuple(numpy.subtract(coords, cinfo.start))
    >>> bool(data[coords] == chunk[ccoords])
    True

This offset-based access is actually what b2nd optimized slicing performs internally.  Please note that neither PyTables nor HDF5 were involved at all in the actual reading of the chunk (Blosc2 just got a file name and an offset).  It's difficult to cut more overhead than that!

It won't always be the case that you can (or want to) read a chunk in that way.  The `read_chunk()` method allows you to read a raw chunk as a new byte string or into an existing buffer, given the chunk's start coordinates (which you may compute yourself or get via `chunk_info()`).  Let's use `read_chunk()` to redo the reading that we just did above::

    >>> rchunk = carray.read_chunk(coords)
    Traceback (most recent call last):
        ...
    tables.exceptions.NotChunkAlignedError: Coordinates are not multiples
        of chunk shape: (42, 23) !* (np.int64(10), np.int64(100))
    >>> rchunk = carray.read_chunk(cinfo.start)  # Always use chunk start!
    >>> b2chunk = blosc2.ndarray_from_cframe(rchunk)
    >>> chunk = numpy.ndarray(b2chunk.shape, buffer=b2chunk[:],
                              dtype=data.dtype)  # Use the right type.
    >>> bool(data[coords] == chunk[ccoords])
    True

TODO
