.. title: Blosc metalayers, where the user metainformation is stored
.. author: Aleix Alcacer
.. slug: blosc-metalayers
.. date: 2021-03-05 7:32:20 UTC
.. tags: blosc2 metalayers
.. category: posts
.. link:
.. status:
.. description:
.. type: text


The C-Blosc2 library has two different spaces to store user-defined information.
In this post, we are going to describe what these spaces are and where they are
stored inside a Blosc2 frame (a persistent super-chunk).

As its name suggests, a metalayer is a space that allows users to store custom information.
For example, `Caterva`_, a project based on C-Blosc2 that handles
compressed and chunked arrays, uses these metalayers to store the dimensions and
the shape, chunkshape and blockshape of the arrays.

.. _Caterva: https://github.com/Blosc/Caterva


Fixed-length metalayers
-----------------------

The first kind of metalayers in Blosc2 are the fixed-length metalayers.
These metalayers are stored in the header of the frame.
This decision allows adding chunks to the frame without the need to
rewrite the whole meta information and data coming after it.

But this implementation has some drawbacks. The most important one is that
fixed-length metalayers cannot be resized.  Furthermore, once the first chunk of data is added
to the super-chunk, no more fixed-length metalayers can be added either.

Let's see with an example the reason for these restrictions. Supose that we
have a frame that stores 10 GB of data with a metalayer containing a "cat".
If we update the meta information with a "dog" we can do that because they
have exactly the same size.

However, if we were to update the meta information with a "giraffe", the
metalayer would need to be resized and therefore we would have to rewrite
the 10GB of data plus the trailer.
This would obviously be very inefficient and hence, not allowed:

.. figure:: /images/metalayers/metalayers.png

   Data that would need to be rewritten are ploted in red.



Variable-length metalayers
--------------------------

To fix the above issue, we have introduced variable-length metalayers.
Unlike fixed-length metalayers, these are stored in the trailer
section of the frame.

As their name suggests, these metalayers can be resized. Blosc can do that because,
whenever the metalayers content are modified, Blosc rewrites the trailer completely,
using more space if necessary.  Furthermore, and since these metalayers are stored in the trailer, 
they will also be rewritten each time a chunk is added.

Another feature of variable-length metalayers is that their content is
compressed by default (in contrast to fixed-length metalayers).
This will minimize the size of the trailer, a very important feature
because since the trailer is rewritten every time new data is added, we
want to keep it as small as possible so as to optimize data written.

Let's continue with the previous example, but storing the meta
information in a variable-length metalayer now:

.. figure:: /images/metalayers/metalayers-vl.png

In this case the trailer is rewritten each time that we update the metalayer, 
but it is a much more efficient operation than rewriting all the data (as a fixed-length metalayer would require).
So the variable-length metalayers complement the fixed-length metalayers by bringing different capabilities on the table.
Depending on her needs, it is up to the user to choose one or another metalayer storage.

Fixed-length vs variable-length metalayers comparsion
-----------------------------------------------------

To summarize, and to better see what kind of metalayer is more suitable
for each situation, the following table contains a comparison between fixed-length
metalayers and variable-length metalayers:

+---------------------------------------+-------------------------+----------------------------+
|                                       | Fixed-length metalayers | Variable-length metalayers |
+---------------------------------------+-------------------------+----------------------------+
| Where are stored?                     |          Header         |            Trailer         |
+---------------------------------------+-------------------------+----------------------------+
| Can be resized?                       |          No             |            Yes             |
+---------------------------------------+-------------------------+----------------------------+
| Can be added after adding chunks?     |          No             |            Yes             |
+---------------------------------------+-------------------------+----------------------------+
| Are they rewritten when adding chunks?|          No             |            Yes             |
+---------------------------------------+-------------------------+----------------------------+


Metalayers API
--------------

Currently, C-Blosc2 has the following functions implemented:

- ``blosc2_meta_add()`` / ``blosc2_vlmeta_add()``: Add a new metalayer.
- ``blosc2_meta_get()`` / ``blosc2_vlmeta_get()``: Get the metalayer content.
- ``blosc2_meta_exists()`` / ``blosc2_vlmeta_exists()``: Check if a metalayer exists or not.
- ``blosc2_meta_update()`` / ``blosc2_vlmeta_update()``: Update the metalayer content.


Conclusions
-----------

As we have seen, Blosc2 supports two different spaces where users can store
their meta information.  The user can choose one or another depending on her needs.

On the one hand, the fixed-length metalayers are meant to store user meta
information that does not change size over time.
They are stored in the header and can be updated without having to rewrite any
other part of the frame, but they can no longer be added once the first chunk
of data is added.

On the other hand, for users storing meta information that is going to change in size over time,
they can store their meta information into variable-length metalayers.  These
are stored in the trailer section of a frame and are more flexible
than its fixed-length counterparts.  However, each time that a metalayer content is
updated, the whole trailer has to be rewritten.
