.. title: TreeStore: Endowing Your Data With Hierarchical Structure
.. author: Francesc Alted
.. slug: new-treestore-blosc2
.. date: 2025-08-17 10:33:20 UTC
.. tags: treestore hierarchical structure performance
.. category:
.. link:
.. description:
.. type: text


When working with large and complex datasets, having a way to organize your data efficiently is crucial. ``blosc2.TreeStore`` is a powerful feature in the ``blosc2`` library that allows you to store and manage your compressed arrays in a hierarchical, tree-like structure, much like a filesystem. This container, typically saved with a ``.b2z`` extension, can hold not only ``blosc2.NDArray`` or ``blosc2.SChunk`` objects but also metadata, making it a versatile tool for data organization.

What is a TreeStore?
--------------------

A ``TreeStore`` lets you arrange your data into groups (like directories) and datasets (like files). Each dataset is a ``blosc2.NDArray`` or ``blosc2.SChunk`` instance, benefiting from Blosc2's high-performance compression. This structure is ideal for scenarios where data has a natural hierarchy, such as in scientific experiments, simulations, or any project with multiple related datasets.

Basic Usage: Creating and Populating a TreeStore
-------------------------------------------------

Creating a ``TreeStore`` is straightforward. You can use a ``with`` statement to ensure the store is properly managed. Inside the ``with`` block, you can create groups and datasets using a path-like syntax.

.. code-block:: python

    import blosc2
    import numpy as np

    # Create a new TreeStore
    with blosc2.TreeStore("my_experiment.b2z", mode="w") as ts:
        # You can store numpy arrays, which are converted to blosc2.NDArray
        ts["/dataset0"] = np.arange(100)

        # Create a group with a dataset that can be a blosc2 NDArray
        ts["/group1/dataset1"] = blosc2.zeros((10,))

        # You can also store blosc2 arrays directly (vlmeta included)
        ext = blosc2.linspace(0, 1, 10_000, dtype=np.float32)
        ext.vlmeta["desc"] = "dataset2 metadata"
        ts["/group1/dataset2"] = ext

In this example, we created a ``TreeStore`` in a file named ``my_experiment.b2z``.

.. image:: /images/new-treestore-blosc2/tree-store-blog.png

It contains two groups, ``root`` and ``group1``, each holding datasets.

Reading from a TreeStore
------------------------

To access the data, you open the ``TreeStore`` in read mode (``'r'``) and use the same path-like keys to retrieve your arrays.

.. code-block:: python

    # Open the TreeStore in read-only mode ('r')
    with blosc2.TreeStore("my_experiment.b2z", mode="r") as ts:
        # Access a dataset
        dataset1 = ts["/group1/dataset1"]
        print("Dataset 1:", dataset1[:])  # Use [:] to decompress and get a NumPy array

        # Access the external array that has been stored internally
        dataset2 = ts["/group1/dataset2"]
        print("Dataset 2", dataset2[:])
        print("Dataset 2 metadata:", dataset2.vlmeta[:])

        # List all paths in the store
        print("Paths in TreeStore:", list(ts))

.. code-block:: text

    Dataset 1: [0 1 2 3 4 5 6 7 8 9]
    Dataset 2 [0.0000000e+00 1.0001000e-04 2.0002000e-04 ... 9.9979997e-01 9.9989998e-01
     1.0000000e+00]
    Dataset 2 metadata: {b'desc': 'dataset2 metadata'}
    Paths in TreeStore: ['/group1/dataset2', '/group2', '/group1', '/group2/another_dataset', '/group1/dataset1']

Advanced Usage: Metadata and Subtrees
-------------------------------------

``TreeStore`` becomes even more powerful when you use metadata and interact with subtrees (groups).

Storing Metadata with ``vlmeta``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can attach variable-length metadata (``vlmeta``) to any group or to the root of the tree. This is useful for storing information like author names, dates, or experiment parameters. ``vlmeta`` is essentially a dictionary where you can store your metadata.

.. code-block:: python

    # Appending metadata to the TreeStore
    with blosc2.TreeStore("my_experiment.b2z", mode="a") as ts:  # 'a' for append/modify
        # Add metadata to the root
        ts.vlmeta["author"] = "The Blosc Team"
        ts.vlmeta["date"] = "2025-08-17"

        # Add metadata to a group
        ts["/group1"].vlmeta["description"] = "Data from the first run"

    # Reading metadata
    with blosc2.TreeStore("my_experiment.b2z", mode="r") as ts:
        print("Root metadata:", ts.vlmeta[:])
        print("Group 1 metadata:", ts["/group1"].vlmeta[:])

.. code-block:: text

    Root metadata: {'author': 'The Blosc Team', 'date': '2025-08-17'}
    Group 1 metadata: {'description': 'Data from the first run'}

Working with Subtrees (Groups)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can get a group object from the ``TreeStore`` and work with it as if it were a smaller, self-contained ``TreeStore``. This is useful for modularizing your data access code.

.. code-block:: python

    with blosc2.TreeStore("my_experiment.b2z", mode="r") as ts:
        # Get the group as a subtree
        group1 = ts["/group1"]

        # Now you can access datasets relative to this group
        dataset2 = group1["dataset2"]
        print("Dataset 2 from group object:", dataset2[:])

        # You can also list contents relative to the group
        print("Contents of group1:", list(group1))

