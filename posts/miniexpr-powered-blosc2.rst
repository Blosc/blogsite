.. title: Miniexpr-Powered Blosc2: Beating the Memory Wall (Again)
.. author: Francesc Alted
.. slug: miniexpr-powered-blosc2
.. date: 2026-01-27 08:05:21 UTC
.. tags: roofline, performance, Blosc2, miniexpr, numpy, numexpr, memory wall
.. category: posts
.. link:
.. description:
.. type: text

In my previous post, *The Surprising Speed of Compressed Data: A Roofline Story*, I showed that Blosc2 could shine in out-of-core workloads, but for in-memory, low-intensity computations it often lagged behind Numexpr. That result was so counter-intuitive that it motivated a new effort: **miniexpr**, a block-level expression engine designed to evaluate Blosc2 blocks in parallel and keep the working set in L1/L2 as much as possible.

This post shows what changed.

TL;DR
-----

* The new miniexpr path dramatically improves **low-intensity** performance in memory.
* The biggest gains are in the **very-low/low** kernels where cache traffic dominates.
* High-intensity (compute-bound) workloads remain essentially unchanged, as expected.
* There is one regression: **AMD on-disk uncompressed** got slower; we call that out below.

Before/After: A Quick Look
--------------------------

The following bar plots compare **old vs miniexpr** for Blosc2 (compressed and uncompressed). I'm showing only the low-to-medium intensities, because that's where the memory wall dominates and the changes are most visible.

.. image:: /images/miniexpr-powered-blosc2/barplot-AMD-7800X3D-in-memory.png

.. image:: /images/miniexpr-powered-blosc2/barplot-Apple-M4-Pro-in-memory.png

.. image:: /images/miniexpr-powered-blosc2/barplot-AMD-7800X3D-on-disk.png

.. image:: /images/miniexpr-powered-blosc2/barplot-Apple-M4-Pro-on-disk.png

Mini Tables (Compressed Blosc2, GFLOPS)
---------------------------------------

.. table:: In-memory (old -> miniexpr)

   ===========  =======================  ======================
   CPU          very-low (old->new, x)   low (old->new, x)
   ===========  =======================  ======================
   AMD 7800X3D  0.41 -> 1.70 (4.16x)     2.20 -> 6.32 (2.87x)
   Apple M4 Pro 0.91 -> 2.31 (2.53x)     3.28 -> 9.24 (2.82x)
   ===========  =======================  ======================

.. table:: On-disk (old -> miniexpr)

   ===========  =======================  ======================
   CPU          very-low (old->new, x)   low (old->new, x)
   ===========  =======================  ======================
   AMD 7800X3D  0.57 -> 1.41 (2.50x)     2.66 -> 5.58 (2.10x)
   Apple M4 Pro 0.49 -> 0.95 (1.93x)     2.57 -> 5.31 (2.07x)
   ===========  =======================  ======================

Roofline Context
----------------

To connect the "before/after" gains to the memory wall, here are the updated roofline plots. These show how the low-intensity points move up without changing arithmetic intensity--exactly what we expect when cache traffic is reduced.

.. image:: /images/miniexpr-powered-blosc2/roofline_plot-AMD-7800X3D-in-memory.png

.. image:: /images/miniexpr-powered-blosc2/roofline_plot-Apple-M4-Pro-in-memory.png

.. image:: /images/miniexpr-powered-blosc2/roofline_plot-AMD-7800X3D-on-disk.png

.. image:: /images/miniexpr-powered-blosc2/roofline_plot-Apple-M4-Pro-on-disk.png

Discussion: What Changed?
-------------------------

In the original post I attributed the low-intensity slowdown mainly to indexing overhead when extracting operand chunks. The new results suggest a different dominant cost: **cache traffic**. The old path evaluates whole chunks per operand, which inflates the working set beyond L2/L1 and pushes a lot of data through L3 and memory. With miniexpr, computation happens on much finer blocks in parallel, keeping most traffic in L1/L2 and shrinking the working set per thread. The roofline behavior matches this: very-low and low intensities jump up sharply, while high-intensity points are essentially unchanged.

Indexing still matters, but it is minimized when operands share the **same chunk and block shapes**. This alignment is common for large arrays with a consistent storage layout, and when it holds, miniexpr delivers the big gains shown above. When it doesn't, python-blosc2 automatically falls back to the previous chunk/numexpr path, preserving coverage and correctness while trading off some performance.

A note on baselines: on my current Mac runs, the Numexpr in-memory baseline is lower than in the original post. I re-ran the benchmark several times and the numbers are stable, but I did not pin down the exact cause (BLAS build or dataset/layout differences are plausible). The comparisons here are still apples-to-apples because all runs are from the same environment.

A Note on Regressions
---------------------

There is one case where results regress: **AMD on-disk, uncompressed**. The most plausible explanation is I/O overlap. In the previous chunk/numexpr path, the next chunk could be read in parallel while worker threads were computing on the current one. In the miniexpr path, all blocks of a chunk must be read sequentially before the block-level compute phase starts, so that overlap is largely lost. This would disproportionately hurt the on-disk, uncompressed case on AMD/Linux. The curious part is that Apple on-disk, uncompressed improves, which suggests that parallel chunk reads were not helping much on macOS (for reasons we do not yet understand). We will keep investigating.

Conclusions
-----------

Miniexpr flips the "surprising story" from the previous post. In-memory, low-intensity kernels--the classic memory-wall case--now see large gains, while compute-bound workloads behave as expected. The roofline shifts confirm the diagnosis: this is a cache-traffic problem, and miniexpr fixes it by working at the block level.

This is a big step forward for "compute-on-compressed-data" in Python, and a strong foundation for future work (including the remaining on-disk regression).

----

Read more about `ironArray SLU <https://ironarray.io>`_ -- the company behind Blosc2, Caterva2, Numexpr and other high-performance data processing libraries.

Compress Better, Compute Bigger!
