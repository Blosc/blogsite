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

    # Create a new TreeStore in write mode ('w')
    with blosc2.TreeStore("my_experiment.b2z", mode="w") as ts:
        # You can store numpy arrays, which are converted to blosc2.NDArray
        ts["/group1/dataset1"] = np.arange(100)

        # You can also store blosc2 arrays directly
        ts["/group1/dataset2"] = blosc2.full((5, 5), fill_value=3.14)

        # And external arrays with vlmeta attached (these are included internally too)
        ext = blosc2.zeros((10,), urlpath="external_array.b2nd", mode="w")
        ext.vlmeta["desc"] = "included array metadata"
        ts["/group1/included_array"] = ext

        # Create another group with a dataset
        ts["/group2/another_dataset"] = blosc2.zeros((10,))

In this example, we created a ``TreeStore`` in a file named ``my_experiment.b2z``. It contains two groups, ``group1`` and ``group2``, each holding datasets.

Reading from a TreeStore
------------------------

To access the data, you open the ``TreeStore`` in read mode (``'r'``) and use the same path-like keys to retrieve your arrays.

.. code-block:: python

    # Open the TreeStore in read mode ('r')
    with blosc2.TreeStore("my_experiment.b2z", mode="r") as ts:
        # Access a dataset
        dataset1 = ts["/group1/dataset1"]
        print("Dataset 1:", dataset1[:])  # Use [:] to decompress and get a NumPy array

        # Access the external array that has been included internally
        ext_array = ts["/group1/included_array"]
        print("Included array:", ext_array[:])
        print("Included array metadata:", ext_array.vlmeta[:])

        # List all paths in the store
        print("Paths in TreeStore:", list(ts))

Advanced Usage: Metadata and Subtrees
-------------------------------------

``TreeStore`` becomes even more powerful when you use metadata and interact with subtrees (groups).

Storing Metadata with ``vlmeta``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can attach variable-length metadata (``vlmeta``) to any group or to the root of the tree. This is useful for storing information like author names, dates, or experiment parameters. ``vlmeta`` is essentially a dictionary where you can store your metadata.

.. code-block:: python

    with blosc2.TreeStore("my_experiment.b2z", mode="a") as ts: # 'a' for append/modify
        # Add metadata to the root
        ts.vlmeta["author"] = "The Blosc Team"
        ts.vlmeta["date"] = "2025-07-10"

        # Add metadata to a group
        ts["/group1"].vlmeta["description"] = "Data from the first run"

    # Reading metadata
    with blosc2.TreeStore("my_experiment.b2z", mode="r") as ts:
        print("Root metadata:", ts.vlmeta[:])
        print("Group 1 metadata:", ts["/group1"].vlmeta[:])

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

Iterating Through a TreeStore
-----------------------------

You can easily iterate through all the nodes in a ``TreeStore`` to inspect its contents.

.. code-block:: python

    with blosc2.TreeStore("my_experiment.b2z", mode="r") as ts:
        for path, node in ts.items():
            if isinstance(node, blosc2.NDArray):
                print(f"Found dataset at '{path}' with shape {node.shape}")
            else: # It's a group
                print(f"Found group at '{path}' with metadata: {node.vlmeta[:]}")

Some Benchmarks
---------------

``TreeStore`` is based on powerful abstractions from the ``blosc2`` library, so it is very fast. Here are some benchmarks comparing ``TreeStore`` to other data storage formats, like HDF5 and Zarr.

Conclusion
----------

``blosc2.TreeStore`` provides a simple yet powerful way to organize compressed datasets hierarchically. By combining the high-performance compression of ``blosc2.NDArray`` with a flexible, filesystem-like structure and metadata support, ``TreeStore`` is an excellent choice for managing complex data projects.
