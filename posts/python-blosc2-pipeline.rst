.. title: User Defined Pipeline for Python-Blosc2
.. author: Marta Iborra
.. slug: python-blosc2-pipeline
.. date: 2022-12-15 8:00:20 UTC
.. tags: blosc2 python user-defined filters codecs
.. category:
.. link:
.. description:
.. type: text


The Blosc Development Team is happy to announce that the latest version of  `Python-Blosc2 <https://github.com/Blosc/python-blosc2>`_ supports the creation by the user of all the functions that can participate in its pipeline: prefilters, postfilters, filters and codecs.

The Blosc2 pipeline
-------------------

The Blosc2 pipeline includes all the functions that are applied to the data until it is finally compressed. It has one way for compression and another for decompression. As can be seen in the image below, when compressing the first function to apply the data to is the prefilter (if any), then the filters pipeline with a maximum of six filters and, last but not least, the codec. For decompressing, the order will be the other way around: first the codec, then the filters pipeline and finally the postfilter (if any).

.. image:: /images/blosc2-pipeline/blosc2-pipeline.png
  :width: 50%
  :alt: blosc2-pipeline
  :align: center

In previous versions of Python-Blosc2, we did not have the ability to define a prefilter nor a postfilter and the only filters and codecs that could be used were those predefined in C-Blosc2. But now, Python-Blosc2 has the ability to build the entire pipeline out of pure Python functions.

Defining prefilters and postfilters
-----------------------------------

As already seen, a prefilter is a function related to a SChunk that is applied to the data each time you compress it (when appending or updating). This function is executed for each block and receives three parameters: input, output and offset. The input and output are NumPy arrays. The first one contains the corresponding block of data to apply the function to and the second one is empty and must be filled by the prefilter. This last one is what the first filter in the filters pipeline will receive. Regarding the offset, it is an integer which indicates where the corresponding block begins inside the SChunk.

Because a prefilter is always set to a SChunk instance, you can set it to the specific SChunk with the easy to use decorator::

    schunk = blosc2.SChunk()
    @schunk.prefilter(np.int64, np.float64)
    def pref(input, output, offset):
        output[:] = input - np.pi + offset

This decorator receives the data types of the input (original data) and output NumPy arrays, which must be of same itemsize.

If you do not want the prefilter to be applied anymore, you can always remove it::

    schunk.remove_prefilter("pref")

As for the postfilters, they are applied at the end of the pipeline during decompression. This function receives the same parameters as the prefilter and can be set very similarly::

    @schunk.postfilter(np.float64, np.int64)
    def postf(input, output, offset):
        output[:] = input + np.pi - offset

In this case, the input data type is the one from the buffer returned by the filter pipeline, and the output data type should be the one of the original data. Similarly to the prefilters, you can also remove them whenever you want::

    schunk.remove_postfilter("postf")

Fillers
^^^^^^^

Before we move onto the next step in the pipeline, we need to talk about the fillers. A filler is a prefilter but with a twist. It is used to fill an empty SChunk and you can pass to it any extra parameter you would like to use as long as it is a NumPy array, SChunk or Python Scalar. All these extra parameters will be passed as a tuple containing only the corresponding block slice for each parameter (except for the scalars). To set it, you will have to pass the inputs along with its data type::

    @schunk.filler(((schunk0, dtype0), (ndarray1, dtype1), (py_scalar3, dtype2)), schunk_dtype)
    def filler(inputs_tuple, output, offset):
        output[:] = inputs_tuple[0] - inputs_tuple[1] * inputs_tuple[2]

And it automatically will append the data to the SChunk applying the filler function. After that, the filler will be removed and the next time you update some data the it would not be executed. In the case of the fillers, the data types of the different objects involved do not have to be of same itemsize.

User-defined filters and codecs
-------------------------------

The main difference between prefilters/postfilters and filters/codecs is that the first ones are defined for an specific SChunk instance, whereas the second ones can be locally registered and used in any SChunk.

Following with the compression process order, we will first begin with the filters. A filter is composed by two functions: one for the compression process (*forward*), and another one for the decompression process (*backward*). These functions receive the input and output to fill as uint8 NumPy arrays, the filter meta and the SChunk instance to which the block in particular belongs. The *forward* function will fill the output with the modified data from input. The *backward* will take care of undoing the changes done by *forward* so that the data returned at the end of the decompression is the same as the one received at the beginning of the compression. Find below a drawing explaining that.

.. image:: /images/blosc2-pipeline/forward.png
  :width: 35%
  :alt: forward

.. image:: /images/blosc2-pipeline/backward.png
  :width: 35%
  :alt: backward

Once this pair of functions is defined, it can be registered locally associating an id between 160 and 255::

    blosc2.register_filter(id, forward, backward)

And use it in any SChunk assigning its id in the filters pipeline::

    schunk.cparams = {"filters": [id], "filters_meta": [meta]}

Regarding the codecs, there are not many differences from the creation and definition of filters. The only one is that, because their goal is to actually compress data, the corresponding functions (*encoder* and *decoder*) will have to return the size in bytes of the compressed/decompressed data respectively. This time the scheme would be:

.. image:: /images/blosc2-pipeline/encoder.png
  :width: 45%
  :alt: encoder

.. image:: /images/blosc2-pipeline/decoder.png
  :width: 45%
  :alt: decoder

To register it, you will use a similar function adding also the name of the codec::

    blosc2.register_codec(codec_name, id, encoder, decoder)

And to use it you will use its id in the cparams::

    schunk.cparams = {"codec": id, "codec_meta": meta}

Final thoughts
--------------

So now, you can define filters and codecs working with just NumPy arrays as the input and output buffers from each step in the pipeline.

See more examples in the `repository <https://github.com/Blosc/python-blosc2/tree/main/examples>`_.

Finally, you can find the complete documentation at: https://www.blosc.org/python-blosc2/python-blosc2.html.

This work has been made thanks to a Small Development Grant from `NumFOCUS <https://numfocus.org>`_.
NumFOCUS is a non-profit organization supporting open code for better science.  If you like this, consider giving a donation to them (and if you like our work, you can nominate it to our project too!).
