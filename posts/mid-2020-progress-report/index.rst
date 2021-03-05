.. title: Mid 2020 Progress Report
.. author: Francesc Alted
.. slug: mid-2020-progress-report
.. date: 2020-08-27 12:32:20 UTC
.. tags: blosc progress report grants
.. category:
.. link:
.. description:
.. type: text

Mid 2020 Report for Status of Work on Blosc projects
====================================================

2020 has been a year where the Blosc projects have received important donations, totalling an amount of $55,000 USD so far.  In the present report we list the most important tasks that have been carried out during the period that goes from January 2020 to August 2020.  Most of these tasks are related to the most fast-paced projects under development: C-Blosc2 and Caterva (including its cat4py wrapper).  Having said that, the Blosc development team has been active in other projects too (C-Blosc, python-blosc), although mainly for maintenance purposes.

Besides, we also list the roadmap for the C-Blosc2, Caterva and cat4py projects that we plan to tackle during the next few months.


C-Blosc2
--------

C-Blosc2 adds new data containers, called superchunks, that are essentially a set of compressed chunks in memory that can be accessed randomly and enlarged during its lifetime.  Also, a new frame serialization layer has been added, so that superchunks can be persisted on disk, while keeping the same properties of superchunks in memory.  Finally, a metalayer capability allow for higher level containers to be created on top of superchunks/frames.

Highligths
~~~~~~~~~~

* Maskout functionality.  This allows for selectively choose the blocks of a chunk that are going to be decompressed.  This paves the road for faster multidimensional slicing in Caterva (see below in the Caterva section).

* Prefilters introduced and declared stable.  Prefilters allow for the user to pass C functions for performing arbitrary computations on a chunk prior to the filter/codec pipeline.  In addition, the C function can even have access to more chunks than just the one that is being compressed.  This opens the door to a way to operate with different super-chunks and produce a new one very efficiently. See https://github.com/Blosc/c-blosc2/blob/master/tests/test_prefilter.c for some examples of use.

* Support for PowerPC/Altivec.  We added support for PowerPC SIMD (Altivec/VSX) instructions for faster operation of shuffle and bitshuffle filters.  For details, see https://github.com/Blosc/c-blosc2/pull/98.

* Improvements in compression ratio for LZ4/BloscLZ.  New processors are continually increasing the amount of memory in their caches.  In recent C-Blosc and C-Blosc2 releases we increased the size of the internal blocks so that LZ4/BloscLZ codecs have better opportunities for finding duplicates and hence, increasing their compression ratios.  But due to the increased cache sizes, performance has kept close to the original, fast speeds.  For some benchmarks, see https://blosc.org/posts/beast-release/.

* New entropy probing method for BloscLZ.  BloscLZ is a native codec for Blosc whose mission is to be able to compress synthetic data efficiently.  Synthetic data can appear in multiple situations and having a codec that is meant to compress/decompress that with high compression ratios in a fast manner is important.  The new entropy probing method included in recent BloscLZ 2.3 (introduced in both C-Blosc and C-Blosc2) allows for even better compression ratios for highly compressible data, while giving up early when blocks are going to be difficult to compress at all.  For details see: https://blosc.org/posts/beast-release/ too.

Roadmap for C-Blosc2
~~~~~~~~~~~~~~~~~~~~

During the next few months, we plan to tackle the next tasks:

* Postfilters.  The same way that prefilters allows to do user-defined computations prior to the compression pipeline, the postfilter would allow to do the same *after* the decompression pipeline.  This could be useful in e.g. creating superchunks out of functions taking simple data as input (for example, a [min, max] range of values).

* Finalize the frame implementation.  Although the frame specification is almost complete (bar small modifications/additions), we still miss some features that are included in the specification, but not implemented yet.  An example of this is the fingerprint support at the end of the frames.

* Chunk insertion.  Right now only chunk appends are supported.  It should be possible to support chunk insertion in any position, and not only at the end of a superchunk.

