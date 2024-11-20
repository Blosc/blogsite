.. title: Mastering Persistent, Dynamic Reductions and Lazy Expressions in Blosc2
.. author: Oumaima Ech Chdig, Francesc Alted
.. slug: persistent-reductions
.. date: 2024-11-05 12:58:20 UTC
.. tags: lazy-expressions, persistent-reduction, data-processing, large-datasets
.. category:
.. link:
.. description:
.. type: text


Working with large volumes of data is challenging, but Blosc2 offers unique tools to facilitate processing.

Blosc2 is a powerful data compression library designed to handle and process large datasets effectively. One standout feature is its support for **lazy expressions** and **persistent and dynamic reductions**. These tools make it possible to define complex calculations that execute only when necessary, reducing memory usage and optimizing processing time, which can be a game-changer when dealing with massive arrays.

In this guide, we’ll break down how to use these features to streamline data manipulation and get better performance out of your workflows. We’ll also see how resizing operand arrays is automatically reflected in the results, highlighting the flexibility of lazy expressions.

Getting Started with Arrays and Broadcasting
--------------------------------------------

Blosc2 works smoothly with arrays of various shapes and dimensions, enabling users to perform calculations such as addition or multiplication across arrays of different sizes. This is where **broadcasting** comes in. With broadcasting, Blosc2 automatically aligns the shapes of arrays for easy operations. This means you don’t need to manually adjust array dimensions to match, a huge time-saver when working with multidimensional data.

For example, let’s suppose we have an array representing a large dataset and, `a`, another representing a smaller dimension, `c`.

.. code-block:: python

    a = blosc2.full((1, 3, 2), fill_value=3)
    c = blosc2.full(2, fill_value=9, dtype=np.int8)
    expr = a + c - 1

As seen above, broadcasting works automatically (and efficiently) with arrays of compressed data.  Also, the correct data type of the result will be inferred from the operands and the expression. Thanks to this mechanism, the interpreter automatically adjusts the dimensions and data types of the arrays involved in the operation, allowing calculations to be performed without the need for manual adjustments.

.. image:: /images/blosc2-broadcast.png
  :width: 50%

This approach is ideal for quick and simple data analysis, especially when working with large volumes of information that require frequent operations across different dimensions.

Setting Up and Saving Lazy Expressions
--------------------------------------

Imagine you need to perform a calculation like `sum(a, axis=0) + b * sin(c)`. Rather than immediately calculating this, Blosc2’s **lazy expression** feature lets you store the expression for later. By using `blosc2.lazyexpr`, you define complex mathematical formulas and only trigger their execution when required, and only for the part of the resulting array that you are interested in. This is highly advantageous for large computations that might not be needed right away or that may depend on evolving data.

Let's see how that works with a little more complex expression:

.. code-block:: python
    # Create arrays with specific dimensions and values
    a = blosc2.full((2, 3, 4), 1, urlpath="a.b2nd", mode="w")
    b = blosc2.full((2, 4), 2, urlpath="b.b2nd", mode="w")
    c = blosc2.full(4, 3, dtype=np.uint8, urlpath="c.b2nd", mode="w")
    # Define a lazy expression and the operands for later execution
    # Note that we are using a string version of the expression here
    # so that it can be re-opened as-is later on
    expression = "sum(a, axis=0) + b * sin(c)"
    lazy_expression = blosc2.lazyexpr(expression)
    lazy_expression.save("arrayResult.b2nd", mode="w")

In this code, `sum(a, axis=0) + b * sin(c)` is defined but not executed immediately. When you’re ready to use the result, you can call `lazy_expression.compute()` (returns a Blosc2 array that is compressed by default) to run the calculation. Alternatively, you can specify the part of the result that you are interested in with `lazy_expression[0, :]` (returns a NumPy array). This way, you save CPU and memory and only perform the computation when necessary.

Dynamic Computation: Reusing and Updating Results
-------------------------------------------------

Another big advantage of Blosc2 is its ability to compute persistent expressions that are **dynamic**: when an operand is enlarged, Blosc2 re-adapts the expression to account for its new shape. This approach significantly speeds up processing time, especially when working with frequently updated or real-time data.

For instance, if you have an expression stored, and only part of your dataset changes, Blosc2 can apply reductions dynamically to efficiently update the sum:

.. code-block:: python
    # Resizing arrays and updating values
    a.resize((30, 30, 40))
    a[20:30] = 5
    b.resize((30, 40))
    b[20:30] = 7
    # Open the saved file
    lazy_expression = blosc2.open(urlpath=url_path)
    result = lazy_expression.compute()

In this case, the final `result` will have a shape of `(30, 40)` (instead of the previous `(20, 40)`). This allows for quick adaptability, which is crucial in data environments where values evolve constantly.

Why Persistent Reductions and Lazy Expressions Matter
-----------------------------------------------------

These features make Blosc2 a top choice for working with large datasets, as they allow for:

- **Broadcasting** of memory, on-disk or network operands.
- **Efficient use of CPU and memory** by only executing calculations when needed.
- **Dynamic expressions** that adapt to changing data in operands.
- **Enhanced performance** due to streamlined, multi-threaded and pre-fetched calculations.

Together, lazy expressions and persistent reductions provide a flexible, resource-efficient way to manage complex data processes. They’re perfect for real-time analysis, evolving datasets, or any high-performance computing tasks requiring dynamic data handling.

Conclusion
----------

Blosc2’s features offer a way to make data processing smarter and faster. If you work with large arrays or require adaptable workflows, Blosc2 can help you make the most of your data processing resources.

For more in-depth guidance, visit the `full tutorial on Blosc2 <https://www.blosc.org/python-blosc2/getting_started/tutorials/04.persistent-reductions.html>`_.
