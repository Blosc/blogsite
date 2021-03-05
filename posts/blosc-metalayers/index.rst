.. title: Blosc metalayers, where the user metainformation is stored
.. author: Aleix Alcacer, Francesc Alted
.. slug: blosc-metalayers
.. date: 2021-03-04 7:32:20 UTC
.. tags: blosc2 metalayers
.. category:
.. link:
.. status:
.. description:
.. type: text


Blosc2 format introduces two different spaces to store user-defined information.
In this post, we are going to describe what these spaces are and where they are
stored inside a Blosc persistent schunk.

The concept of metalayers has been introduced in the Blosc2 format. As its
name suggests, a metalayer is a space in the Blosc2 format that allows users to
store custom information.
For example, `Caterva`_, a project based on c-blosc2 that manipulates
compressed and chunked arrays, uses metalayers to store the dimension and
the shape/chunkshape/blockshape of the arrays.

.. _Caterva: https://github.com/Blosc/Caterva



Fixed-length metalayers
-----------------------

The first metalayers defined in the Blosc2 format are the fixed-length metalayers.
These metalayers are stored in the frame header.
This decision allows adding Blosc chunks to the frame without the need to
rewrite the meta information (if they were stored in the trailer, they would
have to be rewritten each time).

But this implementation has some restrictions. The most important one is that
fixed-length metalayers cannot be resized.
Furthermore, once the first chunk of data is added, no more fixed-length
metalayers can be added. With these limitations, we make sure that we are not going
to rewrite the data each time we update the metalayers content.

Let's see with an example the reason for these restrictions. Supose that we
have a frame that stores 10GB of data with one metalayer containing a "cat".

If we update the meta information with a "dog" nothing bad happens because they
have the same size.

However, if we update the meta information with a "giraffe", the
metalayer must be resized and therefore we have to rewrite the 10GB of
data plus the trailer.
This procedure is obviously very inefficient and is not supported.

.. figure:: /images/metalayers/metalayers.png

   Data that must be rewritten are ploted in red.




Variable-length metalayers
--------------------------

To fix the above issue, variable-length metalayers are introduced into the
Blosc2 format.
Unlike fixed-length metalayers, these are stored in the trailer
section of a Blosc2 schunk.

As their name suggests, these metalayers can be resized. So whenever we
modify the metalayers content, we will  have to rewrite the trailer.
Furthermore, since they are stored in the trailer, they also will be rewritten
each time a chunk is added.

Another characteristic feature of these metalayers is that their content is
compressed.
This will minimize the size of the trailer, a very important factor
since the trailer is rewritten every time new data is added.

Let's continue with the previous example, but now we have the meta
information in a variable-length metalayer.

.. figure:: /images/metalayers/metalayers-vl.png

In this case, as we can see in the figure, the trailer is rewritten each time
that we update the metalayer.
But it is a much more efficient operation than rewriting all the data.
So the variable-length metalayers fixed the fixed-length metalaters limitations.

To summarize these two concepts and see what type of metalayer is more suitable
for each situation, the following table contains a comparison between fixed-length
metalayers and variable-length metalayers:

+---------------------------------------+-------------------------+----------------------------+
|                                       | Fixed-length metalayers | Variable-length metalayers |
+---------------------------------------+-------------------------+----------------------------+
| Where are stored?                     |          Header         |            Trailer         |
+---------------------------------------+-------------------------+----------------------------+
| Can be resized?                       |          False          |            True            |
+---------------------------------------+-------------------------+----------------------------+
| Can be added after adding chunks?     |          False          |            True            |
+---------------------------------------+-------------------------+----------------------------+
| Are not rewritten when adding chunks? |          True           |            False           |
+---------------------------------------+-------------------------+----------------------------+


Metalayers API
--------------

For now, both metalayers have the following functions implemented:

- ``blosc2_meta_add()`` / ``blosc2_vlmeta_add()``: Add a new metalayer.
- ``blosc2_meta_get()`` / ``blosc2_vlmeta_get()``: Get the metalayer content.
- ``blosc2_meta_has()`` / ``blosc2_vlmeta_has()``: Check if a metalayer exists or not.
- ``blosc2_meta_update()`` / ``blosc2_vlmeta_update()``: Update the metalayer content.


Conclusions
-----------

As we have seen, Blosc2 format introduces two spaces where users can store
their meta information.

On the one hand, the fixed-length metalayers are meant to store user meta
information that not changes over time.
They are stored in the header and can be updated without having to rewrite any
other part of the frame, but they can no longer be added once the first chunk
of data is added.

On the other hand, if users' meta information will change in size over time,
they can store their meta information into variable-length metalayers. These
metalayers are stored in the trailer section of a frame and are more flexible
than fixed-length metalayers. However, each time that a metalayer content is
updated, the trailer has to be rewritten.