* Security.  Although we already started actions to improve the safety of the package using tools like OSS-Fuzz, this is an always work in progress task, and we plan indeed continuing improving it in the future.

* Wheels.  We would like to deliver wheels on every release soon.


Caterva/cat4py
--------------

Caterva is a multidimensional container on top of C-Blosc2 containers.  It uses the metalayer capabilities present in superchunks/frames in order to store the multidimensionality information necessary to define arrays up to 8 dimensions and up to 2^63 elements.  Besides being able to create such arrays, Caterva provides functionality to get (multidimensional) slices of the arrays easyly and efficiently.  cat4py is the Python wrapper for Caterva.

Highligths
~~~~~~~~~~

* Multidimensional blocks.  Chunks inside superchunk containers are endowed with a multidimensional structure so as to enable efficient slicing.  However, in many cases there is a tension between defining large chunks so as to reduce the amount of indexing to find chunks or smaller ones in order to avoid reading data that falls outside of a slice.  In order to reduce such a tension, we endowed the blocks inside chunks with a multidimensional structure too, so that the user has two parameters (chunkshape and blockshape) to play with in order to optimize I/O for their use case.  For an example of the kind of performance enhancements you can expect, see https://htmlpreview.github.io/?https://github.com/Blosc/cat4py/blob/269270695d7f6e27e6796541709e98e2f67434fd/notebooks/slicing-performance.html.

* API refactoring.  Caterva is a relatively young project, and its API grew up organically and hence, in a quite disorganized manner.  We recognized that and proceeded with a big API refactoring, trying to put more sense in the naming schema of the functions, as well as in providing a minimal set of C structs that allows for a simpler and better API.

* Improved documentation.  A nice API is useless if it is not well documented, so we decided to put a significant amount of effort in creating high-quality documentation and examples so that the user can quickly figure out how to create and access Caterva containers with their own data.  Although this is still a work in progress, we are pretty happy with how docs are shaping up.  See https://caterva.readthedocs.io/ and https://cat4py.readthedocs.io/.

* Better Python integration (cat4py).  Python, specially thanks to the NumPy project, is a major player in handling multidimensional datasets, so have greatly bettered the integration of cat4py, our Python wrapper for Caterva, with NumPy.  In particular, we implemented support for the NumPy array protocol in cat4py containers, as well as an improved NumPy-esque API in cat4py package.

Roadmap for Caterva / cat4py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During the next months, we plan to tackle the next tasks:

* Append chunks in any order. This will make it easier for the user to create arrays, since they will not be forced to use a row-wise order.

* Update array elements. With this, users will be able to update their arrays without having to make a copy.

* Resize array dimensions. This feature will allow Caterva to increase or decrease in size any dimension of the arrays.

* Wheels.  Once Caterva/cat4py would be in beta stage, we plan to deliver wheels on every release.


Final thoughts
--------------

We are very grateful to our sponsors in 2020; they allowed us to implement what we think would be nice features for the whole Blosc ecosystem.  However, and although we did a lot of progress towards making C-Blosc2 and Caterva as featured and stable as possible, we still need to finalize our efforts so as to see both projects stable enough to allow them to be used in production.  Our expectation is to release a 2.0.0 (final) release for C-Blosc2 by the end of the year, whereas Caterva (and cat4py) should be declared stable during 2021.

Also, we are happy to have enrolled new members on Blosc crew: Óscar Griñón, who proved to be instrumental in implementing the multidimensional blocks in Caterva and Nathan Moinvaziri, who is making great strides in making C-Blosc and C-Blosc2 more secure.  Thanks guys!

Hopefully 2021 will also be a good year for seeing the Blosc ecosystem to evolve.  If you are interested on what we are building and want to help, we are open to any kind of contribution, including `donations <https://blosc.org/pages/donate/>`_.  Thank you for your interest!
