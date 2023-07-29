.. title: Dynamic plugins in C-Blosc2
.. author: Marta Iborra, Francesc Alted
.. slug: dynamic-plugins
.. date: 2023-05-10 08:32:20 UTC
.. tags: blosc2 plugins dynamic
.. category:
.. link:
.. description:
.. type: text


The Blosc Development Team is excited to announce that the latest version of `C-Blosc2 <https://github.com/Blosc/c-blosc2>`_ includes a great new feature: the ability to dynamically load plugins, such as codecs and filters. This means that these codecs or filters will only be loaded at runtime when they are needed.

Creating a dynamically loaded filter
------------------------------------

To learn how to create these plugins, we'll use an `already created example <https://github.com/Blosc/blosc2_plugin_example>`_.  Suppose you have a filter that you want C-Blosc2 to load dynamically only when it is used. In this case, you need to create a Python package to build a wheel and install it as a separate library. You can follow the structure used in `blosc2_plugin_example <https://github.com/Blosc/blosc2_plugin_example>`_ to do this::

    ├── CMakeLists.txt
    ├── README.md
    ├── blosc2_plugin_name
    │         └── __init__.py
    ├── pyproject.toml
    ├── requirements-build.txt
    ├── setup.py
    └── src
        ├── CMakeLists.txt
        ├── test_plugin.c
        └── urfilters.c

Note that the project name will be `blosc2_` followed by the plugin name. The corresponding functions will be defined in the `src` folder, in our case in `urfilters.c`, following the same format as functions for user-defined filters (see `<https://github.com/Blosc/c-blosc2/blob/main/plugins/README.md>`_ for more information)::

    int blosc2_plugin_example_forward(const uint8_t* src, uint8_t* dest,
                                      int32_t size, uint8_t meta,
                                      blosc2_cparams *cparams, uint8_t id) {
      blosc2_schunk *schunk = cparams->schunk;

      for (int i = 0; i < size / schunk->typesize; ++i) {
        switch (schunk->typesize) {
          case 8:
            ((int64_t *) dest)[i] = ((int64_t *) src)[i] + 1;
            break;
          default:
            BLOSC_TRACE_ERROR("Item size %d not supported", schunk->typesize);
            return BLOSC2_ERROR_FAILURE;
        }
      }
      return BLOSC2_ERROR_SUCCESS;
    }


    int blosc2_plugin_example_backward(const uint8_t* src, uint8_t* dest, int32_t size,
                                       uint8_t meta, blosc2_dparams *dparams, uint8_t id) {
      blosc2_schunk *schunk = dparams->schunk;

      for (int i = 0; i < size / schunk->typesize; ++i) {
        switch (schunk->typesize) {
          case 8:
            ((int64_t *) dest)[i] = ((int64_t *) src)[i] - 1;
            break;
          default:
            BLOSC_TRACE_ERROR("Item size %d not supported", schunk->typesize);
            return BLOSC2_ERROR_FAILURE;
        }
      }
      return BLOSC2_ERROR_SUCCESS;
    }

In addition to these functions, we need to create a `filter_info` (or `codec_info` or `tune_info` in each case) named `info`. This variable will contain the names of the `forward` and `backward` functions. In our case, we will have::

    filter_info info  = {.forward="blosc2_plugin_example_forward", .backward="blosc2_plugin_example_backward"};

To find the functions, the variable must always be named `info`.

Creating and installing the wheel
---------------------------------

Once the project is done, you can create a wheel and install it locally::

    python setup.py bdist_wheel
    pip install dist/*.whl

Registering the plugin in C-Blosc2
----------------------------------

After installation, you must register it in C-Blosc2. This step is necessary only if the filter is not already registered globally by C-Blosc2, which is likely if you are testing it or do not want to share it with other users. To register it, follow the same process as registering a user-defined plugin (filling its structure), but leave the function pointers as NULL::

    blosc2_filter plugin_example;
    plugin_example.id = 250;
    plugin_example.name = "plugin_example";
    plugin_example.version = 1;
    plugin_example.forward = NULL;
    plugin_example.backward = NULL;
    blosc2_register_filter(&plugin_example);

When the filter is used for the first time, C-Blosc2 will automatically fill in the function pointers.

Using the plugin
----------------

To use the plugin, simply set the filter ID in the filters pipeline, as you would do with user-defined filters::

    blosc2_cparams cparams = BLOSC2_CPARAMS_DEFAULTS;
    cparams.filters[4] = 250;
    cparams.filters_meta[4] = 0;

    blosc2_dparams dparams = BLOSC2_DPARAMS_DEFAULTS;

    blosc2_schunk* schunk;

    /* Create a super-chunk container */
    cparams.typesize = sizeof(int32_t);
    blosc2_storage storage = {.cparams=&cparams, .dparams=&dparams};
    schunk = blosc2_schunk_new(&storage);

To see a full usage example, refer to `<https://github.com/Blosc/blosc2_plugin_example/blob/main/examples/test_plugin.c>`_. Keep in mind that the executable using the plugin must be launched from the virtual environment where the plugin wheel was installed. When compressing or decompressing, C-Blosc2 will dynamically load the library and call its functions (as depicted below).

.. image:: /images/dynamic-plugins/dynamic-plugin.png
  :width: 100%
  :alt: Dynamically loading filter

Once you are satisfied with your plugin, you may choose to request the Blosc Development Team to register it as a global plugin. The only difference (aside from its ID number) is that users won't need to register it locally anymore. However, the plugin will not be loaded until it is requested by any compression or decompression function.

Conclusions
-----------

C-Blosc2's ability to support dynamically loaded plugins allows the library to grow in features without increasing the size of the library itself. For more information about user-defined plugins, refer to this `blog entry <https://www.blosc.org/posts/registering-plugins/>`_.

We appreciate your interest in our project! If you find our work useful and valuable, we would be grateful if you could support us by `making a donation <https://www.blosc.org/pages/donate/>`_. Your contribution will help us continue to develop and improve our technology, making it more accessible and useful for everyone.  Our team is dedicated to creating high-quality, efficient software that meets the needs of our users, and your support will help us to achieve this goal.
