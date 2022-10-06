.. title: New features in Python-Blosc2
.. author: Marta Iborra, Francesc Alted
.. slug: python-blosc2-improvements
.. date: 2022-10-06 10:32:20 UTC
.. tags: blosc2 features performance
.. category:
.. link:
.. description:
.. type: text


The Blosc Development Team is happy to announce that the latest version of `Python-Blosc2 0.4 <https://github.com/Blosc/python-blosc2>`_ comes with new and exciting features.  Among them, there is a handier way of setting, expanding or getting the data of a super-chunk (`SChunk`) instance.  Contrarily to chunks, a super-chunk can update its data, and it does not have the 2 GB storage limitation.

Additionally, you can now convert a `SChunk` to a contiguous, serialized buffer (aka `CFrame <https://github.com/Blosc/c-blosc2/blob/main/README_CFRAME_FORMAT.rst>`_) and vice-versa; as a bonus, this serialization process also works with a NumPy array at a blazing speed.

Let's visit the new features a bit more in depth.

Retrieve data with `__getitem__` and `get_slice`
------------------------------------------------

The general way to store data in Python-Blosc2 is through a `SChunk` (super-chunk) object. Here the data is split into chunks of the same size. So until now, the only way of working with it was chunk by chunk (see `the basics tutorial <https://github.com/Blosc/python-blosc2/blob/main/examples/tutorial-basics.ipynb>`_).

With the new version, you can get general data slices with the handy `__getitem__()` method without having to mess with chunks manually.  The only inconvenience is that it returns a bytes object, which is difficult to read by humans; to overcome this, we have also implemented the `get_slice()` method. It comes with three optional params: `start`, `stop` and `out`. You can pass to `out` any Python object supporting the `Buffer Protocol <http://jakevdp.github.io/blog/2014/05/05/introduction-to-the-python-buffer-protocol/>`_ and it will be filled with the data slice.  One common example is to pass a NumPy array in the `out` argument::

    out_slice = numpy.empty(chunksize * nchunks, dtype=numpy.int32)
    schunk.get_slice(out=out_slice)

We have now the `out_slice` NumPy array filled with the `schunk` data.  Easy and effective.

Set data with `__setitem__`
---------------------------

Similarly, if we would like to set data, we had different ways of doing it, e.g. with the `update_chunk()` or the `update_data()` methods. But those work, again, chunk by chunk, which was a bummer. That's why we also implemented the convenient `__setitem__()` method.  In a similar way to the `get_slice()` method, the value to be set can be any Python object supporting the Buffer Protocol. In addition, this method is very flexible because it not only can set the data of an already existing slice of the SChunk, but it also can expand (and update at the same time) it.

To do so, the `stop` param will set the new number of items in SChunk::

    start = schunk_nelems - 123
    stop = start + new_value.size   # new number of items
    schunk[start:stop] = new_value

In the code above, the data between `start` and the SChunk size will be updated and then, the data between the previous SChunk `size` and the new `stop` will be appended automatically for you.  This is very handy indeed (note that the `step` parameter is not yet supported though).

Serialize SChunk from/to a contiguous compressed buffer
-------------------------------------------------------

Super-chunks can be serialized in two slightly different format frames: contiguous and sparse.  A contiguous frame (aka `cframe <https://github.com/Blosc/c-blosc2/blob/main/README_CFRAME_FORMAT.rst>`_) serializes the super-chunk into a sequential buffer, whereas the sparse frame (aka `sframe <https://github.com/Blosc/c-blosc2/blob/main/README_SFRAME_FORMAT.rst>`_) uses a contiguous frame for metadata (including indexes) and the data is stored in so-called `chunks <https://github.com/Blosc/c-blosc2/blob/main/README_CHUNK_FORMAT.rst>`_ which are stored separately. Here it is how the look like:

.. image:: /images/python-blosc2-improvements/frame-blosc2.png
  :width: 50%
  :align: center
  :alt: Compression ratio for different codecs

The contiguous and sparse formats come with its own pros and cons.  A contiguous frame is ideal for transmitting / storing data as a whole buffer / file, while the sparse one is better to be used as a store while a super-chunk is being built.

In this new version of Python-Blosc2, we have added a method to convert from a SChunk to a contiguous, serialized buffer::

    buf = schunk.to_cframe()

as well as a function to convert from that buffer back to the SChunk::

    schunk = schunk_from_cframe(buf)

This allows for a nice way to serialize / deserialize super-chunks for transmission / storage purposes.


Serialize NumPy arrays
----------------------

