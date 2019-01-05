.. title: ARM and Memory Walls
.. author: Francesc Alted
.. slug: arm-memory-walls-followup
.. date: 2019-01-05 18:32:20 UTC
.. tags: arm, memory wall, tuning
.. category:
.. link:
.. description:
.. type: text


ARM CPUs and Memory Walls
=========================

At the beginning of the 1990s the computing world was mainly using RISC (Reduced Instruction Set Computer) architectures, namely SPARC, Alpha, Power and MIPS CPUs for performing serious calculations and Intel CPUs were seen as something appropriate to run essentially personal applications on PCs, but basically nobody was thinking about them as a serious contender for the High Performance Computing arena.  Moreover, the average user was perceiving Intel (being CISC, Complex Instruction Set Computer) as an architecture clearly flawed for crunching numbers.  But Intel had an argument that almost nobody was ready to recognize: with its dominance of the PC market it quickly ranked to be the biggest CPU maker in the world and, with such an enormous revenue, Intel played its cards well and, by the beginning of 2000s, they were able to make of its architecture (remember, a CISC one) the one with the best compute/price ratio, and clearly extremely well suited for High Performance Computing.

Fast forward 20 years to the beginning of 2010s, with Intel clearly dominating the making of CPUs for crunching numbers, but with `the ARM architecture being the most widely used architecture in mobile devices and the most popular 32-bit one in embedded systems <https://cacm.acm.org/magazines/2011/5/107684-an-interview-with-steve-furber/fulltext_`.  By that time, ARM also introduced its ARMv8 specification, which added support for a 64-bit address space and 64-bit arithmetic, making of it an architecture that was serious enough for entering the HPC arena.  By 2017, with over 100 billion ARM processors produced, ARM was already the most widely used architecture in the world.  Now, the smart reader will have noted here a clear parallelism between the situation of Intel at the end of 1990s and ARM at the end of 2010s.

But for the parallelism to complete and see whether ARM would go ahead and take the place of Intel as a dominant architecture for computing during the next decade, an essential piece is: is ARM willing to invest in the pushing its architecture on the server side of the things, or are they comfortable enough with the current situation?  The answer is that, during 2018, ARM provided all the signs that they really want to push hard for the client market (PCs and laptops) with the `introduction of the Cortex A76 CPU <https://www.anandtech.com/show/13226/arm-unveils-client-cpu-performance-roadmap>`_ which looks to redefine the capability of ARM to compete with Intel at its own game:

.. image:: /images/arm-memory-walls-followup/arm-compute-plans.png
   :scale: 125 %
   :align: center

Also, the fact that ARM is not just providing licenses to use its IP cores, but also the possibility to buy an architectural licence for clients to design their own CPU cores using the ARM instruction sets makes possible that other players like Apple, AppliedMicro, Broadcom, Cavium (now: Marvell), Nvidia, Qualcomm, and Samsung Electronics can produce ARM CPUs that can be adapted to be used in different scenarios.  One example that is interesting for this discussion is Marvell who, with its ThunderX2 CPU, is already entering into the computing servers market --actually, a new super-computer with more than 100,000 ThunderX2 cores has recently entered into the `TOP500 ranking <https://t.co/LM2wXQrXm8>`_, the first time that an ARM-based computer enters that list, dominated by Intel architectures for almost two decades now.

Now, the legitimate question is: is ARM (and its licensees) fulfilling its promise, or this announcement was just bare marketing?  For answering this, I decided to use two recent (2018) implementations of the ARMv8-A architecture and replicate the benchmarks in my previous `Breaking Down Memory Walls <http://blosc.org/posts/breaking-memory-walls/>_` blog entry.


The Kirin 980 SoC
-----------------

Here we are going to analyze Huawei's Kirin 980, a SoC (System On a Chip) that uses the ARM A76 core internally. This is an example of an internal IP core design of ARM that is licensed to be used in a CPU chipset by another vendor (Huawei in this case).  The Kirin 980 wears 4 A76 cores plus 4 A55 cores, but the more powerful ones are the A76 (the A55 is more headed to do light tasks with very little energy consumption, which is critical specially for phones).  The A76 core is designed to be implemented with a 7nm technology (as it is the case here), and supports ARM's DynamIQ technology which allows scalability to target the specific requirements of a SoC.  The case that we are analyzing here is Kirin 980 in a phone (Humawei's Mate 20), and in this scenario the power dissipation (TDP) cannot exceed the 4 W figure, so DynamIQ should avoid to make too many cores active at the same time, as we will see that it is the case for our benchmark below.

ARM is saying that they designed the `A76 to be a competitor of the Intel Skylake Core i5 <https://arstechnica.com/gadgets/2018/06/arm-promises-laptop-level-performance-in-2019/>`_, so this is what we are going to check here.  For this, we are going to compare a Kirin 980 in a Mate 20 against a Core i5 included in a MacBook Pro (late 2016).  Here it is the side-by-side performance for the `precipitation dataset <http://blosc.org/posts/breaking-memory-walls/>_` (i.e. a real dataset):

.. |rainfall-kirin980| image:: /images/arm-memory-walls-followup/kirin980-rainfall.png
   :scale: 70 %

.. |rainfall-i5| image:: /images/arm-memory-walls-followup/i5-rainfall.png
   :scale: 70 %

+---------------------+-----------------+
| |rainfall-kirin980| | |rainfall-i5|   |
+---------------------+-----------------+

Here we can already see a couple of things.  First, the speed of the calculation of the reduction when there is no reduction is similar for both CPUs.  This is interesting because, although the bottleneck for this benchmark is in the memory access, the fact that the Kirin 980 performance is almost the same than the Core i5 is a testimony of how well ARM performed in the design of a memory prefetcher, clearly allowing for a good memory-level parallelism.

Second, for the compressed case, although the Core i5 is still a 50% faster than the Kirin 980, the big news here is that the Core i5 has a TDP of 28 W, whereas for the Kirin 980 is just 4 W (and probably less than that).  It is also true that we are comparing an Intel CPU from 2016 against an ARM CPU from 2018; nowadays probably we can find Intel exemplars showing a similar performance than this i5 for probably no more than 10 W (e.g. an `i5-8265U with configurable TDP-down <https://ark.intel.com/products/149088/Intel-Core-i5-8265U-Processor-6M-Cache-up-to-3-90-GHz->_`).  On its part, and still having the same amount of high performance cores (4), the Kirin 980 still consumes less than half of the power than its Intel counterpart --and its price would probably be a fraction of it too.

I believe that these facts are really a good testimony of how serious ARM was on their claim that they were going to catch Intel in the performance side of the things for client devices, and probably with an edge in consuming less energy (nothing surprising, given the focus of ARM in that area for decades).  Keep this in mind when you are going to buy your next laptop and do not blindly assume that Intel is the only reasonable option anymore ;-)


The ThunderX2 core
------------------


Acknowledgements
----------------


Appendix: Software used
-----------------------

For reference, here it is the software that has been used for this blog entry.

For the Kirin 980:

* **OS**: Android 9 - Linux Kernel 4.9.97
* **Compiler**: clang 7.0.0
* **C-Blosc2**: 2.0.0a6.dev (2018-05-18)

For the ThunderX2:

* **OS**: Ubuntu 18.04
* **Compiler**: GCC 7.3.0
* **C-Blosc2**: 2.0.0a6.dev (2018-05-18)
