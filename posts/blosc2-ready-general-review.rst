.. title: C-Blosc2 Ready for General Review
.. author: Francesc Alted
.. slug: blosc2-ready-general-review
.. date: 2021-05-06 10:32:20 UTC
.. tags: blosc2 release candidate
.. category: posts
.. link:
.. description:
.. type: text


On behalf of the Blosc team, we are happy to announce the `first C-Blosc2
release (Release Candidate 1) <https://github.com/Blosc/c-blosc2/releases/tag/v2.0.0.rc1>`_
that is meant to be reviewed by users.  As of now
we are declaring both the API and the format frozen, and we are seeking for
feedback from the community so as to better check the library and declare it
apt for its use in production.

Some history
------------

The next generation Blosc (aka Blosc2) started back in 2015 as a way
to overcome some limitations of the Blosc compressor, mainly the limitation
of 2 GB for the size of data to be compressed.  But it turned out that I wanted
to make thinks a bit more complete, and provide a native serialization too.
During that process Google awarded my contributions to Blosc with the
`Open Source Peer Bonus Program <https://www.blosc.org/posts/prize-push-Blosc2/>`_ in 2017.
This award represented a big emotional push for me in
persisting in the efforts towards producing a stable release.

Back in 2018, Zeeman Wang from Huawei invited me to go to their central headquarters in Shenzhen to meet
a series of developers that were trying to use compression in a series of scenarios.
During two weeks we had a series of productive meetings, and I got aware of the many
possibilities that compression is opening in industry: since making phones with
limited hardware to work faster to accelerate computations on high-end computers.
That was also a great opportunity for me to better know a millennial culture; I was
genuinely interested to see how people live, eat and socialize in China.

In 2020, `Huawei graciously offered a grant to the Blosc project
<https://www.blosc.org/posts/blosc-donation/>`_ to complete the project.  Since then,
we have got donations from several other sources (like NumFOCUS, Python Software Foundation,
ESRF among them).  Lately `ironArray <https://ironarray.io>`_ is sponsoring
two of us (Aleix Alcacer and myself) to work partial time on Blosc related projects.

Thanks to all this support, the Blosc development team has been able to grow quite a lot (we are currently 5 people in the core team) and we
have been able to work hard at producing a series of improvements in different projects under the Blosc umbrella, in particular `C-Blosc2 <https://github.com/Blosc/c-blosc2>`_,
`Python-Blosc2 <https://github.com/Blosc/python-blosc2>`_,
`Caterva <https://github.com/Blosc/caterva>`_ and `cat4py <https://github.com/Blosc/cat4py>`_.

As you see, there is a lot of development going on around C-Blosc2 other than C-Blosc2 itself.  In this installment I am going to focus just on the main features that C-Blosc2 is bringing, but hopefully all the other projects in the ecosystem will also complement its existing functionality.  When all these projects would be ready, we hope that users will be able to use them to store big amounts of data in a way that is both efficient, easy-to-use and most importantly, adapted to their needs.

New features of C-Blosc2
------------------------

Here it is the list of the main features that we are releasing today:

* **64-bit containers:** the first-class container in C-Blosc2 is the `super-chunk` or, for brevity, `schunk`, that is made by smaller chunks which are essentially C-Blosc1 32-bit containers.  The super-chunk can be backed or not by another container which is called a `frame` (see later).

* **More filters:** besides `shuffle` and `bitshuffle` already present in C-Blosc1, C-Blosc2 already implements:

  - `delta`: the stored blocks inside a chunk are diff'ed with respect to first block in the chunk.  The idea is that, in some situations, the diff will have more zeros than the original data, leading to better compression.

  - `trunc_prec`: it zeroes the least significant bits of the mantissa of float32 and float64 types.  When combined with the `shuffle` or `bitshuffle` filter, this leads to more contiguous zeros, which are compressed better.

* **A filter pipeline:** the different filters can be pipelined so that the output of one can the input for the other.  A possible example is a `delta` followed by `shuffle`, or as described above, `trunc_prec` followed by `bitshuffle`.

