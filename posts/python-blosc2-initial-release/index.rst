.. title: Wrapping C-Blosc2 in Python (a beginner's view)
.. author: Marta Iborra
.. slug: python-blosc2-initial-release
.. date: 2021-05-10 07:32:20 UTC
.. tags: blosc2 python
.. category:
.. link:
.. status:
.. description:
.. type: text


An initial release of the Python wrapper for
C-Blosc2 is now available in: https://github.com/Blosc/python-blosc2.
In this blog I will try to explain some of the most difficult aspects that I had to learn in doing this
and how I solved them.

This work is being made thanks to a grant from the Python Software Foundation.

Python views
------------

At university, the first programming language that I learned was Python. But because programming was
new for the majority of the class the subject only covered the basics: basic statements and classes.
And although these were easy to understand, the views were unknown to me (until now).

To explain what the views are, let’s suppose we have the following code in Python::

    >>> import sys
    >>> a = []
    >>> b = a
    >>> sys.getrefcount(a)
    3

The reference count for the object is 3: a, b and the argument passed to
sys.getrefcount().

Basically, to avoid making copies of a same variable, Python uses views. Every variable has its counter and until the counter is 0, the variable is not deleted.
But that means that two threads cannot access the counter at the same time.  Because having a lock for every variable would be inefficient and could produce deadlocks (which means that several threads are waiting for each other), the GIL was created.  So GIL was my next thing to learn.

GIL and Cython
--------------

GIL stands for Global Interpreter Lock. With a single lock
on the interpreter there are no deadlocks. But the execution of any
Python program must acquire the interpreter lock, which prevents some
programs to take advantage of the multi-threading execution.

When writing C extensions, this lock is very useful because
it can be released. Thus, the program can be more efficient (i.e.
threads can actually run in parallel).
To write a function with the GIL I spent many time reading about it.
Unfortunately, nothing seemed to expain what I wanted to do until
I found this nice
`blog <http://nicolas-hug.com/blog/cython_notes#>`_
from
Nicolas Hug
in which he explains the 3 rules you have to follow to make Cython release the GIL.

First of all, Cython needs to know which C functions that were imported are thread-safe.
This is done by using the `nogil` statement in the function declaration.
Then, inside the function the `with nogil` statement lets Cython know that this block is
going to be executed with the GIL released. But to make that code block safe,
there cannot be any Python interaction inside that block.

To understand it better, an example is shown below::

    cdef extern from "math_operation.h":
        int add(int a, int b)nogil

    cpdef sum(src, dest):
        cdef int len_src = len(src)
        cdef int len_dest = len(dest)
        cdef int result
        with nogil:
            # Code with the GIL released
            result = add(len_src, len_dest)
        # Code with the GIL, any Python interaction can be done here


The function `sum` returns the result of adding the length of `src` and `dest`.
As you can see, the function has been defined with the `cpdef` statement
instead of the `def`. The `c` lets Cython know that
this function can be called with C. So this is necessary when writing a
function with the GIL released, otherwise you will be trying to execute a Python
program without the GIL (which, as explained previously cannot be done).
Notice that `len_src` and `len_dest` have also been defined as C integers with the
`cdef int` statement. If not, it would not be possible to work with them
with the GIL released (the `with nogil` block).

On the other hand, the `p` lets Cython know that this function can be called through Python.
This does not have to be done always, only when you want to call that function from Python.


Cython typed memoryviews
------------------------

One of the main differences between  the python-blosc
and python-blosc2 API, is that the functions `compress_ptr`
and `decompress_ptr` are no longer supported. We decided
to do so, because the Pickle protocol 5 already makes
an optimization of the copies. That way, we could have
a similar performance for `compress_ptr`
and `decompress_ptr` but with the functions `pack`
and `unpack`.

However, when timing the functions I realised that
in the majority of the cases,
although
the `compress` function from python-blosc2 was faster
than the `compress_ptr`,
the
`decompress` function was slower than the `decompress_ptr`.
Thus I checked the code to see if the
speed could somehow be
increased.

Originally, the code used the Python Buffer Protocol.
which is part of the Python/C API. The Python Buffer Protocol lets
you (among other things) obtain a
pointer to the raw data of an object. But because
it wasn't clear for me wether it needed to do a copy
or not
we decided to work with Cython typed memoryviews.

Cython typed memoryviews are very similar to
Python memory views, but with the main difference
that the
first ones are a C-level type and therefore
they do not have much Python overhead.
Because it is a C-level type you have to know
the dimension of the buffer from which you want to
obtain
the typed memoryview as well as its data type.

The shape dimension of the buffer is expressed writing
as many ``:`` between brackets as dimensions it has.
If the memory is allocated contiguously, you can write
``::1`` instead in the corresponding dimension.
On the other hand, the type is expressed as you would
do it in Cython.
In the following code, you can see an example for a
one-dimensional numpy array::

 import numpy as np
 arr = np.ones((10**6,), dtype=np.double)
 cdef double [:] typed_view = arr

However, if you want to define a function that receives
an object whose type may be unknown,
you will have to create a
Python memoryview and then cast it into the
type you wish as in the next example::

 # Get a Python memoryview from an object
 mem_view = memoryview(object)
 # Cast that memory view into an unsigned char memoryview
 cdef unsigned char[:]typed_view = mem_view.cast('B')

The 'B' indicates to cast the memoryview type into an
unsigned char.

But if I run the latter code for a binary Python string,
it produces a runtime error. It
took me 10 minutes to fix the error adding the
`const` statement to the definition of the Cython
typed memoryview (as shown below), but I spent two
days trying to
understand the error and its solution. ::

 # Get a Python memoryview from an object
 mem_view = memoryview(object)
 # Cast that memory view into an unsigned char memoryview
 cdef const unsigned char[:]typed_view = mem_view.cast('B')

The reason why the `const` statement fixed it, is that a binary Python string is
a read-only buffer. By declaring the
typed memoryview to `const`, Cython is being told that
the object from the memory view is a read-only buffer
so that it cannot change it.

Conclusions
-----------

So far, my experience wrapping `C-Blosc2` has had
some ups and downs.

One method that I use whenever I learn something new is
to write down a summary of what I read. Sometimes is almost a
copy (therefore some people may find it useless), but
it always works really well for me.
It helps me connect the ideas better or
to build a global idea of what I have or want to do.

Another aspect I realized when doing this wrapper is that because
I am a stubborn person, I usually tend to
force myself to try to understand something and get frustrated
if I do not.
However,
I have to recognize that sometimes it is better to
forget about it until the next day. Your brain will organize
your ideas at night so that you can invest better your time
the next morning.

But maybe the most difficult
part for me was the beginning, and therefore
I have to thank Francesc Alted and
Aleix Alcacer for giving me a push into the not always easy
 world of Python extensions.
