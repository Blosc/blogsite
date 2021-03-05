.. title: Announcing Blosc Wheels
.. author: Oscar Guiñón
.. slug: new-blosc-wheels
.. date: 2021-01-18 12:32:20 UTC
.. tags: wheels
.. category:
.. link:
.. description:
.. type: text


We are happy to announce that wheels for Intel (32 and 64 bits) and all major OS (Win, Linux, Mac) are being produced on regular basis for python-blosc.  Such wheels also contain development files for the C-Blosc library.  If you are interested in knowing more how to use them, keep reading.

A Python wheel (.whl file) is a ZIP archive used to make easier the installation process of packages.  The new wheels make Blosc library installation faster by avoiding compiling, and they are now available at PyPI. See: https://pypi.org/project/blosc/.

Moreover, wheels for Blosc have support for AVX2 *runtime* detection, so it will be automatically leveraged in case the local host has AVX2. On the other hand, if the host does not have AVX2, SSE2 is used instead, which, even if it is slower than AVX2, it is still faster than regular x86 instructions.


Small intro to wheels
---------------------

Wheels are an advantageous alternative to distribute Python (but also pure C) packages which contain C (or Cython) source code, and hence, need a compiler.  For those that are not familiar to wheels, here it comes a small tutorial on how to create and use wheels.

First, let's recall the traditional way to build a source distribution:

.. code-block:: console

    $ python setup.py sdist

To build a wheel, the process is quite similar:

.. code-block:: console

    $ python setup.py bdist_wheel

To install a package via pip (pip decides whether install a from wheel or compile from the source package; wheels have obviously more priority):

.. code-block:: console

    $ python -m pip install {package}

To install a package forcing to use source distribution:

.. code-block:: console

    $ python -m pip install --no-binary {package}

To install a package forcing to use wheels:

.. code-block:: console

    $ python -m pip install --only-binary {package}


Different types of wheels
-------------------------

There are different kind of wheels, depending on the goals and the build process:

- Universal Wheels are wheels that are pure Python (i.e. contain no compiled extensions) and support Python 2 and 3.

- Pure Python Wheels that are not “universal” are wheels that are pure Python (i.e. contain no compiled extensions), but don’t natively support both Python 2 and 3.

- Platform Wheels are wheels that are specific to a certain platform like Linux, macOS, or Windows, usually due to containing compiled extensions.

Platform wheels are built in one Linux variant and have no guarantee of working on another Linux variant.  However, the manylinux wheels are accepted by most Linux variants:

- manylinux1: based on Centos5.
- manylinux2010: based on Centos6.
- manylinux2014: based on Centos7.

Specifically, Blosc wheels are platform wheels that support Python3 (3.7 and up) on Windows, Linux and Mac, for both 32 and 64 bits systems.


Binaries for C-Blosc libraries are included
-------------------------------------------

Although wheels were meant for Python packages, nothing prevents adding more stuff to them.  In particular, we are not only distributing python-blosc binary extensions in our wheels, but also binaries for the C-Blosc library.  This way, people willing to use the C-Blosc library can make use of these wheels to install the necessary development files.

First, install the binary wheel via PyPI without the need to manually compile the thing:

.. code-block:: console

    $ pip install --only-binary blosc

Now, let's suppose that we want to compile the `c-blosc/examples/many_compressors.c` on Linux:

First, you have to look where the wheels directory is located.  In our case:

.. code-block:: console

    $ WHEEL_DIR=/home/soscar/miniconda3
    $ export LD_LIBRARY_PATH=$WHEEL_DIR/lib   # note that you need the LD_LIBRARY_PATH env variable

For the actual compilation, you need to pass the directory for the include and lib directories:

.. code-block:: console

    $ gcc many_compressors.c -I$WHEEL_DIR/include -o many_compressors -L$WHEEL_DIR/lib -lblosc

Finally, run the resulting binary and hopefully you will see something like:

.. code-block:: console

    $ ./many_compressors
    Blosc version info: 1.20.1 ($Date:: 2020-09-08 #$)
    Using 4 threads (previously using 1)
    Using blosclz compressor
    Compression: 4000000 -> 37816 (105.8x)
    Succesful roundtrip!
    Using lz4 compressor
    Compression: 4000000 -> 37938 (105.4x)
    Succesful roundtrip!
    Using lz4hc compressor
    Compression: 4000000 -> 27165 (147.2x)
    Succesful roundtrip!


For more details, including compiling with binary wheels on other platforms than Linux, see: https://github.com/Blosc/c-blosc/blob/master/COMPILING_WITH_WHEELS.rst.


Final remarks
-------------

Producing Python wheels for a project can be somewhat involved for regular users. However, the advantages of binary wheels really make them worth the effort, since they make the installation process easier and faster for users.  This is why we are so happy to finally provide wheels that can benefit, not only python-blosc users, but users of the C-Blosc library as well.

Last but not least, a big thank you to the Zarr team, specially to Jeff Hammerbacher, who provided a grant to the Blosc team for making the wheels support official.  Hopefully this new development will make life easier for Zarr developers and users (by the way, we are really glad to see Zarr quickly spreading as a data container for big multidimensional data, and Blosc helping on the compression part).
