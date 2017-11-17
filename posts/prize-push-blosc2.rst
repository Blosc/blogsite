.. title: Blosc Has Won The Open Source Peer Bonus
.. author: Francesc Alted
.. slug: prize-push-Blosc2
.. date: 2017-11-17 17:32:20 UTC
.. tags: Google, Prize, Blosc2
.. category:
.. link:
.. description:
.. type: text


Blosc Has Won The Open Source Peer Bonus
========================================

Past month `Google announced the winners for the 2017’s second round of their Open Source Peer Bonus program <https://opensource.googleblog.com/2017/10/more-open-source-peer-bonus-winners.html>`_ and I was among them for my commitment to the Blosc project.  It took a bit, but I wanted to express my thoughts on this nice event.  Needless to say, I am proud and honored for this recognition, most specially when this is the first completely uninterested donation that someone made to me after 15 years of doing open source (in many occasions doing that as a full-time work), so thank you very much Google!  The assumption is that people does open source because 1) they believe in the concept and 2) they can earn a public consideration that allows them to get contracts (so allowing many of us to have a life!).  However, this time the unexpected happened, and that an important corporation like Google decided to publicly recognize this work makes me very happy (would that pave the way for others to follow? :-).

In fact, this prize comes very timely because it is giving me more stamina towards the release of `Blosc2 <https://github.com/Blosc/c-blosc2>`_.  Blosc2 is the next generation of Blosc, and will add features like:

* Full 64-bit support for chunks (i.e. not anymore limited to 2 GB). 
* New filters, like delta and truncation of floating point precision.
* A new filter pipeline that will allow to run more than one filter before the compression step.
* Support for variable length objects (i.e. not limited to fixed-length datasets).
* Support for dictionaries between different blocks in the same chunk.  That will be important for allowing smaller chunks (and hence improving decompression latency) while keeping compression ratio and performance relatively untouched.
* Support for more codecs (`lizard <http://blosc.org/posts/new-lizard-codec/>`_ support is already in).
* New serialisation format which is meant to allow self-discovery via magic numbers and introspection.
* New super-chunk object that will allow to work seamlessly with arbitrarily large sets of chunks, both in-memory and on-disk.
* Support for `SIMD in ARM processors <http://blosc.org/posts/arm-is-becoming-a-first-class-citizen-for-blosc/>`_.

All in all, and after more than 2 years working in different aspects of these features, I am quite satisfied on the progress so far. My expectation was to do a beta release during this fall, and although the work is quite advanced, there are still some loose ends that require quite a bit of work.  If you like where I am headed and are interested in seeing this work to complete faster, a contribution to the project in the form of a pull request or, better yet, a donation suggesting which feature you would like the most will be greatly appreciated.

Finally, I'd like to take the opportunity to annonunce that Blosc has a logo (finally!). You can admire it at the header of this page.  This is the work of `Domènec Morera <http://domenec123.blogspot.com.es>`_ who also made for us the logo of `PyTables <http://www.pytables.org>`_.  I really think he is a great artist and that he did an excellent job again; I hope the new logo will be beneficial for the Blosc project as a whole!
