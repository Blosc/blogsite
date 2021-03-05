.. title: Compress Me, Stupid!
.. author: Francesc Alted
.. slug: compress-me-stupid
.. date: 2014-08-28 17:01:20 UTC
.. tags: blosc,blosclz,history,pytables,hdf5
.. link: 
.. description: 
.. type: text


How it all started
------------------

I think I began to become truly interested in compression when, back
in 1992, I was installing `C-News
<http://en.wikipedia.org/wiki/C_News>`_, a news server package meant
to handle `Usenet News <http://en.wikipedia.org/wiki/Usenet>`_
articles in `our university <http://www.uji.es>`_.  For younger
audiences, Usenet News was a very popular way to discuss about all
kind of topics, but at the same time it was pretty difficult to cope
with the huge amount of articles, specially because spam practices
started to appear by that time.  As Gene Spafford put it in 1992:

  "Usenet is like a herd of performing elephants with
  diarrhea. Massive, difficult to redirect, awe-inspiring,
  entertaining, and a source of mind-boggling amounts of excrement
  when you least expect it."

But one thing was clear: Usenet brought **massive** amounts of data
that had to be transmitted through the typical low-bandwidth data
lines of that time: 64 Kbps shared for everyone at our university.

My mission then was to bring the Usenet News feed by making use of as
low of resources as possible.  Of course, one of the first things that
I did was to start news transmission during the night, when everyone
was warm at bed and nobody was going to complain about others stealing
the precious and scarce Internet bandwidth.  Another measure was to
subscribe to just a selection of groups so that the transmission would
end before the new day would start.  And of course, I started
experimenting with compression for maximizing the number of groups
that we could bring to our community.

Compressing Usenet News
-----------------------

The most used compressor by 1992 was `compress
<http://en.wikipedia.org/wiki/Compress>`_, a Unix program based on the
`LZW <http://en.wikipedia.org/wiki/LZW>`_ compression algorithm.  But
LZW had patents issues, so by that time Jean-Loup Gailly and Mark
Adler started the work with `gzip
<http://en.wikipedia.org/wiki/Gzip>`_.  At the beginning of 1993 gzip
1.0 was ready for consumption and I find it exciting not only because
it was not patent-encumbered, but also because it compressed way
better than the previous ``compress`` program, allowed different
compression levels, and it was pretty fast too (although ``compress``
still had an advantage here, IIRC).

So I talked with `the university <http://www.uv.es>`_ that was
providing us with the News feed and we manage to start compressing it,
first with ``compress`` and then with ``gzip``.  Shortly after that,
while making measurements on the new gzip improvements, I discovered
that the bottleneck was in our News workstation (an HP 9000-730 with a
speedy `PA-7000 RISC microprocessor
<http://en.wikipedia.org/wiki/PA-RISC>`_ @ 66 MHz) being unable to
decompress all the gzipped stream of subscribed news on-time.  The
bottleneck suddenly changed from the communication line to the CPU!

I remember spending large hours playing with different combinations of
data chunk sizes and gzip compression levels, plotting the results
(with the fine `gnuplot <http://en.wikipedia.org/wiki/Gnuplot>`_)
before finally coming with a combination that stroked a fair balance
between available bandwidth and CPU speed, maximizing the amount of
news articles hitting our university.  I think this was my first
realization of how compression could help bringing data faster to the
system, making some processes more effective.  In fact, that actually
blew-up my mind and made me passionate about compression technologies
for the years to come.

LZO and the explosion of compression technology
-----------------------------------------------

During 1996, Markus F.X.J. Oberhumer started to announce the
availability of his own set of LZO compressors.  These consisted in
many different compressors, all of them being variations of his own
compression algorithm (LZO), but tweaked to achieve either better
compression ratios or compression speed.  The suite was claimed to
being able to achieve speeds reaching **1/3 of the memory speed** of
the typical Pentium-class computers available at that time.  An entire
set of compressors being able to approach memory speed? boy, that was
a very exciting news for me.

LZO was in the back of my mind when I started my work on `PyTables
<http://www.pytables.org>`_ in August 2002 and shortly after, in `May
2003 <http://pytables.org/svn/pytables/tags/std-0.5/README.txt>`_,
PyTables gained support for LZO.  My goal was indeed to accelerate
data transmission from disk to the CPU (and back), and `these plots
<http://pytables.github.io/usersguide/optimization.html#understanding-chunking>`_
are testimonial of how beneficial LZO was for achieving that goal.
Again, compression was demonstrating that it could effectively
increase disk bandwidth, and not only slow internet lines.

