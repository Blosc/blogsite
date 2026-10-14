<!--
.. title: When More Threads Make Things Slower
.. slug: when-more-threads-make-things-slower
.. date: 2026-10-12 13:00:00 UTC
.. tags: Blosc2, compression, performance, threading
.. category: posts
.. link:
.. description: Why avoiding unnecessary parallel setup can make small C-Blosc2 compression requests faster.
.. type: text
.. author: Johnny Kao
-->

*Why matching the number of workers to the available compression blocks can make small requests much faster.*

More threads usually help compression when there is enough data to process in parallel. For a small request, however, the cost of preparing those threads can exceed the useful work. While working on [C-Blosc2 PR #805](https://github.com/Blosc/c-blosc2/pull/805), I found a case where a **16 KiB compression request with sixteen configured threads** took about **710 µs** with a fresh context. After the change, the same measured operation took about **18 µs**, almost **39× faster**. This is a result for that particular request and context lifecycle, not a 39× increase in the compression algorithm's throughput.

The improvement came from two decisions that are easy to distinguish: **skip parallel startup when a request contains only one block**, and **avoid scheduling workers that have no blocks to process** when a request contains only a few blocks. Neither requires changing how the data is compressed. To understand the results, we first need to look at what each decision avoids, and then at the tests used to evaluate them.

<!-- TEASER_END -->

## Two Ways to Avoid Unnecessary Parallel Work

### 1. Skip parallel startup for a single block

C-Blosc2 can divide an input into blocks and compress them in parallel, which is useful when several blocks can be processed independently. With a **16 KiB block size**, though, a **16 KiB input contains just one block**. Even if the application configures sixteen threads, there is still only one piece of compression work. Starting the parallel backend before recognizing that fact adds overhead without offering any opportunity for parallel speedup.

The first change in PR #805 makes that decision earlier. If the request has only one block, compression proceeds without preparing the parallel workers. The existing compression algorithm does the same useful work; the unnecessary setup simply no longer happens.

![Before and after: a single-block job skips unnecessary parallel startup](/images/pr805-threads/01-startup.svg)

*For a single block, the request can bypass parallel startup entirely.*

### 2. Schedule only workers that can do useful work

Not every request fits in a single block. Consider **three blocks with sixteen threads configured**: there is useful parallel work, but not enough to keep sixteen workers occupied. Preparing or notifying workers that will receive no block can still add scheduling overhead, even though some parallelism is appropriate.

The second change therefore matches the work dispatched to the number of available blocks rather than blindly following the configured thread count. Unlike the single-block path, this does not remove parallel execution; it limits unnecessary worker participation within it.

![Workers assigned before and after PR #805](/images/pr805-threads/02-workers.svg)

*When three blocks are available, there is no useful block assignment for thirteen additional workers.*

## Testing the Optimization

The purpose of our benchmarks was to verify whether reducing unnecessary parallel work could improve compression performance, particularly for small requests where worker preparation might account for a significant portion of the execution time. We also wanted to understand how the improvement changed as the amount of data increased, since an optimization that works well for small inputs may not provide the same benefit for larger workloads.

To make the comparison reproducible, we used a rainfall-grid sample as a reproducible source of real data, repeating its contents to test different input sizes and thread configurations. The rainfall data itself was not the target of the optimization; it simply provided a consistent input for comparing the original and modified implementations. The tests were performed under matched conditions, and the complete methodology and results are available in the [reproducibility repository](https://github.com/Johnny-Kao/c-blosc2-pr805-reproducibility).

![Performance comparison before and after PR #805](/images/pr805-threads/03-new-context.svg)

*Selected compression benchmarks using newly created contexts. Measurements include context setup and cleanup; lower is better.*

The most significant improvement appeared in small compression requests. With a **16 KiB input and sixteen configured threads**, the measured operation dropped from approximately **710 µs to 18 µs**, representing a speedup of nearly **39×**. This result illustrates how expensive unnecessary parallel preparation can become when there is too little work to distribute. By avoiding that preparation, the library can substantially reduce the cost of processing small requests without changing the compression algorithm itself.

The benefits were not uniform across all configurations. As the amount of data increased, more parallel work became available, and the relative advantage of avoiding startup overhead became smaller. Other tested configurations also showed more modest improvements or occasional regressions, reinforcing the importance of evaluating performance changes across different workloads rather than relying on a single favorable result.

## Why We Chose the Simpler Approach

During development, we explored more aggressive ways to reduce parallel overhead, including keeping worker threads ready between compression requests. Early experiments showed that some of these approaches could deliver even greater speedups. However, achieving the best performance in a particular benchmark was only one part of the challenge. More aggressive designs also introduced additional complexity in managing workers and their state, creating potential risks for existing behavior and future maintenance.

An optimization in a widely used library must work well beyond the specific workload it targets. Improvements for small compression requests should not come at the expense of larger workloads, and new mechanisms should remain understandable and maintainable for future contributors. This meant weighing the potential performance gains against the risk of regressions, implementation complexity, and the long-term cost of maintaining the code.

We ultimately chose a more focused approach: avoiding unnecessary worker startup and scheduling only the workers that could perform useful work. This delivered substantial improvements in the targeted cases without introducing a more complex worker-management system. Although further optimization opportunities remain, the goal was not to maximize a single benchmark result, but to achieve a meaningful performance improvement with a manageable engineering trade-off.

## Conclusion

The useful distinction is between **threads configured** and **blocks available to process**. PR #805 improves that match at two points: it skips parallel startup for one-block requests and avoids scheduling excess workers when only a few blocks exist. The rainfall fixture helped make the comparison reproducible, but the improvement applies to the shape of the compression request, not the subject of the data.

These changes were merged in [C-Blosc2 PR #805](https://github.com/Blosc/c-blosc2/pull/805). I would like to thank Francesc Alted and the Blosc maintainers for reviewing the contribution and helping keep the solution focused on avoiding unnecessary work.