* **Prefilters:** allows to apply user-defined C callbacks **prior** the filter pipeline during compression.  See `test_prefilter.c <https://github.com/Blosc/c-blosc2/blob/master/tests/test_prefilter.c>`_ for an example of use.

* **Postfilters:** allows to apply user-defined C callbacks **after** the filter pipeline during decompression. The combination of prefilters and postfilters could be interesting for supporting e.g. encryption (via prefilters) and decryption (via postfilters).  Also, a postfilter alone can used to produce on-the-flight computation based on existing data (or other metadata, like e.g. coordinates). See `test_postfilter.c <https://github.com/Blosc/c-blosc2/blob/master/tests/test_postfilter.c>`_ for an example of use.

* **SIMD support for ARM (NEON):** this allows for faster operation on ARM architectures.  Only `shuffle` is supported right now, but the idea is to implement `bitshuffle` for NEON too.  Thanks to Lucian Marc.

* **SIMD support for PowerPC (ALTIVEC):** this allows for faster operation on PowerPC architectures.  Both `shuffle`  and `bitshuffle` are supported; however, this has been done via a transparent mapping from SSE2 into ALTIVEC emulation in GCC 8, so performance could be better (but still, it is already a nice improvement over native C code; see PR https://github.com/Blosc/c-blosc2/pull/59 for details).  Thanks to Jerome Kieffer and `ESRF <https://www.esrf.fr>`_ for sponsoring the Blosc team in helping him in this task.

* **Dictionaries:** when a block is going to be compressed, C-Blosc2 can use a previously made dictionary (stored in the header of the super-chunk) for compressing all the blocks that are part of the chunks.  This usually improves the compression ratio, as well as the decompression speed, at the expense of a (small) overhead in compression speed.  Currently, it is only supported in the `zstd` codec, but would be nice to extend it to `lz4` and `blosclz` at least.

* **Contiguous frames:** allow to store super-chunks contiguously, either on-disk or in-memory.  When a super-chunk is backed by a frame, instead of storing all the chunks sparsely in-memory, they are serialized inside the frame container.  The frame can be stored on-disk too, meaning that persistence of super-chunks is supported.

* **Sparse frames (on-disk):** each chunk in a super-chunk is stored in a separate file, as well as the metadata.  This is the counterpart of in-memory super-chunk, and allows for more efficient updates than in frames (i.e. avoiding 'holes' in monolithic files).

* **Partial chunk reads:** there is support for reading just part of chunks, so avoiding to read the whole thing and then discard the unnecessary data.

* **Parallel chunk reads:** when several blocks of a chunk are to be read, this is done in parallel by the decompressing machinery.  That means that every thread is responsible to read, post-filter and decompress a block by itself, leading to an efficient overlap of I/O and CPU usage that optimizes reads to a maximum.

* **Meta-layers:** optionally, the user can add meta-data for different uses and in different layers.  For example, one may think on providing a meta-layer for `NumPy <http://www.numpy.org>`_ so that most of the meta-data for it is stored in a meta-layer; then, one can place another meta-layer on top of the latter for adding more high-level info if desired (e.g. geo-spatial, meteorological...).

* **Variable length meta-layers:** the user may want to add variable-length meta information that can be potentially very large (up to 2 GB). The regular meta-layer described above is very quick to read, but meant to store fixed-length and relatively small meta information.  Variable length metalayers are stored in the trailer of a frame, whereas regular meta-layers are in the header.

* **Efficient support for special values:** large sequences of repeated values can be represented with an efficient, simple and fast run-length representation, without the need to use regular codecs.  With that, chunks or super-chunks with values that are the same (zeros, NaNs or any value in general) can be built in constant time, regardless of the size.  This can be useful in situations where a lot of zeros (or NaNs) need to be stored (e.g. sparse matrices).

* **Nice markup for documentation:** we are currently using a combination of Sphinx + Doxygen + Breathe for documenting the C-API.  See https://c-blosc2.readthedocs.io.  Thanks to Alberto Sabater and Aleix Alcacer for contributing the support for this.

* **Plugin capabilities for filters and codecs:** we have a plugin register capability inplace so that the info about the new filters and codecs can be persisted and transmitted to different machines.  Thanks to the NumFOCUS foundation for providing a grant for doing this.

* **Pluggable tuning capabilities:** this will allow users with different needs to define an interface so as to better tune different parameters like the codec, the compression level, the filters to use, the blocksize or the shuffle size.  Thanks to ironArray for sponsoring us in doing this.

* **Support for I/O plugins:** so that users can extend the I/O capabilities beyond the current filesystem support.  Things like use databases or S3 interfaces should be possible by implementing these interfaces.  Thanks to ironArray for sponsoring us in doing this.

* **Python wrapper:**  we have a preliminary wrapper in the works.  You can have a look at our ongoing efforts in the `python-blosc2 repo <https://github.com/Blosc/python-blosc2>`_.  Thanks to the Python Software Foundation for providing a grant for doing this.

* **Security:** we are actively using using the `OSS-Fuzz <https://github.com/google/oss-fuzz>`_ and `ClusterFuzz <https://oss-fuzz.com>`_ for uncovering programming errors in C-Blosc2.  Thanks to Google for sponsoring us in doing this.

As you see, the list is long and hopefully you will find compelling enough features for your own needs.  Blosc2 is not only about speed, but also about
providing

Tasks to be done
----------------

Even if the list of features above is long, we still have things to do in Blosc2; and the plan is to continue the development, although always respecting the existing API and format.  Here are some of the things in our TODO list:

* **Centralized plugin repository:** we have got a grant from NumFOCUS for implementing a centralized repository so that people can send their plugins (using the existing machinery) to the Blosc2 team.  If the plugins fulfill a series of requirements, they will be officially accepted, and distributed withing the library.

* **Improve the safety of the library:**  although this is always a work in progress, we did a long way in improving our safety, mainly thanks to the efforts of Nathan Moinvaziri.

* **Support for lossy compression codecs:** although we already support the `trunc_prec` filter, this is only valid for floating point data; we should come with lossy codecs that are meant for any data type.

* **Checksums:** the frame can benefit from having a checksum per every chunk/index/metalayer.  This will provide more safety towards frames that are damaged for whatever reason.  Also, this would provide better feedback when trying to determine the parts of the frame that are corrupted.  Candidates for checksums can be the xxhash32 or xxhash64, depending on the goals (to be decided).

* **Documentation:** utterly important for attracting new users and making the life easier for existing ones.  Important points to have in mind here:

  - **Quality of API docstrings:** is the mission of the functions or data structures clearly and succinctly explained? Are all the parameters explained?  Is the return value explained?  What are the possible errors that can be returned?.

  - **Tutorials/book:** besides the API docstrings, more documentation materials should be provided, like tutorials or a book about Blosc (or at least, the beginnings of it).  Due to its adoption in GitHub and Jupyter notebooks, one of the most extended and useful markup systems is Markdown, so this should also be the first candidate to use here.

* **Lock support for super-chunks:** when different processes are accessing concurrently to super-chunks, make them to sync properly by using locks, either on-disk (frame-backed super-chunks), or in-memory. Such a lock support would be configured in build time, so it could be disabled with a cmake flag.

It would be nice that, in case some of this feature (or a new one) sounds useful for you, you can help us in providing either code or sponsorship.

Summary
-------

Since 2015, it has been a long time to get C-Blosc2 so much featured and tested.
But hopefully the journey will continue because as `Kavafis said <https://www.poetryfoundation.org/poems/51296/ithaka-56d22eef917ec>`_::

  As you set out for Ithaka
  hope your road is a long one,
  full of adventure, full of discovery.

Let me thank again all the people and sponsors that we have had during the life of the Blosc project; without them we would not be where we are now.  We do hope that C-Blosc2 will have a long life and we as a team will put our soul in making that trip to last as long as possible.

Now is your turn.  We expect you to start testing the library as much as possible and report back.  With your help we can get C-Blosc2 in production stage hopefully very soon.  Thanks in advance!
