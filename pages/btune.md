title: Btune: Making Compression Better

## What is Btune?

<a href="/btune-state-explorer/main.html"> <img src="/btune-state-explorer/btune-preview-running.png" alt="Btune Free in action" width="400" align="right"/></a>

[Btune is a dynamic plugin for Blosc2](https://github.com/Blosc/blosc2_btune) that can help you find the optimal combination of compression parameters for your datasets. Depending on your needs, Btune has three different tiers of support for tuning datasets:

- **Genetic (Btune Free)**: This genetic algorithm tests different combinations of compression parameters to meet the user's requirements for both compression ratio and speed for each chunk in the dataset. It assigns a score to each combination and, after a number of iterations, the software stops and uses the best score (minimal value) found for the rest of the dataset. For a graphical visualization, click on the image, select an example, and click on the 'play' button (it may require clicking twice). This is best suited for personal use.

- **Trained (Btune Models)**: With this approach, the user sends a representative sample of datasets to the Blosc development team and receives back trained neural network models that enable Btune to predict the best compression parameters for similar or related datasets. This approach is best for workgroups that need to optimize for a limited variety of datasets.

- **Fully managed (Btune Studio)**: The user receives a license to use our training software, which enables on-site training for an unlimited number of datasets. The license also includes a specified number of training/consultancy hours to help the user get the most out of the training process. Refer to the details below for more information. This approach is best suited for organizations that need to optimize for a wide range of datasets.

## How To Use Btune?

Btune is a plugin for Blosc2 that can be obtained from the [PyPI repository](https://pypi.org/project/blosc2-btune/). You can learn how to use it in the [Btune README](https://github.com/Blosc/blosc2_btune/#readme). The plugin is currently only available for Linux and macOS, and only for Intel architecture. However, we plan to add support for other architectures in the future.

The Btune plugin above can be used for both Btune Free and Btune Models.  For Btune Studio, you will need to contact us to get the additional software for training the models.

Also, there are a couple of tutorials about different aspects of Btune.  You can find them here:

- [Btune Genetic & Trained](https://github.com/Blosc/Btune-Genetic-tutorial)
- [Btune Studio](https://github.com/Blosc/Btune-tutorial)

For completing the Studio version, you will need to contact us to get the additional software for training the models.

## Why Btune?

Essentially, because compression is not a one-codec-fits-all problem. Compressing data involves a trade-off between compression ratio and speed. A higher compression ratio results in a slower compression process. Depending on your needs, you may want to prioritize one over the other.

For instance, if you are storing data from high-speed data acquisition systems, you may want to prioritize *compression* speed over compression ratio. This is because you will be writing data at speeds near the capacity of your systems. On the other hand, if the goal is to access the data repeatedly from a file system, you may want to prioritize *decompression* speed over compression ratio for optimal performance.

Finally, if you are storing data in the cloud, you may want to prioritize *compression ratio* over speed. This is because you pay for the storage (and potentially upload/download costs) of data.

<!-- <a href="https://www.blosc.org/posts/bytedelta-enhance-compression-toolset/"> <img src="/btune/cratio-vs-cspeed.png" alt="Compression ratio vs compression speed" width="800" align="center"/></a> -->

<a href="https://www.blosc.org/posts/bytedelta-enhance-compression-toolset/"> <img src="/btune/cratio-vs-dspeed.png" alt="Compression ratio vs compression speed" width="800" align="center"/></a>

<!-- <a href="https://www.blosc.org/posts/bytedelta-enhance-compression-toolset/"> <img src="/btune/cratio-vs-codec.png" alt="Compression ratio vs codec" width="800" align="center"/></a> -->

Finding the optimal compression parameters in Blosc2 can be a slow process due to the large number of combinations of compression parameters (codec, compression level, filter, split mode, number of threads, etc.), and it may require a significant amount of manual trial and error to find the best combinations. However, you can significantly speed up this process by using Btune while compressing your datasets.

## What's in a Model?

<img src="/btune/NN-simple-model.png" alt="Simple Neural Network Model" width="250" align="right"/>

A neural network is a simplified model of the way the human brain processes information. It simulates a large number of interconnected processing units that resemble abstract versions of neurons. These processing units are arranged in layers, which are connected by weights that are adjusted during the training process. To train the network, a large number of examples are fed into it, and the weights are adjusted to minimize the difference between the expected output and the actual output. Once training is complete, the network can be used to predict the output for new inputs.

In our context, the "model" refers to the serialization of the layers and weights of the trained neural network. It is delivered to you as a set of small files (in JSON and TensorFlow format) that can be [placed anywhere in your filesystem for Btune to access](https://github.com/Blosc/blosc2_btune/blob/main/README.md#btune-models). By using this model, Btune can predict the optimal combination of compression parameters for a given chunk of data. The inference process is very fast, making it suitable for selecting the appropriate compression parameters on a chunk-by-chunk basis while consolidating large amounts of data.

## Licensing Model

There are different licenses available for Btune.

**Btune Free** allows you to explore compression parameters that are better suited to your datasets. However, this process can be slow and may require a large number of iterations before finding the best combination. Additionally, certain chunks in the same dataset may benefit more from a particular combination, while others may benefit more from a different one.

**Btune Models** addresses the limitations of Btune Free by automatically finding the best combination for chunks in a dataset, without requiring any manual operation. This is made possible by using pre-trained neural network models, which allow the best combination to be found on a chunk-by-chunk basis, thereby increasing the effectiveness of the compression process.

Finally, for those who need to train a wide range of datasets, **Btune Studio** provides access to the software necessary for training the datasets yourself. In this way, you have control over all the necessary components to find optimal compression parameters and avoid external dependencies.

## Donation fees

### Btune Free
It is free to use (but hey, if you like the project, please consider [donating](https://www.blosc.org/pages/donate/) too!). Please note that it is licensed under an [Affero GPLv3 license](https://www.gnu.org/licenses/agpl-3.0.en.html). This license comes with limited support, as it is mostly a community-supported project.

### Btune Models
Requires a donation of $1500 USD (or 1500 EUR) for up to 3 trained models. If you need more than 3 models, ask for a quote.

### Btune Studio
Requires a donation of $7500 USD (or 7500 EUR) for the first year, or $750 USD (or 750 EUR) per month for at least 1 year, whichever fits best for you.  Renewal is $6000 USD (or 6000 EUR) per year, or $600 USD (or 600 EUR) monthly after the 1st year.  If you don't renew, you keep the right to use Btune Studio for producing models internally in your organization forever, but you will not have access to newer versions.

**Note**: With Btune Studio we deliver sources of it, so that you can build/fix it yourself.  However, you cannot include it in your own software and distribute it without permission.

### Priority Support
For support hours, please [contact us](mailto:contact@blosc.org).  Our donation fee is typically $100 USD (or 100 EUR) per hour. The support can be used for training in the use of the software, or for consultation on compression for big data in general.

### How To Pay?
You can do the payments via [the donations form for the Blosc project](https://www.blosc.org/pages/donate/) where, at the end of the form, you can specify the kind of license and support you are interested in.  If for some reason, you cannot (or you don't want to) donate via NumFOCUS, please [contact us](mailto:contact@blosc.org); we can invoice you directly as well.

### Why donations via NumFOCUS?

[NumFOCUS](https://numfocus.org/community/mission) is a non-profit organization with a mission to promote open practices in research, data, and scientific computing. They serve as a fiscal sponsor for open-source projects and organize community-driven educational programs.

The Blosc project has benefited significantly from NumFOCUS [Small Development Grant Program](https://numfocus.org/programs/small-development-grants), and they have been instrumental in helping us to channel donations. When you pay Btune fees by donating to the Blosc project via NumFOCUS, 15% of the amount goes to them as a fee. We believe this fee is fair and helps repay NumFOCUS for the services, support, and love they have shown us over the years. Your donation will not only strengthen the Blosc project, but also many other open-source projects.

If you (or your organization) have issues donating via NumFOCUS, the Blosc development team can also produce invoices directly.

## Practical Example

In the figure below, you can see the most predicted combinations of codecs and filters when optimizing for **decompression** performance on a subset of the [Gaia dataset](https://gea.esac.esa.int/archive/). The subset contains stars that are less than 10,000 light years away from our Sun (around 500 millions). The data is stored in an array of shape (20,000, 20,000, 20,000), with the number of stars in every cubic light year cell, resulting in a total uncompressed size of 7.3 TB.

<img src="/btune/Gaia-3D-model-decomp.png" alt="Most predicted codecs/filters for decompression" width="400" align="center"/>

The following figure displays the speed that can be achieved by obtaining multiple multidimensional slices of the dataset along different axes, using the most efficient codecs and filters for various tradeoffs. The speed is measured in GB/s, so a higher value is better.

<img src="/btune/slicing-speed-filters.png" alt="Slicing speed for different codecs/filters" width="800" align="center"/>

The results indicate that the fastest compression combination is BloscLZ (compression level 5), closely followed by Zstd (compression level 9). Also, note how the fastest codecs, BloscLZ and also Zstd, are not affected very much by the number of threads used, which means that they are not CPU-bound, so small computers or laptops with low core counts will be able to reach good speeds.

Finally, it is important to compare the compression ratios achieved by different codecs and filters. In the following figure, we can see the file sizes created when using the most commonly predicted codecs and filters for various trade-offs. The file sizes are measured in GB, so the lower, the better.

<img src="/btune/filesizes-filters.png" alt="File sizes for different codecs/filters" width="600" align="center"/>

In this case, the trained model recommends using Zstd (compression level 9) for a good balance between compression ratio and decompression speed, and that can be confirmed by seeing the large difference in size. However, note that BitShuffle + Zstd (compression level 9) is not a good option in general, unless you are looking for the absolute best compression ratio.

You can read more background for this example in [our forthcoming article for SciPy 2023](https://procbuild.scipy.org/download/Blosc-2023).

## Testimonials

> Blosc2 and Btune are fantastic tools that allow us to efficiently compress and load large volumes of data for the development of AI algorithms for clinical applications. In particular, the new NDarray structure became immensely useful when dealing with large spectral video sequences.

-- Leonardo Ayala, Div. Intelligent Medical Systems, German Cancer Research Center (DKFZ)

> Btune is a simple and highly effective tool. We tried this out with @LEAPSinitiative data and found some super useful spots in the parameter space of Blosc2 compression arguments! Awesome work, @Blosc2 team!

-- Peter Steinbach, Helmholtz AI Consultants Team Lead for Matter Research @HZDR_Dresden

## Contact

If you are interested in Btune and have any further questions, please contact us at [contact@blosc.org](mailto:contact@blosc.org).