.. code-block:: text

    Dataset 2 from group object: [0.0000000e+00 1.0001000e-04 2.0002000e-04 ... 9.9979997e-01 9.9989998e-01
     1.0000000e+00]
    Contents of group1: ['/dataset2', '/dataset1']

Iterating Through a TreeStore
-----------------------------

You can easily iterate through all the nodes in a ``TreeStore`` to inspect its contents.

.. code-block:: python

    with blosc2.TreeStore("my_experiment.b2z", mode="r") as ts:
        for path, node in ts.items():
            if isinstance(node, blosc2.NDArray):
                print(f"Found dataset at '{path}' with shape {node.shape}")
            else:  # It's a group
                print(f"Found group at '{path}' with metadata: {node.vlmeta[:]}")

.. code-block:: text

    Found dataset at '/group1/dataset2' with shape (10000,)
    Found group at '/group1' with metadata: {'description': 'Data from the first run'}
    Found dataset at '/group1/dataset1' with shape (10,)
    Found dataset at '/dataset0' with shape (100,)

That's it for this introduction to ``blosc2.TreeStore``! You now know how to create, read, and manipulate a hierarchical data structure that can hold compressed datasets and metadata. You can find the source code for this example in the `blosc2 repository <https://github.com/Blosc/python-blosc2/blob/main/examples/tree-store-blog.py>`_.

Some Benchmarks
---------------

``TreeStore`` is based on powerful abstractions from the ``blosc2`` library, so it is very fast. Here are some benchmarks comparing ``TreeStore`` to other data storage formats, like HDF5 and Zarr. We have used two different configurations: one with small arrays, where sizes follow a gaussian distribution centered at 10 MB each, and the other with larger arrays, where sizes follow a gaussian distribution centered at 1 GB each. We have compared the performance of ``TreeStore`` against HDF5 and Zarr for both small and large arrays, measuring the time taken to create and read datasets.  For comparing apples with apples, we have used the same compression codec (``zstd``) and filter (``shuffle``) for all three formats.

For assessing different platforms, we have used a desktop with an Intel i9-13900K CPU and 32 GB of RAM, running Ubuntu 25.04, and also a Mac mini with an Apple M4 Pro processor and 24 GB of RAM. The benchmarks were run using the `blosc2-benchmarks repository <https://github.com/Blosc/python-blosc2/blob/main/bench/large-tree-store.py>`_.

Results for the Intel i9-13900K desktop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /images/new-treestore-blosc2/benchmark_comparison_b2z-i13900K-10M.png

For the small arrays scenario, we can see that ``TreeStore`` is the fastest to create datasets (due to use of multi-threading), but it is slower than HDF5 and Zarr when reading datasets.  The reason for this is two-fold: first, ``TreeStore`` is designed to work using multi-threading, so it must setup the necessary threads at the beginning of the read operation, which takes some time; second, ``TreeStore`` is using NDArray objects internally, which are using a double partitioning scheme (chunks and blocks) to store the data, which adds some overhead when reading small slices of data. Regarding the space used, ``TreeStore`` is the most efficient, very close to HDF5, and significantly more efficient than Zarr, which is using quite a lot of space.

.. image:: /images/new-treestore-blosc2/benchmark_comparison_b2z-i13900K-1G.png

For the larger arrays scenario, ``TreeStore`` is again the fastest to create datasets, and it is also the fastest to read complete datasets. However, access time is still slower than HDF5 and Zarr when reading small slices of data. The space used is also the least, followed by HDF5, and Zarr is still the most inefficient in this regard.


Results for the Apple M4 Pro Mac mini
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the small arrays scenario.

.. image:: /images/new-treestore-blosc2/benchmark_comparison_b2z-MacM4-10M.png

For the large arrays scenario.

.. image:: /images/new-treestore-blosc2/benchmark_comparison_b2z-MacM4-1G.png

As before, ``TreeStore`` requires the least amount of space to store the data, and it is also the fastest to create and read datasets, especially for larger arrays.  The only metric where ``TreeStore`` is not the fastest is when reading small slices of data (access time), where it is significantly slower than HDF5 and Zarr.

In general, it is pretty interesting to see that the Mac mini with the Apple M4 Pro processor is able to be competitive with the Intel i9-13900K CPU, which is a high-end desktop processor, consuming up to 8x more power than the M4 Pro. This is a testament to the efficiency of the ARM architecture in general and Apple silicon in particular.

Conclusion
----------

``blosc2.TreeStore`` provides a simple yet powerful way to organize compressed datasets hierarchically. By combining the high-performance compression of ``blosc2.NDArray`` with a flexible, filesystem-like structure and metadata support, ``TreeStore`` is an excellent choice for managing complex data projects.  ``TreeStore`` is still in beta, so we welcome any feedback or suggestions for improvement.  You can find more information on the documentation page for `blosc2.TreeStore <https://www.blosc.org/python-blosc2/reference/tree_store.html#blosc2.TreeStore>`_.
