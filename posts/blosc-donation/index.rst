.. title: Blosc Received a $50,000 USD donation
.. author: Francesc Alted
.. slug: blosc-donation
.. date: 2020-02-20 01:32:20 UTC
.. tags: donation blosc2 caterva
.. category:
.. link:
.. description:
.. type: text


I am happy to announce that the Blosc project recently received a donation of $50,000 USD from Huawei via NumFOCUS.  Now that we have such an important amount available, our plan is to use it in order to continue making Blosc and its ecosystem more useful for the community.  In order to do so, it is important to stress out that our priorities are going to be on the fundamentals of the stack: getting `C-Blosc2 <https://github.com/Blosc/c-blosc2>`_ out of beta and pushing for making `Caterva <https://github.com/Blosc/Caterva>`_ (the multi-dimensional container on top of C-Blosc2) actually usable.

Critical Tasks: Pushing C-Blosc2 and Caterva
--------------------------------------------

`C-Blosc2 <https://github.com/Blosc/c-blosc2>`_ has been kind of a laboratory that we used for testing new ideas, like new 64-bit containers, new filters, a new serialization system, the concept of pre-filters and others, for the past 5 years.  Although the fork from C-Blosc happened such a long time ago, we tried hard to keep the API backwards compatible so that C-Blosc2 can be used as a drop-in replacement of C-Blosc1 --but beware, the C-Blosc2 format will not be forward-compatible with C-Blosc1, but will be backward-compatible, that is, it will be able to read C-Blosc1 compressed chunks.

On its hand, `Caterva <https://github.com/Blosc/Caterva>`_ is our attempt to build a multidimensional container that is tightly built on top of C-Blosc2, so leveraging its unique features.  Caterva is a C99 library (the same than C-Blosc2) that will allow an easy adoption by many different libraries that are about matrix manipulation.  The fact that it supports on-the-flight compression and persistency will open new possibilities in that the size of matrices will not be limited to the available memory anymore: data may span through available memory *or* disk in *compressed* state.

Provided how fundamental C-Blosc2 and Caterva packages are meant to be, we think that the usefulness of the Blosc project as a whole will be largely benefited from putting most of our efforts here for the next months/years.  For this, we already established a series of priorities for working in these projects, as specified in the roadmaps below

Roadmap for C-Blosc2
--------------------

C-Blosc2 is already in beta stage, and in the next few months we should see it in production stage.  Here are some of the more important the things that we want to tackle in order to make this happen:

* Plugin capabilities for allowing users to add more filters and codecs. There should also be a plugin register capability so that the info about the new filters and codecs can be persistent and propagated to different machines.

* Checksums: the frame can benefit from having a checksum per every chunk/index/metalayer. This will provide more safety towards frames that are damaged for whatever reason. Also, this would provide better feedback when trying to determine the parts of the frame that are corrupted.

* Documentation: utterly important for attracting new users and making the life easier for existing ones. Important points to have in mind here:

  - Quality of API docstrings: is the mission of the functions or data structures clearly and succinctly explained? Are all the parameters explained? Is the return value explained? What are the possible errors that can be returned?

  - Tutorials/book: besides the API docstrings, more documentation materials should be provided, like tutorials or a book about Blosc (or at least, the beginnings of it). Due to its adoption in GitHub and Jupyter notebooks, one of the most extended and useful markup systems is MarkDown, so this should also be the first candidate to use here.

* Wrappers for other languages: Python and Java are the most obvious candidates, but others like R or Julia would be nice to have. Still not sure if these should be produced and maintained by the Blosc development team, or leave them for third-party players that would be interested.

For a more detailed discussion see: https://github.com/Blosc/c-blosc2/blob/master/ROADMAP.md

Roadmap for Caterva
-------------------

Caterva is a much more young project and as such, one may say that it is still in alpha stage, although the basic functionality like creating multidimensional containers, getting items or multidimensional slices or accessing persistent data without a previous load is already there.  However, we still miss important things like:

* A complete refactorization of the Caterva C code to facilitate its usability.

* Adapt the Python interface to the refactorization done in C code.

* Add examples into the Python wrapper documentation and create some jupyter notebooks.

* Build wheels to make the Python wrapper easier for the user.

* Implements a new level of multidimensionality in Caterva. After that, we will support three layers of multidimensionality in a Caterva container: the shape, the chunk shape and the block shape.

For a more detailed discussion see: https://github.com/Blosc/Caterva/blob/master/ROADMAP.md

How we are spending resources
-----------------------------

Money is important, but not everything: you need people to work on a project.  We are slowly starting to put consistent human resources in the Blosc project.  To start with, I (Francesc Alted) and Aleix Alcacer will be putting 25% of our time in the project for the next months, and hopefully others will join too.  We will also be using funds to invest in our main tool, that is laptops and desktop computers, but also some furniture like proper seats and tables; the office space is important for creating a happy team.  Finally, our plan is to use a part of the donation in facilitating meeting among the Blosc development team.

Your input is important for us
------------------------------

Although during the next year or so, we plan to organize some meetings of the board of directors and the Blosc development team, we think that our ideas cannot grow isolated from the community of users.  So in case you want to convey ideas or better, contribute with *implementation* of ideas, we will be happy to hear and discuss.  You can get in touch with us via the Blosc mailing list (https://groups.google.com/forum/#!forum/blosc), and the @Blosc2 twitter account.  We are thinking that having other tools like Discourse may help in driving discussions more to the point, but so far we have little experience with it; if you have other suggestions please tell us.

All in all, the Blosc development team is very excited about this new development, and we are putting all our enthusiasm for delivering a new set of tools that we sincerely hope will of of help for the data community out there.

Finally, let me thank our main sponsor for their generous donation, NumFOCUS for accepting our project inside its umbrella, and to all the users and contributors that made Blosc and its ecosystem to help people through the past years (a bit more than 10 since the first C-Blosc 1.0 release).

  **Enjoy Data!**