Last but not least, you can also serialize NumPy arrays with the new pair of functions `pack_array2() <https://www.blosc.org/python-blosc2/reference/autofiles/top_level/blosc2.pack_array2.html>`_ / `unpack_array2() <https://www.blosc.org/python-blosc2/reference/autofiles/top_level/blosc2.unpack_array2.html>`_. Although you could already do this with the existing `pack_array() <https://www.blosc.org/python-blosc2/reference/autofiles/top_level/blosc2.pack_array.html>`_ / `unpack_array() <https://www.blosc.org/python-blosc2/reference/autofiles/top_level/blosc2.unpack_array.html>`_ functions, the new ones are much faster and do not have the 2 GB size limitation.
To prove this, let's see its performance by looking at some benchmark results obtained with an Intel box (i9-10940X CPU @ 3.30GHz, 14 cores) running Ubuntu 22.04.

In this benchmark we are comparing a plain NumPy array copy against compression/decompression through different compressors and functions (`compress() / decompress()`, `pack_array() / unpack_array()` and `pack_array2() / unpack_array2()`). The data distribution for the plots below is for 3 different data distributions: `arange, linspace and random <https://github.com/Blosc/python-blosc2/blob/main/bench/pack_compress.py>`_:

.. image:: /images/python-blosc2-improvements/cratios.png
  :width: 50%
  :align: center
  :alt: Compression ratio for different codecs

As can be seen, different codecs offer different compression ratios for the different distributions.  Note in particular how linear distributions (arange for int64 and linspace for float64) can reach really high compression ratios (very low entropy).

Let's see the speed for compression / decompression; in order to not show too many info in this blog, we will show just the plots for the linspace linear distribution:

.. image:: /images/python-blosc2-improvements/linspace-compress.png
  :width: 45%
  :alt: Compression speed for different codecs

.. image:: /images/python-blosc2-improvements/linspace-decompress.png
  :width: 45%
  :alt: Decompression speed for different codecs

Here we can see that the pair `pack_array2() / unpack_array2()` is consistently (much) faster than their previous version `pack_array() / unpack_array()`. Despite that, the fastest is the `compress() / decompress()` pair; however this is not serializing all the properties of a NumPy array, and has the limitation of not being able to compress data larger than 2 GB.

You can test the speed in your box by running the `pack_compress bench <https://github.com/Blosc/python-blosc2/blob/main/bench/pack_compress.py>`_.

Also, if you would like to store the contiguous buffer on-disk, you can directly use the pair of functions `save_array() <https://www.blosc.org/python-blosc2/reference/autofiles/top_level/blosc2.save_array.html#blosc2.save_array>`_, `load_array() <https://www.blosc.org/python-blosc2/reference/autofiles/top_level/blosc2.save_array.html#blosc2.load_array>`_.

Native performance on Apple M1 processors
-----------------------------------------

Contrariliy to Blosc1, Blosc2 comes with native support for ARM processors (it leverages the NEON SIMD instruction set there), and that means that it runs very fast in this architecture.  As an example, let's see how the new `pack_array2() / unpack_array2()` works in an Apple M1 laptop (Macbook Air).

.. image:: /images/python-blosc2-improvements/M1-i386-vs-arm64-pack.png
  :width: 45%
  :alt: Compression speed for different codecs

.. image:: /images/python-blosc2-improvements/M1-i386-vs-arm64-unpack.png
  :width: 45%
  :alt: Decompression speed for different codecs

As can be seen, running Blosc2 in native arm64 mode on M1 offers quite a bit more performance (specially during compression) than using the i386 emulation.  If speed is important to you, and you have a M1/M2 processor, make sure that you are running Blosc2 in native mode (arm64).

Conclusions
-----------

The new features added to python-blosc2 offer an easy way of creating, getting, setting and expanding data in a SChunk. Furthermore, you can get a contiguous compressed representation (aka `CFrame <https://github.com/Blosc/c-blosc2/blob/main/README_CFRAME_FORMAT.rst>`_) of it and re-create it again latter. And you can do the same with NumPy arrays (either in-memory or on-disk) faster than with the former functions, and even faster than a plain `memcpy()`.

For more info on how to use these useful new features, see the `tutorial <https://github.com/Blosc/python-blosc2/blob/main/examples/slicing_and_beyond.ipynb>`_.

Finally, see the complete documentation at: https://www.blosc.org/python-blosc2/python-blosc2.html.  Thanks to Marc Garcia (`@datapythonista`) for his fine work and enthusiasm in helping us providing a better structure to the Blosc documentation!

This work has been made thanks to a Small Development Grant from `NumFOCUS <https://numfocus.org>`_.
NumFOCUS is a non-profit organization supporting open code for better science.  If you like the goal, consider giving a donation to them (you can optionally make it to go to our project too :-).
