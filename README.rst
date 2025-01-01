.. |pypi_download| image:: https://img.shields.io/pypi/dm/trame-simput

===========================================================
trame-simput |pypi_download|
===========================================================

Python package that let you create web forms/ui using Trame.
The project include both a Python module along with a generated
Vue based plugin for proxy editing using a set of widgets which
can be extended by the user.

Introduction
-----------------------------------------------------------

Simput rely on **definitions** to describe the set of **proxies** that it can control.
A **proxy** is a virtual object that gather a set of **properties** which as a whole
represent its **state**. **Proxies** are meant to streamline **state** update and exchange.

A **proxy** can also be used to control a **concrete object** by mapping its state to it.
This is particularly important when a **concreate object** needs to live on a remote location
or inside another thread or service. Having a **proxy** allow us to present and edit its **properties**
in a way that we can easily reconciliate its **state** with its **concrete object** counter part.

When initializing or editing a **property**, we may want to bounds the values to a limited set.
To apply constraints to a **property**, you can define a **domains** section.
A **domain** can be used to compute a reasonable **initial value** once all its dependency have
been resolved or limit a value to be within a set of available ones (list, range).

On top of the data model, Simput aims to provide UI/forms to help user input and update
any user data. And for that we have some UI needs that could be defined to refine how
the information should be display to the user. By default the data model **definition**
is all we need, but if you want to add internationalization, you can provide a **language**
definition to describe **label** and **help** of any **property**. Then if the automatic
property layout is not to your liking, you can create a **layout** definition to manually place
into a grid where each **property** of a given **proxy** should go. Also, you can use that
**layout** to optionally show/hide a subset of properties based on a **domain**.

With definitions for the **data models** with **domains**, **languages** and **ui layouts**,
we think we are empowering developers to create applications with complex user input in no time.
High level definitions files allow developers to describe in a concise manner what they want rather
than how to make their data editing possible within their application.

Detailed documents
-----------------------------------------------------------

* `Definitions explained <./docs/definitions.md>`_
* `API <./docs/api.md>`_
* Examples: `Address book <./examples/00_AddressBook>`_, `Widgets <./examples/01_Widgets>`_, `Hints <./examples/02_Hints>`_, `VTK <./examples/03_VTK>`_, `Dynamic domain <./examples/04_DynaDomain>`_

License: Apache Software License
-----------------------------------------------------------

.. code-block:: console

    Apache Software License 2.0

    Copyright (c) 2022, Kitware Inc.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.



Development
-----------------------------------------------------------

Build and install the Vue components

.. code-block:: console

    cd vue-components
    npm i
    npm run build
    cd -

Install the application for development

.. code-block:: console

    pip install -e .
