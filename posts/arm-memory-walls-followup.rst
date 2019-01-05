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

Also, the fact that ARM is not just providing licenses to use its IP cores, but also the possibility to buy an architectural licence for clients to design their own CPU cores using the ARM instruction sets makes possible that other players like Apple, AppliedMicro, Broadcom, Cavium (now: Marvell), Nvidia, Qualcomm, and Samsung Electronics can produce CPUs that can be adapted to be used in different scenarios.  One that is interesting for this discussion is Marvell who, with its ThunderX2 CPU, is already entering into the computing servers market --actually, a new super-computer with more than 100,000 ThunderX2 cores has recently entered into the `TOP500 ranking <https://t.co/LM2wXQrXm8>`_, the first time that an ARM-based computer enters that list, dominated by Intel architectures for almost two decades now.

Now, the legitimate question is: is ARM fulfilling its promise, or their announcement was just bare marketing?  For answering this, I decided to use two recent (2018) implementations of the ARMv8-A architecture and replicate the benchmarks in my previous `Breaking Down Memory Walls <http://blosc.org/posts/breaking-memory-walls/>_` blog entry.

The ARM A76 core
----------------

This is an example of an internal IP core design of ARM that is licensed to be used in other

The ThunderX2 core
------------------


Acknowledgements
----------------


Appendix: Software used
-----------------------

For reference, here it is the software that has been used for this blog entry:

* **OS**: Ubuntu 18.04
* **Compiler**: GCC 7.3.0
* **C-Blosc2**: 2.0.0a6.dev (2018-05-18)
