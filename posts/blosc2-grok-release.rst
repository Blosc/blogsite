Blosc2-grok plugin for Blosc2
=============================

The Blosc Development Team is happy to announce that the first public release (0.1.0) of `blosc2-grok <https://github.com/Blosc/blosc2_grok>`_ is available for testing. This dynamic plugin is meant for using the JPEG2000 codec from the `grok library <https://github.com/GrokImageCompression/grok>`_.

In this blog we will see how to use it as well as the functionality of some parameters. To do so, we will depict `an already created example <https://github.com/Blosc/blosc2_grok/blob/main/examples/params.py>`_. Let's get started!

Installing the plugin
---------------------

First of all, you will need to install the blosc2-grok plugin. You can do it with::

    pip install blosc2-grok

That's it! You are ready to use it.

Registering and using the codec
-------------------------------

Blosc2-grok codec plugin has not been yet registered as a global dynamically loaded plugin of Blosc2 (we will be doing that shortly, so you would be able to skip this step soon), so you will need to register it locally with its name and id::

    blosc2.register_codec('grok', 160)

To tell Blosc2 to use it, you only need to use the same id in the codec field of the cparams::

    # Define the compression parameters. Disable the filters and the
    # splitmode, because these don't work with the codec.
    cparams = {
        'codec': 160,
        'filters': [],
        'splitmode': blosc2.SplitMode.NEVER_SPLIT,
    }

It is important to disable any filter or splitmode, since we don't want the data to be modified before proceeding to the compression using grok.

Now, imagine you have an image as a NumPy array (let's say, created using [pillow](https://pillow.readthedocs.io/en/stable/)). But first, you will need to tell blosc2-grok which format to use among the available ones in the grok library (we will get through the different parameters later)::

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

We already compressed our first image with blosc2-grok!

In this case, the `chunks` and `blocks` params of Blosc2 have been set to the shape of the image (including the number of components) so that grok receives the image as a whole and therefore, can find more opportunities to compress better.

Setting grok parameters
-----------------------

We have already used the `cod_format` grok parameter to set the format to use with the `blosc2_grok.set_params_defaults()`, but blosc2-grok lets you set many other parameters. All of them are mentioned in the `README <https://github.com/Blosc/blosc2_grok#parameters-for-compression>`_. When possible, and to make it easier for existing users, these parameters are named the same than in `the Pillow library <https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg-2000-saving>`_.

For example, let's see how to set the `quality_mode` and `quality_layers` params, which are meant for lossy compression. So, realize you don't care too much about the quality but want a compression ratio of 10x. Then, you would specify the `quality_mode` to be `rates` and the `quality_layers` to 10::

    kwargs = {'cod_format': blosc2_grok.GrkFileFmt.GRK_FMT_JP2}
    kwargs['quality_mode'] = 'rates'
    kwargs['quality_layers'] = np.array([10], dtype=np.float64)
    blosc2_grok.set_params_defaults(**kwargs)

With that, you will be able to store the same image than before, but with a compression ratio of 10x.  Please note that the `quality_layers` parameter is a numpy array; specifying more than one element here will produce different layers of quality of the original image. Above we only wanted one layer, but if you want to specify more, you can do it like this::

    kwargs['quality_layers'] = np.array([10, 20, 30], dtype=np.float64)

Now, just like in Pillow, `quality_mode` can also be expressed in `dB`, which indicates that you want to specify the quality as the peak signal-to-noise ratio (PSNR) in decibels. For example, let's set a PSNR of 45 dB (which will give us a compression of 9x)::

    kwargs['quality_mode'] = 'dB'
    kwargs['quality_layers'] = np.array([45], dtype=np.float64)

Another useful parameter if you want to speed things up is the `num_threads` parameter. Although grok already sets a good default for you, you can set it to some other value (e.g. when experimenting the best one for your box). Or, if you would like to deactivate multithreading, you can set it to 1::

    kwargs['num_threads'] = 1

For example, in a MacBook Air laptop with Apple M2 CPU (8-core), the speed difference when performing lossless compression between the single thread setting and the default thread value is around 6x, so expect quite large accelerations.

Visual example
--------------

Below we did a total of 3 different compressions: a lossless compression, a lossy with 10x for `rates` quality mode and another lossy with 45dB for `dB` quality mode (generated above), from left to right.

.. image:: files/images/blosc2-grok-release/kodim23.png
  :width: 30%
  :alt: Lossless compression
.. image:: files/images/blosc2-grok-release/kodim23rates.png
  :width: 30%
  :alt: Compression with quality mode rates
.. image:: files/images/blosc2-grok-release/kodim23dB.png
  :width: 30%
  :alt: Compression with quality mode dB

As can be seen, the lossy images have lost some quality which is to be expected when using this level of compression (around 10x cratios). But the great quality of the JPEG2000 codec allows us to still see the image quite well. Furthermore, the combination of grok and Blosc2 allows us to compress the image in a very fast way, but we will leave this for another blog.

Conclusions
-----------

The addition of the grok plugin to Blosc2 opens many possibilities for compressing images. In the example we used a RGB image, but grayscale images, up to 16-bit of precision, can also be compressed without any problem.

Although fully usable, this plugin is still in its early stages, so we encourage you to try it out and give us feedback. We will be happy to hear from you!

Thanks to the [LEAPS consortium](https://www.leaps-innov.eu) and NumFOCUS for sponsoring this work. Providing the funding for this project has allowed us to develop this plugin and make it available to the community.
