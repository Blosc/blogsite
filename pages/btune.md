title: Btune: Making Compression Better


## What is Btune?

<a href="/btune-state-explorer/main.html"> <img src="/btune-state-explorer/btune-preview-running.png" alt="Btune Free in action" width="400" align="right"/></a>

[Btune is a dynamic plugin for Blosc2](https://github.com/Blosc/blosc2_btune) that can help you find the optimal combination of compression parameters for your datasets. Depending on your needs, Btune has three different tiers of support for tuning datasets:

- **Genetic (Btune Free)**: This genetic algorithm tests different combinations of compression parameters to meet the user's requirements for both compression ratio and speed for each chunk in the dataset. It assigns a score to each combination and, after a number of iterations, the software stops and uses the best score (minimal value) found for the rest of the dataset. For a graphical visualization, click on the image, select an example, and click on the 'play' button (it may require clicking twice). This is best suited for personal use.

- **Trained (Btune Model)**: The user sends a representative sample of datasets to the Blosc development team and receives back a trained neural network model that enables Btune to predict the best compression parameters for similar/related datasets. The neural network model is serialized as a small number of files (in JSON and TensorFlow format) that can be [dropped anywhere in your filesystem for Btune to use](https://github.com/Blosc/blosc2_btune#btune-model). This approach is best for work-groups that need to optimize for a limited variety of datasets.

- **Fully managed (Btune Studio)**: The user gets a license to use our training software, allowing on-site training for an unlimited number of datasets. The license also includes a specified number of training/consultancy hours to help the user get the most out of the training process.  See below for more details.  This approach is best for organizations that need to optimize for a wide variety of datasets.

For usage details, see the [README of the Btune plugin](https://github.com/Blosc/blosc2_btune#readme).

## Why Btune?

Finding the optimal compression parameters in Blosc2 can be a slow process. Due to the large number of combinations of compression parameters (codec, compression level, filter, split mode, number of threads, etc.), it may require a significant amount of manual trial and error to find the best combinations. However, you can significantly accelerate this process by using Btune while compressing your datasets.

There are different licenses available for Btune.

**Btune Free** enables you to explore compression parameters that better adapt to your datasets. However, this process can be slow and may require a large number of iterations before finding the best combination. Moreover, it is possible that some chunks in the same dataset would benefit more from a certain combination, while others would benefit more from a different one.

The **Btune Model** addresses the limitations of Btune Free by finding the best combination for chunks in a dataset automatically, without requiring any manual operation. This is possible because a pre-trained neural network model is provided, allowing the best combination to be found on a chunk-by-chunk basis, increasing the effectiveness of the compression process.

Finally, for those who need to train a wide diversity of datasets, **Btune Studio** provides access to the software to train the datasets yourself. With this, you have control over all the necessary components for finding optimal compression parameters and avoiding external dependencies.

## Licenses and Pricing

- **Btune Free** is free to use. Please note that it is licensed under an [Affero GPLv3 license](https://www.gnu.org/licenses/agpl-3.0.en.html). This license comes with limited support, as it is mostly a community-driven project.

- The **Btune Model** requires a fee of $1500 USD (or 1500 EUR) for up to 3 trained models per year, including 3 hours of support. You can ask to re-train models for the same or a different set of datasets on a yearly basis.  The renewal is $1200 USD (or 1200 EUR) per year.  If you don't renew, you keep the right to use the models you already have forever, but you will not be able to ask for training new models.

- **Btune Studio** requires a fee of $7500 USD (or 7500 EUR) per year, or $750 USD (or 750 EUR) per month for at least 1 year, whichever fits best for you. This includes 25 hours of support per year, or up to 3 hours of support per month when using the monthly fee. The renewal is $6000 USD (or 6000 EUR) per year, or $600 USD (or 600 EUR) monthly after the 1st year.  If you don't renew, you keep the right to use Btune Studio for producing models internally in your organization forever, but you will not have access to newer versions.

**Note**: Btune Studio is not open source, but we deliver sources with it so that you can build/fix it yourself.  However, you cannot include it in your own software and distribute it without permission.

Additionally, for all licenses we offer an optional support pack that includes up to 3 hours of support per month for a monthly fee of $250 (or 250 EUR).  For more support hours, please [contact us](mailto:contact@blosc.org). The contracted support can be used for training in the use of the software, or for consultation on compression for big data in general.

You can do the payments via [the donations form for the Blosc project](https://www.blosc.org/pages/donate/) where, at the end of the form, you can specify the kind of license and support you are interested in.  If for some reason, you cannot (or you don't want to) donate via NumFOCUS, please [contact us](mailto:contact@blosc.org); we can invoice you directly as well.

## Why donations via NumFOCUS?

[NumFOCUS](https://numfocus.org/community/mission) is a non-profit organization with a mission to promote open practices in research, data, and scientific computing. They serve as a fiscal sponsor for open-source projects and organize community-driven educational programs.

The Blosc project has benefited significantly from NumFOCUS [Small Development Grant Program](https://numfocus.org/programs/small-development-grants), and they have been instrumental in helping us to channel donations. When you pay Btune fees by donating to the Blosc project via NumFOCUS, 15% of the amount goes to them as a fee. We believe this fee is fair and helps repay NumFOCUS for the services, support, and love they have shown us over the years. Your donation will not only strengthen the Blosc project, but also many other open-source projects.

If you or your organization encounter issues donating via NumFOCUS, the Blosc development team can also produce invoices directly.

## Testimonials

> Blosc2 and Btune are fantastic tools that allow us to efficiently compress and load large volumes of data for the development of AI algorithms for clinical applications. In particular, the new NDarray structure became immensely useful when dealing with large spectral video sequences.

-- Leonardo Ayala, Div. Intelligent Medical Systems, German Cancer Research Center (DKFZ)

> Btune is a simple and highly effective tool. We tried this out with @LEAPSinitiative data and found some super useful spots in the parameter space of Blosc2 compression arguments! Awesome work, @Blosc2 team!

-- Peter Steinbach, Helmholtz AI Consultants Team Lead for Matter Research @HZDR_Dresden.

## Contact

If you are interested in Btune and have any further questions, please contact us at [contact@blosc.org](mailto:contact@blosc.org).
