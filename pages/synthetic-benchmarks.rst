.. title: Synthetic Benchmarks
.. slug: synthetic-benchmarks
.. date: 2014-06-27 10:41:41 UTC
.. tags:
.. link:
.. description:
.. type: text

Synthetic Benchmarks (And How You Can Contribute Yours)
=======================================================

In order to assess the performance of Blosc in a variety of scenarios, a
benchmark program is provided. This should enable a fair comparison between
different hardware and software platforms.  In this section, a series of plots
about the performance of Blosc on a selected set of platforms are shown.  It is
fun to see the evolution of the hardware/software in recent years in terms of
the speed of Blosc compared to a plain OS ``memcpy()``.  These conclusions can
be applied to the evolution of the ratio of computing power versus memory
bandwidth in general.

Many users have contributed their own benchmarks and you can view
them all in the next links:

* :doc:`benchmarks-blosclz`

* :doc:`benchmarks-lz4`

* :doc:`benchmarks-lz4hc`

* :doc:`benchmarks-snappy`

* :doc:`benchmarks-zlib`

In case you want to contribute and run the benchmarks your own platform, follow
the instructions below on how to compile, run and report back the results of
the benchmark.


How to compile (or get binaries for) the benchmark suite for Blosc
------------------------------------------------------------------

First, checkout the master version from:

https://github.com/Blosc/c-blosc

Then, compile the sources:

*GCC/Clang (Unix) or MINGW/Clang (Windows)*

.. code-block:: console

  $ cd your_blosc_sources
  $ mkdir build
  $ cd build
  $ cmake ..
  $ make  # the benchmark will appear in `your_blosc_sources`/build/bench
  $ cp bench/bench ../bench
  $ cd ../bench


Running and plotting the different suites in benchmark
------------------------------------------------------

Now that you have the executable benchmark, you can run it by passing
the ``suite`` parameter followed by the number of cores in your machine
to the ``bench`` program, i.e. something like:

.. code-block:: console

  $ ./bench $CODEC suite [nthreads]  # $CODEC can be any of blosclz, lz4, lz4hc, snappy, zlib

then a small suite will be run that checks the speed of Blosc for the
specified number of threads.  Given this output, you can convert it
into a plot by using the ``bench/plot-speeds.py`` scripts (you will need
the [http://matplotlib.sourceforge.net/ matplotlib] library
installed).  You can print a small online help for this script usage:

.. code-block:: console

  $ python plot-speeds.py -h
  Usage: plot-speeds.py [-r] [-o outfile] [-t title ] [-d|-c] filename

  Options:
    -h, --help            show this help message and exit
    -o OUTFILE, --outfile=OUTFILE
                          filename for output (many extensions supported, e.g.
                          .png, .jpg, .pdf)
    -t TITLE, --title=TITLE
                          title of the plot
    -l LIMIT, --limit=LIMIT
                          expression to limit number of threads shown
    -x XMAX, --xmax=XMAX  limit the x-axis
    -r, --report          generate file for reporting
    -d, --decompress      plot decompression data
    -c, --compress        plot compression data

For example, if you have, say, 4 cores in your machine, and want to
get the plots interactively, proceed like this:

.. code-block:: console

  $ ./bench blosclz suite 4 > blosclz.txt
  $ python plot-speeds.py -c blosclz.txt   # get the compression plot
  $ python plot-speeds.py -d blosclz.txt   # get the decompression one

Alternatively, you can directly get a plot file by using the ``-o``
flag:

.. code-block:: console

  $ python plot-speeds.py -o plot.png -c mysuite-blosclz.txt

Or, you can get a nice plot apt for reporting and publication on this site
with:

.. code-block:: console

  $ python plot-speeds.py -r -c blosclz.txt  # gives blosclz-compr.png
  $ python plot-speeds.py -r -d blosclz.txt  # gives blosclz-decompr.png

Sometimes the legend may cover some of the data in this case you can
increase the limit of the x-axis (compression ratio) using the ``-x``
switch (`10` is quite a good value):

.. code-block:: console

  $ python plot-speeds.py -x 10 -c mysuite.txt

If you have many, many threads, the output can become quite confusing
and you may want to take a look at the ``-l`` switch. This can limit the
number of displayed threads using an arbitrary Python expression, like
a list or an iterator over ``ints`` (indexing starts at 1, not 0):

.. code-block:: console

  $ python plot-speeds.py -l '[1]' -c mysuite.txt
  $ python plot-speeds.py -l 'range(1, 8)' mysuite.txt
  $ python plot-speeds.py -l 'range(1, 8, 2)' mysuite.txt
  $ python plot-speeds.py -l '[1, 3, 28]' mysuite.txt


Reporting your results back
---------------------------

If you want to help with fine-tuning Blosc for other processors, please send
the output of the suite to `the mailing list
<http://groups.google.com/group/blosc>`__.  That info will be extremely useful
to help us improve Blosc so that it can achieve better compression ratios
and performance in future versions.  Please be sure that you also provide the
following information (as a minimum):

* CPU info: (vendor, model or cache sizes)
* Operating System: (e.g. Linux/Windows/MacOSX/Solaris and version)
* Compiler used: (e.g. GCC/ICC/MSVC/MINGW/Clang and version)


Testing Blosc further
---------------------

Finally, if you have spare CPU cycles available, you may want to run the
``hardsuite``, which is a series of tests that are much more comprehensive (and
costly) than the ``suite`` above.  The ``hardsuite`` will take between 1 and 6
hours to run, depending on your machine and the number of cores, and will
compress/decompress around 4 TB of data.  Running it is easy:

.. code-block:: console

  $ ./bench `compr` hardsuite 4 > myhardsuite.txt
  $ gzip -9 < myhardsuite.txt > myhardsuite.txt.gz    # use zip or 7z compressors if on Windows

**IMPORTANT**: In order to get fine results, please be sure that you
are not running other heavy process while running the suites.

You can search through the output for the ``FAILED`` string in order to see
if something went wrong.  If ``FAILED`` does not appear anywhere, you
can be pretty sure that Blosc works well for your platform.  If
failures appear, please report this to `the mailing list
<http://groups.google.com/group/blosc>`__.

**NOTE**: You cannot use ``plot-speeds.py`` to plot the results of the
``hardsuite``, as it is only meant for plotting ``suite`` output purposes.

Incidentally, we have added a new suite called ``extremesuite`` that
performs a crazy check on many, many possible inputs to Blosc.  It
works similarly than the ``hardsuite``, but it can take between 2 and 3
days to finish on a relatively recent CPU, and can account up to 60 TB
of data compressed, decompressed and round-trip checked.  Really, this
is not for everyone but in case you are brave enough, you might want
to have it a try.
