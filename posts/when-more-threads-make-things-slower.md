<!--
.. title: When More Threads Make Things Slower
.. slug: when-more-threads-make-things-slower
.. date: 2026-10-12 13:00:00 UTC
.. tags: Blosc2, compression, performance, threading
.. category: posts
.. link:
.. description: How avoiding unnecessary worker setup reduces the cost of small compression requests in C-Blosc2.
.. type: text
.. author: Johnny Kao
-->

*How a small change to worker scheduling improved small compression requests, and what the results mean for data-processing workloads.*

A common assumption in performance engineering is that more threads should make a program faster. This works well when there is enough work to distribute, but it can backfire when the task is smaller than the overhead of organizing the workers. Imagine a kitchen preparing a single sandwich: bringing fifteen additional cooks into the room would probably take longer than preparing the order. Compression can run into much the same problem when an application has configured many threads but supplies only a small amount of data.

While working on [C-Blosc2 PR #805](https://github.com/Blosc/c-blosc2/pull/805), I found that a small compression request could spend much more time preparing parallel execution than performing useful compression work. In one focused Linux benchmark, a **16 KiB request with sixteen configured threads and a newly created compression context** took approximately **710 microseconds** before the change and **18 microseconds** afterward, a speedup of almost **39×** in that specific configuration. The compression algorithm itself was unchanged. The improvement came from deciding whether parallel workers were needed *before* paying to prepare them.

<!-- TEASER_END -->

## Where the Overhead Comes From

Parallel compression is useful when the input contains enough blocks to keep multiple workers busy. A small request, however, may contain only one block, even if the calling application has configured sixteen threads. In that case there is nothing to split among the available workers, so preparing parallel execution cannot accelerate the actual compression. The startup cost can instead dominate the elapsed time, particularly if the application creates a fresh compression context for each operation.

The first part of PR #805 addresses precisely that mismatch. Before initializing parallel workers, the library can determine whether the input offers only a single unit of work and take the direct path when it does. This avoids unnecessary worker setup without changing the data format or the compression operation that processes the block.

![Before and after: a single-block job skips unnecessary parallel startup](/images/pr805-threads/01-startup.svg)

*For a single-block request, skipping parallel startup removes work that cannot contribute to compression throughput.*

A related inefficiency appears when the input has a few blocks, but fewer than the configured number of threads. For example, sixteen available threads do not make sixteen workers useful when there are only three blocks to process. PR #805 also limits the work assigned to the number of blocks that can actually benefit from parallelism, rather than preparing assignments for workers with nothing to do.

![Workers assigned before and after PR #805](/images/pr805-threads/02-workers.svg)

*With three blocks and sixteen configured threads, at most three workers can have useful block assignments.*

These are intentionally modest changes: instead of introducing a new compression algorithm or trying to make thread creation inherently faster, they avoid parallel work that the current request cannot use. This also makes the performance behavior easier to explain. The optimization should have its strongest effect on small inputs where scheduling and startup are a large fraction of total latency, while the benefit becomes less important as actual compression work grows.

## What This Means for a Rainfall Dataset

To evaluate the change with realistic data rather than an artificial byte pattern, I used a rainfall-data sample and repeated it to construct inputs of different sizes. Rainfall data is a useful illustration because an application might ingest observations, transform or aggregate them, and compress batches of measurements before writing them to storage. The relevant distinction for this optimization is not that the measurements represent rainfall, but **how much data each individual compression call receives and whether its compression context is reused**.

Consider a workflow that reads a rainfall dataset, divides it into small chunks, and compresses those chunks separately as they are produced. If the application repeatedly creates new compression contexts for tiny chunks while leaving a relatively high thread count configured, each call may pay a substantial setup cost despite having only one useful block. PR #805 reduces that portion of the per-call cost. In such a workflow the **compression stage for small chunks** can become faster, and repeated savings may accumulate over many calls. This does not imply that loading the rainfall file, computing rainfall statistics, accessing storage, or the entire end-to-end pipeline becomes 39 times faster; those activities were not measured by the focused compression benchmark.

For example, if the application spends most of its time compressing many small independently processed chunks, a lower per-chunk compression latency could make a noticeable difference to throughput. If it instead loads the data once, keeps a compression context alive, and compresses large blocks, worker setup is a smaller part of the total cost, so the improvement may be modest. Applications that only decompress existing rainfall data should not expect a speedup from this compression-side change. These distinctions matter more for predicting practical gains than the overall size of the rainfall dataset: a large dataset processed as many tiny requests behaves differently from one compressed in a few large requests.

## Benchmark Results and Their Limits

I compared the original C-Blosc2 implementation with the modified version on the same Linux machine, using the same data and compression settings. The measurements deliberately cover different request sizes and distinguish newly created compression contexts from reused ones, since those two usage patterns expose very different amounts of worker-startup overhead. The complete [benchmark code and results](https://github.com/Johnny-Kao/c-blosc2-pr805-reproducibility) are available, along with a [successful GitHub Actions run](https://github.com/Johnny-Kao/c-blosc2-pr805-reproducibility/actions/runs/37950149167).

![Before and after with newly created compression contexts](/images/pr805-threads/03-new-context.svg)

*Selected configurations in which a fresh compression context is created for each request. Lower latency is better; timings are in microseconds.*

The largest improvement among the configurations discussed here came from the **16 KiB, sixteen-thread, fresh-context** test: about **710 µs** before the patch versus **18 µs** after it, or nearly **39×** faster. At the same request size with four configured threads, the measured speedup was greater than **10×**. These results directly support the startup-overhead explanation: when a call has little actual compression work and must prepare its context, eliminating unnecessary parallel preparation can remove most of its previous runtime.

The pattern changes for larger inputs. As compression occupies more of the total execution time, worker preparation represents a smaller share of each request, and additional threads may be doing useful work. It would therefore be misleading to treat the best small-request speedup as the expected improvement for an entire rainfall-processing application or for all compression workloads.

![Before and after with reused compression contexts](/images/pr805-threads/04-reused-context.svg)

*Selected configurations using a reused context and sixteen configured threads. Lower latency is better; the effects vary by workload.*

With a reused compression context, the measured results were more mixed: some configurations improved, others changed little, and a few became slower. This is an important limitation rather than a contradiction. The high fresh-context speedups largely concern setup that a reused-context workflow has already amortized, while other scheduling costs can become more prominent. Consequently, the most defensible practical expectation is **lower latency for small compression requests that otherwise incur unnecessary parallel setup**, not a universal increase in compression throughput.

## Why We Did Not Keep Workers Permanently Ready

The merged solution was not my first attempt. I initially experimented with keeping workers ready between operations so subsequent calls would not need to repeat their setup. In an early experiment, an operation that took approximately **40 µs** was reduced to roughly **2 µs**. Although promising, that approach also introduced lifecycle problems that were absent from the simpler change.

One example arose when a program created a new process using a fork-like operation. The child could inherit bookkeeping that referred to waiting workers without inheriting those running workers themselves, leaving the new process waiting for threads that no longer existed. We investigated a way to handle that situation, but doing so increased the complexity of resource management and of the states that needed to remain correct. Keeping a worker pool alive is not merely a one-time performance choice; it also requires the library to manage that pool reliably across process and context lifetimes.

The final approach takes a narrower path: avoid preparing unnecessary workers rather than maintaining additional ones indefinitely. This captured an important benefit for the small-request case without introducing a new persistent-worker lifecycle. Platform behavior also mattered during review and testing; in particular, the existing startup behavior was preserved on Windows rather than accepting a compatibility regression for the sake of the optimization. These constraints are part of the engineering result, not incidental details.

## Conclusions

PR #805 is an example of a performance improvement that comes from avoiding work, rather than making the central algorithm more sophisticated. When there is only one compression block, preparing a parallel team has no benefit, and when there are only a few blocks, creating assignments for many more workers adds overhead without additional useful processing. Checking the work available before preparing parallel execution provides a direct way to remove those costs.

For users processing rainfall observations or similar scientific arrays, the change is most relevant when data is compressed in **many small requests**, especially with **fresh contexts and a thread count larger than the number of useful blocks**. The measurements show substantial improvements for targeted requests, but they do not establish an equivalent speedup for reading, analyzing, or storing the full dataset. The practical lesson is to examine not only the total volume of data, but also the size and lifecycle of the operations that process it.

The change was merged as [C-Blosc2 PR #805](https://github.com/Blosc/c-blosc2/pull/805). I would like to thank Francesc Alted and the Blosc maintainers for their reviews and for helping keep the final implementation simpler and safer. The broader takeaway is straightforward: before optimizing the cost of parallel execution, check whether the current workload needs that parallel execution at all.
