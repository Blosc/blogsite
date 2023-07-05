title: BTune: Making Compression Better

<!---
![Btune Free in action](/btune-state-explorer/btune-preview-running.png "")
{align=left}
-->

<a href="/btune-state-explorer/main.html"> <img src="/btune-state-explorer/btune-preview-running.png" alt="Btune Free in action" width="300" align="right"/>

## What is Btune?

Btune is a dynamic plugin for Blosc2 that can help you find the optimal combination of compression parameters for your datasets. Depending on your needs, Btune has three different operating modes (see below for more details and pricing):

- **Genetic (Btune Free)**: This genetic algorithm tests different combinations of compression parameters to meet the user's requirements for both compression ratio and speed for each chunk in the dataset. It assigns a score to each combination and, after a number of iterations, the software stops and uses the best score (minimal value) found for the rest of the dataset. For a graphical visualization, click on the graphic, select an example, and clik on the 'play' button (it may require clicking twice). This is best suited for personal use.
- **Trained (Btune Model)**: The user sends a representative sample of datasets to the Blosc development team and receives back a trained neural network model that enables Btune to predict the best compression parameters for similar/related datasets. This approach is best for workgroups that need to optimize for a limited variety of datasets.
- **Fully managed (Btune Studio)**: The user gets a license to use our training software, allowing on-site training for an unlimited number of datasets. The license also includes a specified number of training/consultancy hours to help the user get the most out of the training process.

## Why Btune?

Finding the optimal compression parameters in Blosc2 can be a slow process. Due to the large number of combinations of compression parameters (codec, compression level, filter, split mode, number of threads, etc.), it may require a significant amount of manual trial and error to find the best combinations. However, you can significantly accelerate this process by using Btune while compressing your datasets.

There are different licenses available for Btune.

**Btune Free** enables you to explore compression parameters that better adapt to your datasets. However, this process can be slow and may require a large number of iterations before finding the best combination. Moreover, it is possible that some chunks in the same dataset would benefit more from a certain combination, while others would benefit more from a different one.

The **Btune Model** addresses the limitations of Btune Free by finding the best combination for chunks in a dataset automatically, without requiring any manual operation. This is possible because a pre-trained neural network model is provided, allowing the best combination to be inferred on a chunk-by-chunk basis. This increases the effectiveness of the compression process.

Finally, for those who need to train various datasets, **Btune Studio** provides access to the software to train the datasets yourself. With this, you have control over all the necessary components for finding optimal compression parameters and avoiding external dependencies.

## Licenses and Pricing

- **Btune Free** is free to use. Please note that it is licensed under an [Affero GPLv3 license] (https://www.gnu.org/licenses/agpl-3.0.en.html).
- The **Btune Model** requires a donation of $1500 USD (or 1500 EUR) per trained model per year. You can ask to train a different model on a yearly basis. Additionally, we offer an optional support pack that includes up to 10 hours of support per year for a monthly fee of $250 (or 250 EUR).
- **Btune Studio** requires a donation of $7500 USD (or 7500 EUR) per year, or $750 (or 750 EUR) per month for at least 1 year, whichever fits best for you. This includes 25 hours of support per year that can be used for training in the use of the software or for consultation on compression or big data handling in general.

To do the donations to the Blosc project, visit https://www.blosc.org/pages/donate/ and specify the kind of license you are interested in.

## Why Donations via NumFOCUS?

[NumFOCUS](https://numfocus.org/community/mission) is a non-profit organization with a mission to promote open practices in research, data, and scientific computing. They serve as a fiscal sponsor for open-source projects and organize community-driven educational programs.

The Blosc project has benefited significantly from NumFOCUS [Small Development Grant Program](https://numfocus.org/programs/small-development-grants), and they have been instrumental in helping us to channel donations.

When you donate to the Blosc project via NumFOCUS, 15% of the amount goes to them as a fee. We believe this fee is fair and helps repay them for the services, support, and love they have shown us over the years. Your donation will not only strengthen the Blosc project, but also many other open-source projects.

If you or your organization encounter issues donating via NumFOCUS, the Blosc development team can also produce invoices directly.

## Contact

If you are interested in Btune and have any further questions, please contact us at [contact@blosc.org](mailto:contact@blosc.org).
