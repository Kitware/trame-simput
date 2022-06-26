============
trame-simput
============

SimPut implementation for Trame.


* Free software: Apache Software License


Installing
----------

Build and install the Vue components

.. code-block:: console

    cd vue-components
    npm i
    npm run build
    cd -

Install the application

.. code-block:: console

    pip install -e .


Introduction
------------

SimPut empowers developers to create applications with complex user input in no time.
High level definition files allow developers to describe in a concise manner what they want rather
than how to make their data editing possible within their application.

SimPut relies on **definitions** to describe a set of **proxies** that it can control.
A **proxy** is a virtual object that gathers a set of **properties**, which as a whole
represents its **state**. **Proxies** are meant to streamline **state** update and exchange.

A **proxy** can also be used to control a **concrete object** by mapping its state to it.
This is particulary important when a **concrete object** needs to live on a remote location
or inside another thread or service. Having a **proxy** allows us to present and edit its **properties**
in a way that we can easily reconciliate its **state** with its **concrete object** counter-part.

When initializing or editing a **property**, we may want to bind the values to a limited set.
To apply constraints to a **property**, you can define a **domains** section.
A **domain** can be used to compute a reasonable **initial value** once all its dependency have
been resolved or limit a value to be within a set of available ones (list, range).

On top of the data model, SimPut aims to provide UI/forms to help users input and update
any user data. And for that we have some UI needs that could be defined to refine how
the information should be displayed to the user. By default the data model **definition**
is all we need, but if you want to add internationalization, you can provide a **language**
definition to describe **label** and **help** of any **property**. Then if the automatic
property layout is not to your liking, you can create a **layout** definition to manually place
into a grid where each **property** of a given **proxy** should go. Also, you can use that
**layout** to optionally show/hide a subset of properties based on a **domain**.


Detailed documents
------------------

* `Definitions <./docs/definitions.md/>`_
* `API <./docs/api.md>`_
