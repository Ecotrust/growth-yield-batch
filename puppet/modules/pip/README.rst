pip for puppet
==============
This is a `puppet`_ module for using Python's `pip`_.  Puppet has a
built-in pip provider, but it's implementation leaves out a few pieces:

* No ability to install from requirements file.
* No ability to add extra arguments
* No support for using mirrors or specifying alternate indexes.

This module fixes this.


Usage
-----
Make sure this module is available by adding this repository's contents
in a directory called ``pip`` inside your Puppet's ``moduledir``.


Boostrap pip (optional):
""""""""""""""""""""""""
Once the module is installed and accessible, you can bootstrap your
pip environment by adding this to your manifest::

	pip::bootstrap{ "pip-bootstrap": }

You only need to do this on machines that do not already have pip
installed.  This installs the latest version of pip and `distribute`_


Installing Packages:
""""""""""""""""""""
To install a package, simply provide the name of the package you want
to install like this::

	pip::install { "armstrong": }

The name is passed to ``pip::install``, so you can include version
requirements and so on using the name.


Configuration
-------------
*TODO*


.. _distribute: http://packages.python.org/distribute/
.. _pip: http://www.pip-installer.org/
.. _puppet: http://puppetlabs.com/