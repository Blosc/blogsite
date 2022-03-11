.. title: Announcing Support for Lossy ZFP Codec as a Plugin for C-Blosc2
.. author: Oscar Guiñon, Francesc Alted
.. slug: support-lossy-zfp
.. date: 2022-03-11 10:32:20 UTC
.. tags: blosc plugins zfp lossy
.. category:
.. link:
.. description:
.. type: text


Announcing Support for Lossy ZFP Codec as a Plugin for C-Blosc2
===============================================================

Blosc supports different filters and codecs for compressing data, like e.g. the lossless `NDLZ <https://github.com/Blosc/c-blosc2/tree/main/plugins/codecs/ndlz>`_ codec and the `NDCELL <https://github.com/Blosc/c-blosc2/tree/main/plugins/filters/ndcell>`_ filter.  These have been developed explicitly to be used in   multidimensional datasets (via `Caterva <https://github.com/Blosc/caterva/>`_ or `ironArray Community Edition <https://github.com/ironArray/iarray-community>`_).

However, a lossy codec like `ZFP <https://zfp.readthedocs.io/>`_ allows for much better compression ratios at the expense of loosing some precision in floating point data.  Moreover, while NDLZ is only available for 2-dim datasets, ZFP can be used up to 4-dim datasets.

How ZFP works?
--------------

ZFP partitions datasets into cells of 4^(number of dimensions) values, i.e., 4, 16, 64, or 256 values for 1D, 2D, 3D, and 4D arrays, respectively. Each cell is then (de)compressed independently, and the resulting bit strings are concatenated into a single stream of bits.

Furthermore, ZFP usually truncates each input value either to a fixed number of bits to meet a storage budget or to some variable length needed to meet a chosen error tolerance.  More more info on how this works, see `zfp overview docs <https://zfp.readthedocs.io/en/release0.5.5/overview.html>`_.

ZFP implementation
------------------

Similarly to other registered Blosc2 official plugins, this codec is now available at the `blosc2/plugins directory <https://github.com/Blosc/c-blosc2/tree/main/plugins/codecs/zfp>`_ of the `C-Blosc2 repository <https://github.com/Blosc/c-blosc2>`_.  However, as there are different modes for working with ZFP, there are different codec IDs that map each of these.

So, in order to use ZFP, users just have to choose the ID for the desired ZFP mode between the ones listed in `blosc2/codecs-registry.h <https://github.com/Blosc/c-blosc2/blob/main/include/blosc2/codecs-registry.h>`_. For more info on how the plugin selection machinery works, see https://www.blosc.org/posts/registering-plugins/.

ZFP modes
~~~~~~~~~

As ZFP is a lossy codec, but it still lets the user to choose how big this data loss is.  There are different compression modes:

- **BLOSC_CODEC_ZFP_FIXED_ACCURACY:** The user can choose the absolute error in truncation.  For example, if the desired absolute error is 0.01, each value loss must be less than or equal to 0.01. With that, if 23.0567 is a value of the original input, after compressing and decompressing this input with error=0.01, the new value must be between 23.0467 and 23.0667.
- **BLOSC_CODEC_ZFP_FIXED_PRECISION:** The user specifies the maximum number of bit planes encoded during compression (relative error). This is, for each input value, the number of most significant bits that will be encoded.
- **BLOSC_CODEC_ZFP_FIXED_RATE:** The user chooses the size that the compressed cells must have based on the input cell size. For example, if the cell size is 2000 bytes and user chooses ratio=50, the output cell size will be 50% of 2000 = 1000 bytes.

For more info, see: https://github.com/Blosc/c-blosc2/blob/main/plugins/codecs/zfp/README.md

Third partition
---------------

One of the most appealing features of Caterva besides supporting multi-dimensionality, is its implementation of a second partitioning schema, `making slicing more efficient <https://www.blosc.org/posts/caterva-slicing-perf/>`_.  As one of the distinctive characteristics of ZFP is that it compresses data in independent (and small) cells, we have been toying with the idea of implementing a third partition so that slicing or single-point selection can be made even faster.

