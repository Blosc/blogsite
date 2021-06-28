.. title:  Registering plugins in C-Blosc2
.. author: Oscar Griñón
.. slug: registering-plugins
.. date: 2021-06-28 10:32:20 UTC
.. tags: blosc plugins codecs filters
.. category:
.. link:
.. description:
.. type: text


Blosc has traditionally supported different filters and codecs for compressing data,
and it was up to the user to choose one or another depending on her needs.
However, there will always be scenarios where a more richer variety of them could be useful.

Blosc2 has now a new plugin register capability in place so that the info about the new filters and codecs can be persisted and transmitted to different machines.
In this way Blosc can figure out the info of persistent plugins, and use them so as to decompress the data without problems.

Besides, the Blosc Development Team has implemented a centralized repository so that people can propose new plugins; and if these plugins fulfill a series of requirements, they will be officially accepted, and distributed *within* the C-Blosc2 library.  This provides an easy path for extending C-Blosc2 and hence, better adapt to user needs.

The plugins that can be registered in the repository can be either codecs or filters.

- A **codec** is a program able to compress and decompress a data stream with the objective of reducing its size and to enable a faster transmission of data.

- A **filter** is a program that reorders the data without changing its size, so that the initial and final size are equal. A filter consists of encoder and decoder.
  The filter encoder is applied before the codec compressor (or codec encoder) in order to make data easier to compress
  and the filter decoder is used after codec decompressor (or codec decoder) to restore the original data arrangement.

Here it is an example on how the compression process goes:

.. code-block:: console

    --------------------   filter encoder  -------------------   codec encoder   -------
    |        src        |   ----------->  |        tmp        |   ---------->   | c_src |
    --------------------                   -------------------                   -------

And the decompression process:

.. code-block:: console

    --------   codec decoder    -------------------   filter decoder  -------------------
    | c_src |   ----------->   |        tmp        |   ---------->   |        src        |
    --------                    -------------------                   -------------------



Register for user plugins
=========================

**User registered plugins** are plugins that users register locally so that they can be used in the same way as Blosc official codecs and filters.
This option is perfect for users that want to try new filters or codecs on their own.

The register process is quite simple.  You just use the ``blosc2_register_filter()`` or ``blosc2_register_codec()`` function and then the Blosc2 machinery
will store its info with the rest of plugins. After that you will be able to access your plugin through its ID by setting Blosc2 compression or decompression
params.

.. code-block:: console

                                               filters pipeline
                                            ----------------------
                                           |  BLOSC_SHUFFLE     1 |
                                            ----------------------
                                           |  BLOSC_BITSHUFFLE  2 |
                                            ----------------------
                                           |  BLOSC_DELTA       3 |
                                            ----------------------
                                           |  BLOSC_TRUNC       4 |
                                            ----------------------
                                           |         ...          |
                                            ----------------------
                                           |  BLOSC_NDCELL     32 |
                                            ----------------------
                                           |  BLOSC_NDMEAN     33 |
                                            ----------------------
                                           |         ...          |
                                            ----------------------
                                           |  urfilter1       160 |
                                            ----------------------
  blosc2_register_filter(urfilter2)  --->  |  urfilter2       161 |  ---> cparams.filters[4] = 161; // can be used now
                                            ----------------------
                                           |         ...          |
                                            ----------------------


Global register for Blosc plugins
=================================

**Blosc global registered plugins** are Blosc plugins that have passed through a selection process and a review by the Blosc Development Team.
These plugins will be available for everybody using the C-Blosc2 library.

You should consider this option if you think that your codec or filter could be useful for the community, or you just want being able to use
them with upstream C-Blosc2 library.  The steps for registering an official Blosc plugin can be seen at:
https://github.com/Blosc/c-blosc2/blob/main/plugins/README.md

Some well documented examples of these kind of plugins are the codec ``ndlz`` and the filters ``ndcell`` and ``ndmean`` on the C-Blosc2 GitHub repository:
https://github.com/Blosc/c-blosc2/tree/main/plugins


Compiling plugins examples using Blosc2 wheels
==============================================

So as to easy the use of the registered filters, full-fledged C-Blosc2 binary libraries including plugins functionality can be installed from
python-blosc2 (>= 0.1.8) wheels:

.. code-block:: console

        $ pip install blosc2
	Collecting blosc2
          Downloading blosc2-0.1.8-cp37-cp37m-manylinux2010_x86_64.whl (3.3 MB)
             |████████████████████████████████| 3.3 MB 4.7 MB/s
        Installing collected packages: blosc2
        Successfully installed blosc2-0.1.8


Once you have installed the C-Blosc2 libraries you can not only use the official Blosc filters and codecs, but you can also register and use them.
You can find directions on how to compile C files using the Blosc2 libraries inside these wheels at:
https://github.com/Blosc/c-blosc2/blob/main/COMPILING_WITH_WHEELS.rst


Using user plugins
------------------

To use your own plugins with the Blosc machinery you first have to register them through the function ``blosc2_register_codec()`` or ``blosc2_register_filter()``
with an ID between ``BLOSC2_USER_DEFINED_FILTERS_START`` and ``BLOSC2_USER_DEFINED_FILTERS_STOP``. Then you can use this ID in the compression parameters (`cparams.compcode`, `cparams.filters`) and decompression parameters (`dparams.compcode`, `dparams.filters`).
For any doubts you can see the whole process in the examples `urcodecs.c <https://github.com/Blosc/c-blosc2/blob/main/examples/urcodecs.c>`_ and `urfilters.c <https://github.com/Blosc/c-blosc2/blob/main/examples/urfilters.c>`_.

.. code-block:: C

  blosc2_codec urcodec;
  udcodec.compcode = 244;
  udcodec.compver = 1;
  udcodec.complib = 1;
  udcodec.compname = "urcodec";
  udcodec.encoder = codec_encoder;
  udcodec.decoder = codec_decoder;
  blosc2_register_codec(&urcodec);

  blosc2_cparams cparams = BLOSC2_CPARAMS_DEFAULTS;
  cparams.compcode = 244;


Using Blosc official plugins
----------------------------

To use the Blosc official plugins it is mandatory to add the next lines in order to activate the plugins mechanism:

- ``#include "blosc2/codecs-registery.h"`` or ``#include "blosc2/filters-registery.h"`` depending on the plugin type at the beginning of the file

- ``#include "blosc2/blosc2.h"`` at the beginning of the file

- Call ``blosc_init()`` at the beginning of main() function

- Call ``blosc_destroy()`` at the end of main() function

Then you just have to use the ID of the plugin that you want to use in the compression parameters (``cparams.compcode``).

.. code-block:: C

  #include "blosc2.h"
  #include "../codecs-registry.h"
  int main(void) {
      blosc_init();
      ...
      blosc2_cparams cparams = BLOSC2_CPARAMS_DEFAULTS;
      cparams.compcode = BLOSC_CODEC_NDLZ;
      cparams.compcode_meta = 4;
      ...
      blosc_destroy();
  }

In case of doubts, you can see how the whole process works in working tests like:
`test_ndlz.c <https://github.com/Blosc/c-blosc2/blob/main/plugins/codecs/ndlz/test_ndlz.c>`_,
`test_ndcell.c <https://github.com/Blosc/c-blosc2/blob/main/plugins/filters/ndcell/test_ndcell.c>`_,
`test_ndmean_mean.c <https://github.com/Blosc/c-blosc2/blob/main/plugins/filters/ndmean/test_ndmean_mean.c>`_ and
`test_ndmean_repart.c <https://github.com/Blosc/c-blosc2/blob/main/plugins/filters/ndmean/test_ndmean_repart.c>`_.


Final remarks
=============

The plugin register functionality let use new codecs and filters within Blosc in an easy and quick way. To enhance the plugin experience, we
have implemented a centralized plugin repository, so that users can propose their own plugins to be in the standard C-Blosc2 library for
the benefit of all the Blosc community.

The Blosc Development Team kindly invites you to test the different plugins we already offer, but also to try with your own one.  Besides, if you are willing to contribute it to the community, then apply to register it. This way everyone will be able to enjoy a variety of different and unique plugins.  Hope you will enjoy this new and exciting feature!

Last but not least, a big thank you to the NumFOCUS foundation for providing a grant for implementing the register functionality.