However, although LZO was free of patent issues and fast as hell,
it had a big limitation for a project like PyTables: the licensing.
LZO was using the GPL license, and that prevented the inclusion of its
sources in distributions without re-licensing PyTables itself as GPL,
a thing that I was not willing to do (PyTables has a BSD license, as
it is usual in the NumPy ecosystem).  Because of that, LZO was a nice
compressor to be included in GPL projects like the Linux kernel
itself, but not a good fit for PyTables (although support for LZO still
exists, as long as it is downloaded and installed separately).

By that time (mid 2000's) it started to appear a plethora of fast
compressors with the same spirit than LZO, but with more permissive
licenses (typically BSD/MIT), many of them being a nice fit for PyTables.

A new compressor for PyTables/HDF5
----------------------------------

By 2008 it was clear that PyTables needed a compressor whose sources
could be included in the PyTables tarball, so minimizing the
installation requirements.  For this I started considering a series of
libraries and immediately devised `FastLZ <http://fastlz.org/>`_ as a
nice candidate because of its simplicity and performance.  Also,
FastLZ had a permissive MIT license, which was what I was looking for.

But pure FastLZ was not completely satisfactory because it was not
simple enough.  It had 2 compression levels that
complicated the implementation quite a bit, so I decided to keep just the
highest level, and then optimize certain parts of it so that speed
would be acceptable.  These modifications gave birth to BloscLZ, which
is still being default compressor in Blosc.

But I had more ideas on what other features the new Blosc compressor
should have, namely, multi-threading and an integrated shuffle filter.
Multi-threading made a lot of sense by 2008 because both Intel and AMD
already had a wide range of multi-core processors by then, and it was
clear that the race for throwing more and more cores into systems was
going to intensify.  A fast compressor had to be able to use all these
cores dancing around, **period**.

Shuffle (see slide 71 of this `presentation
<http://blosc.org/docs/StarvingCPUs.pdf>`_) was the other important
component of the new compressor.  This algorithm relies on
neighboring elements of a dataset being highly correlated to improve
data compression.  A shuffle filter already came as part of the `HDF5
library <http://www.hdfgroup.org/HDF5/>`_ but it was implemented in
pure C, and as it had an important overhead in terms of computation, I
decided to do an `SIMD version
<https://github.com/Blosc/c-blosc/blob/master/blosc/shuffle.c>`_ using
the powerful `SSE2 instructions <http://en.wikipedia.org/wiki/SSE2>`_
present in all Intel and AMD processors since 2003.  The result is
that this new shuffle implementation adds almost zero overhead
compared with the compression/decompression stages.

Once all of these features were implemented, I designed a pretty
comprehensive `suite of tests
<http://blosc.org/synthetic-benchmarks.html>`_ and asked the PyTables
community to help me testing the new compressor in as much systems as
possible.  After some iterations, we were happy when the new
compressor worked flawlessly compressing and decompressing **hundreds
of terabytes** on many different Windows and Unix boxes, both in
32-bit and 64-bit.  The new beast was ready to ship.

Blosc was born
--------------

I then grabbed BloscLZ, the multi-threading support and the
SSE2-powered shuffle and put it all in the same package.  That also became a
**standalone, pure C library**, with no attachments to PyTables or HDF5,
so any application could make
use of it.  I have got the first stable version (1.0) of Blosc
released by `July 2010 <http://www.groupsrv.com/science/about538609.html>`_.
Before this, I already introduced Blosc publicly in my `EuroSciPy 2009 keynote
<http://www.blosc.org/docs/StarvingCPUs.pdf>`_ and also made a small
reference to it in an article about `Starving CPUs
<http://www.blosc.org/docs/StarvingCPUs-CISE-2010.pdf>`_ where I
stated:

  "As the gap between CPU and memory speed continues to widen, I
  expect Blosc to improve memory-to-CPU data transmission rates over
  an increasing range of datasets."

And that is the thing.  As CPUs are getting faster, the chances for
using compression for an advantage can be applied to more and more
scenarios, to the point that improving the bandwidth of main memory
(RAM) is becoming possible now.  And surprisingly enough, the methodology
for achieving that is the same than back in the C-news ages: strike a good
balance between data block sizes and compression speed, and let
compression make your applications handle data faster and not only
making it more compact.

When seen in perspective, it has been a long quest over the last
decades.  During the 90's, compression was useful to improve the
bandwidth of slow internet connections.  In the 2000's, it made
possible accelerating disk I/O operation.  In the 2010's Blosc goal is
making the memory subsystem faster and whether it is able to
achieve this or not will be the subject of future blogs (hint: data
arrangement is critical too).  But one
thing is clear, achieving this (by Blosc or any other compressor out
there) is just a matter of time.  Such is the fate of the ever
increasing gap in CPU versus memory speeds.