So, as part of the current ZFP implementation, we have tried to combine Blosc2 machinery (chunking and blocking) with ZFP functions, allowing to extract single cells from the ZFP streams (blocks in Blosc jargon). Due to the properties and limitation of the different ZFP compression modes, we have been able to implement the third partition **only** for the *FIXED-RATE* mode.

At the moment we have implemented the next third-partition related functions:

- `blosc2_zfp_getcell()`: given a specific chunk and a specific block, the function allows users to decompress a chosen **cell** inside the block (ZFP stream).
- `blosc2_zfp_getitem()`: given a specific chunk and a specific block, the function allows to access the desired **item** from the block, decompressing only the cell that contains it instead of the whole block.

Of course, we could have been more ambitious and try to merge this third partition with the existing `blosc2_getitem_ctx() <https://c-blosc2.readthedocs.io/en/latest/reference/context.html?highlight=blosc_getitem#c.blosc2_getitem_ctx>`_ function for getting slices out of chunks in a general way, but as this would only work for a mode of the ZFP plugin, it won't be general enough, so we considered not a good idea to do it.  Having said this, using the above functions will still allow for a good improvement in speed for retrieving single items, or a cell-size amount of items.

Benchmark: ZFP FIXED-ACCURACY VS FIXED_PRECISION VS FIXED-RATE modes
--------------------------------------------------------------------

The dataset used in this benchmark is called *precipitation_amount_1hour_Accumulation.zarr* and has been fetched from `ERA5 database <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5>`_, which provides hourly estimates of a large number of atmospheric, land and oceanic climate variables.

Specifically, the downloaded dataset in Caterva format has this parameters:

- ndim = 3
- type = float32
- shape = [720, 721, 1440]
- chunkshape = [128, 128, 256]
- blockshape = [16, 32, 64]

The next plots represent the compression results obtained by using the different ZFP modes to compress the already mentioned dataset.

**Note:** It is important to remark that this is a specific dataset and the codec may perform differently for other ones.

.. image:: /images/zfp_plugin/ratio_zfp.png
  :width: 50%

.. image:: /images/zfp_plugin/times_zfp.png
  :width: 50%

Below the bars it is annotated what parameter is used for each test. For example, for the first column, the different compression modes are setup like this:

- FIXED-ACCURACY: for each input value, the absolute error is 10^(-6) = 0.000001.
- FIXED-PRECISION: for each input value, only the 20 most significant bits for the mantissa will be encoded.
- FIXED-RATE: the size of the output cells is 30% of the input cell size.

Although the FIXED-PRECISION mode does not obtain great results, we see that with the FIXED-ACCURACY mode we do get better performance as the absolute error increases.  Similarly, we can see how the FIXED-RATE mode gets the requested ratios, which is cool but, in exchange, the amount of data loss is unknown.

Also, while FIXED-ACCURACY and FIXED-RATE modes consume similar times, the FIXED-PRECISION mode, which seems to have less data loss, also takes longer to compress.  Generally speaking we can see how, the more data loss (more data truncation) achieved by a mode, the faster it operates.

Conclusions
-----------

The integration of ZFP as a codec plugin will greatly enhance the capabilities of lossy compression inside C-Blosc2.  The current ZFP plugin supports different modes; if users want to specify data loss during compression, it is recommended to use the FIXED-ACCURACY or FIXED-PRECISION modes (and most specially the former because of its better compression performance).

However, if the priority is to get good compression ratios without paying too much attention to the amount of data loss, one should use the FIXED-RATE mode, which let choose the desired compression ratio.  With that, ZFP will manage to achieve that storage budget.  This mode also has the advantage that the third partition can be used for improving slicing speed.

This work has been done thanks to a Small Development Grant from the `NumFOCUS Foundation <https://numfocus.org>`_, to whom we are very grateful indeed. NumFOCUS is doing a excellent job in sponsoring scientific projects and you can donate to the Blosc project (or many others under the NumFOCUS umbrella) via its `donation page <https://numfocus.org/support#donate>`_.
