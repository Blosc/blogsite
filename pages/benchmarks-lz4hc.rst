.. title: Benchmarks for LZ4HC
.. slug: benchmarks-lz4hc
.. date: 2014-06-27 10:41:42 UTC
.. tags: 
.. link: 
.. description: 
.. type: text


* Processor model: IBM Blue Gene Q embedded "A2" processor
* Compiler: bgclang, version r209570-20140527 based on clang-3.5.0
* Optimizations: -O3, but as this is BGQ, no sse instructions
* OS: IBM Blue Gene Q driver version V1R2M1
* Contributed by: Rob Latham

`Suite output (64 threads) </images/bench/lz4hc/lz4hc-BGQ.txt>`__

.. image:: /images/bench/lz4hc/lz4hc-BGQ-compr.png
   :width: 50%
.. image:: /images/bench/lz4hc/lz4hc-BGQ-decompr.png
   :width: 50%

----

* Processor model: Intel Core i5 i5-3380M (2 x 2.9 GHZ) 3 MB Cache
* Compiler: GCC version 4.8.2-19ubuntu1
* OS: Ubuntu 14.04 3.13.0-29-generic #53-Ubuntu SMP (64 bit)
* Contributed by: Francesc Alted 

`Suite output (4 threads) </images/bench/lz4hc/i5-3380M-4.txt>`__

.. image:: /images/bench/lz4hc/i5-3380M-4-compr.png
   :width: 50%
.. image:: /images/bench/lz4hc/i5-3380M-4-decompr.png
   :width: 50%

