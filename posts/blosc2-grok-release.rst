Blosc2-grok plugin for Blosc2
=============================

The Blosc Development Team is happy to announce that the
first release (0.1.0) of `blosc2-grok <https://github.com/Blosc/blosc2_grok>`_
is out. This dynamic plugin is meant for using the JPEG2000 codec from the grok library.

In this blog we will see how to use it as well as the functionality of some parameters.
To do so, we will depict `an already created
example <https://github.com/Blosc/blosc2_grok/blob/main/examples/params.py>`_. Let's get started!

Registering and using the codec
-------------------------------

Blosc2-grok codec plugin has not been yet registered as a global dynamically loaded
plugin of blosc2, and this is why you will need to register it first with its name and id. This will not
be needed when the codec is registered::
    # Register codec locally for now
    blosc2.register_codec('grok', 160)

To tell blosc2 to use it, you only need to use the same id in the codec field of the cparams::

    # Define the compression parameters. Disable the filters and the
    # splitmode, because these don't work with the codec.
    cparams = {
        'codec': 160,
        'filters': [],
        'splitmode': blosc2.SplitMode.NEVER_SPLIT,
    }

It is important to disable any filter or splitmode, since we don't want the data
to be modified before proceeding to the compression using grok.

Now, imagine you have an image as a numpy array, you can compress it applying the
blosc2-grok plugin. But first, you will need to tell blosc2-grok which codec to use
among the available from the grok library (we will get through the different parameters
later)::

    # Set the parameters that will be used by the codec
    kwargs = {'cod_format': blosc2_grok.GrkFileFmt.GRK_FMT_JP2}
    blosc2_grok.set_params_defaults(**kwargs)

And finally, you are able to compress the image with::

    bl_array = blosc2.asarray(
        np_array,
        chunks=np_array.shape,
        blocks=np_array.shape,
        cparams=cparams,
        urlpath=urlpath,
        mode="w",
    )

We already compressed our first image with blosc2-grok, obtaining a lossless compression ratio
of  x1.67!

Keep in mind that the `chunks` and `blocks` params will need to be set to the shape
of the image (including the number of components) so that grok receives the whole
image as one and therefore, compress better.

Blosc2-grok parameters
----------------------

We already used the `cod_format` blosc2-grok parameter to set the codec to use with the
`blosc2_grok.set_params_defaults()`, but
blosc2-grok has many other parameters. All of them are mentioned in the
`README <https://github.com/Blosc/blosc2_grok#parameters-for-compression>`_ and can be
set with the same function. When possible,
these parameters are the same than `the Pillow
library <https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-2000-saving>`_ to make usage
easier.

In this section, we will see how the `quality_mode` and `quality_layers` work, which
are meant for lossy compression. So, imagine you don't care about the precision
but want a compression ratio of x10. Then, you would specify the `quality_mode` to
be `rates` and the `quality_layers` 10::

    kwargs = {'cod_format': blosc2_grok.GrkFileFmt.GRK_FMT_JP2}
    kwargs['quality_mode'] = 'rates'
    kwargs['quality_layers'] = np.array([10], dtype=np.float64)
    blosc2_grok.set_params_defaults(**kwargs)

Proceeding with the compression like before, you would be able to store the
same image with a compression ratio of x10!

Now, just like in Pillow, `quality_mode` can also be `dB`, which indicates that
you want to specify the quality as the peak signal-to-noise ratio (PSNR)
in decibels. So, the following parameters, will give us a
compression of x9.02::

    kwargs = {'cod_format': blosc2_grok.GrkFileFmt.GRK_FMT_JP2}
    kwargs['quality_mode'] = 'dB'
    kwargs['quality_layers'] = np.array([45], dtype=np.float64)
    blosc2_grok.set_params_defaults(**kwargs)

Another useful parameter if you want to speed things up is the
`num_threads` parameter, although grok already gets a good default for you, you
can set it to the value you desire. Or if you would like to deactivate
multithreading, you can set it to 1::

    kwargs = {'cod_format': blosc2_grok.GrkFileFmt.GRK_FMT_JP2}
    kwargs['num_threads'] = 1
    blosc2_grok.set_params_defaults(**kwargs)

The speed difference when performing lossless compression between the single thread
 and the default thread value is 0.18 - 0.03 seconds, which is x6 times faster!

Results
-------

We did a total of 3 different compressions which can be seen bellow. These images
correspond to the lossless compression, the rates quality mode compression and
the dB quality mode compression from left to right.

.. image:: /images/blosc2-grok-release/kodim23.png
  :width: 30%
  :alt: Lossless compression
.. image:: images/blosc2-grok-release/kodim23rates.png
  :width: 30%
  :alt: Compression with quality mode rates
.. image:: images/blosc2-grok-release/kodim23dB.png
  :width: 30%
  :alt: Compression with quality mode dB

As can be seen, the lossy images have lost some precision which is to be expected when
using this type of compression. Other than that, so far so good!


Conclusions
-----------

The addition of the blosc2-grok plugin to Blosc2 thanks to the grok library, opens
many possibilities for compressing images. In the example we used a RGB image, but
grayscale images can also be compressed without any problem.

If you like this, consider giving a donation to our project.
