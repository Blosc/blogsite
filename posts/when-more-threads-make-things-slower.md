<!--
.. title: When More Threads Make Things Slower
.. slug: when-more-threads-make-things-slower
.. date: 2026-10-12 13:00:00 UTC
.. tags: blosc2, compression, performance, threading
.. category: posts
.. link:
.. description: How a small C-Blosc2 change made tiny compression jobs much faster by avoiding unnecessary parallel work.
.. type: text
.. author: Johnny Kao
-->

*How a small change in C-Blosc2 made tiny compression jobs dramatically faster—without changing how the data was compressed.*

Imagine walking into a restaurant and ordering a sandwich.

Instead of making it, the chef calls fifteen colleagues into the kitchen. Everyone gets ready, finds a place to stand, and waits for instructions.

By the time they're organized, the sandwich could already be on your table.

It sounds ridiculous. But something surprisingly similar can happen inside a computer.

We tend to think that more workers mean faster results. And often, that's true. Give a big job to several people, and they can finish it together. But when the job is small, organizing everyone can take longer than doing the work.

I came across this while working on [C-Blosc2](https://github.com/Blosc/c-blosc2), an open-source library that helps computers compress data.

In one of our tests, a small compression request took about **710 microseconds**. After a relatively simple change, it took just **18 microseconds**.

That's almost **39 times faster**.

The surprising part? We didn't make the compression itself any faster.

We simply stopped doing some of the work that came before it.

<!-- TEASER_END -->

## The Hidden Cost of Getting Ready

Before a computer can finish a job, it often needs to do a little preparation.

Think about cooking dinner. You get the ingredients out, find a knife, and prepare your workspace. If you're making dinner for twenty people, those few minutes hardly matter.

But what if you're just cutting an apple?

Suddenly, the preparation might take longer than the task itself.

Compression has a similar problem.

When there's a lot of data, C-Blosc2 can split it into smaller pieces and let several workers handle them at the same time. That makes sense. There's enough work to keep everyone busy.

But some compression requests are tiny. There may be only one piece of data to process, even when the application has asked for sixteen workers.

And that's where we found something interesting.

The library could start preparing those workers before checking whether they were actually needed.

Imagine getting sixteen people ready to move a single box.

There's nothing wrong with the people. There's nothing wrong with the box. The problem is that most of the preparation was unnecessary.

Once we understood that, the question changed.

Instead of asking how to make compression faster, we started asking why the computer was spending so much time getting ready.

## What If We Simply Did Less?

The answer turned out to be surprisingly straightforward.

Before preparing extra workers, C-Blosc2 could first check how much work there was.

If there was only one piece to process, it could simply get on with the job.

No extra team. No unnecessary preparation.

![Before and after: a single-block job skips unnecessary parallel startup](/images/pr805-threads/01-startup.svg)

*When there's only one piece of work, there's no need to get a whole team ready.*

There was a second opportunity, too.

Suppose we have three pieces of data and sixteen workers available.

Previously, C-Blosc2 could prepare work for all sixteen workers, even though only three could be useful. The others had nothing to do.

So we changed that as well.

Now, when only three workers are needed, the library can assign work to three and leave the others alone.

![Workers assigned before and after PR #805](/images/pr805-threads/02-workers.svg)

*Sixteen available workers, three pieces of work—only three workers need assignments.*

Neither change required a new compression algorithm.

We didn't ask the computer to process information differently. We just helped it make a better decision about how much preparation was worth doing.

The actual changes were quite small. But small changes can matter a lot when they remove work that happens over and over again.

## Where It Made a Difference

Of course, an idea that sounds sensible isn't necessarily an improvement.

We needed to measure it.

So we compared the original version of C-Blosc2 with our modified version, running both on the same Linux machine with the same data and settings.

We were particularly interested in small requests, where getting ready could take a large share of the total time.

And that's where the difference was remarkable.

![Before and after with newly created compression contexts](/images/pr805-threads/03-new-context.svg)

*Time per request when a fresh workspace is created each time. Shorter bars mean less waiting.*

For a request containing just **16 KiB** of data, with sixteen workers configured, the time dropped from about **710 microseconds** to **18 microseconds**.

Nearly 39 times faster.

With four workers configured, the same-sized request became more than ten times faster.

But here's something equally important: **the improvement wasn't nearly as dramatic for larger jobs.**

Why?

Because when there's plenty of real work to do, the time spent getting ready becomes a much smaller part of the overall task.

Think back to the restaurant. Calling sixteen chefs to make one sandwich is excessive. Calling sixteen chefs to prepare dinner for two hundred guests is a different story.

The value of having more workers depends on how much work there is.

We also tested situations where the computer could reuse its preparation between requests. In those cases, the results varied more. Some jobs became faster, others saw little benefit, and a few were slower.

![Before and after with reused compression contexts](/images/pr805-threads/04-reused-context.svg)

*Results when the compression workspace is reused. The benefit varies with the workload; the chart shows three selected configurations.*

That's a useful reminder that performance improvements are rarely universal. There's still room to improve how different workloads are handled.

These were focused tests, not measurements of an entire application. We used a rainfall-data sample, repeated to create larger inputs, and compared the two versions under the same conditions. The [benchmark code and results are public](https://github.com/Johnny-Kao/c-blosc2-pr805-reproducibility) for anyone who wants to explore them. You can also see the [successful GitHub Actions run](https://github.com/Johnny-Kao/c-blosc2-pr805-reproducibility/actions/runs/37950149167).

## Why We Chose the Simpler Fix

There's another part of this story worth sharing.

The solution we eventually used wasn't actually our first idea.

When I initially noticed how expensive the preparation could be, I thought: why not keep the workers ready between requests?

That way, we wouldn't have to organize a new team every time.

I tried it, and the early results were excellent. An operation that had taken around **40 microseconds** could finish in roughly **2**.

But keeping resources around also meant taking care of them in more situations.

For example, some programs create a new process by copying part of an existing one. The new process might inherit information about the waiting workers without inheriting the workers themselves.

In our tests, that could leave the new process waiting for someone who was no longer there.

We found a way to handle the problem, but the solution was becoming more complicated.

And that brought us back to a basic question.

Did we really need to keep workers waiting?

Or could we simply avoid calling them when they weren't needed?

The second answer was much easier to live with.

It improved the situations we cared about most, without introducing a new system for keeping unused workers around.

There was also an important practical detail: not every operating system manages this work in exactly the same way. During testing, we kept the existing startup behavior on Windows rather than introducing a change that caused compatibility problems.

After all, saving time isn't much of an improvement if something else stops working.

## Sometimes the Best Optimization Is Doing Nothing

I started this work thinking that C-Blosc2 needed a faster way to prepare its workers.

What we eventually discovered was that, sometimes, it didn't need to prepare them at all.

That difference might sound small, but it changed the solution completely.

Instead of making an expensive step faster, we removed that step when it served no purpose.

The result became [C-Blosc2 PR #805](https://github.com/Blosc/c-blosc2/pull/805), which was merged into the project.

I'm grateful to Francesc Alted and the Blosc maintainers for reviewing the contribution and helping make the final change safer and clearer.

And there's a lesson here that goes well beyond compression.

When something is slow, our first instinct is often to make it work harder, add more resources, or find a faster way to perform each step.

But sometimes the better question is much simpler:

*Does this step need to happen at all?*

Because sometimes, the fastest work is the work you never start.
