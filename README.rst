Angus Python SDK's documentation
================================

Angus Python SDK is a python client library for `Angus.ai <http://www.angus.ai>`_ Cloud.

Installation
-----------

**Automatic installation**::

  pip install angus-sdk-python

Angus SDK is listed in `PyPI <http://pypi.python.org/pypi/angus-sdk-python>`_ and
can be installed with ``pip`` or ``easy_install``.  Note that the
source distribution includes demo applications that are not present
when Angus SDK is installed in this way, so you may wish to download a
copy of the source tarball as well.

**Manual installation**: Download `here <https://pypi.python.org/packages/source/a/angus-sdk-python/angus-sdk-python-0.0.4.tar.gz>`_

.. parsed-literal::

   tar xvfz angus-sdk-python-0.0.4.tar.gz
   cd angus-sdk-python-0.0.4
   python setup.py build
   sudo python setup.py install

The Angus SDK source code is `hosted on GitHub <https://github.com/angus-ai/angus-sdk-python>`_.

**Initialize your credentials**: Angus SDK request the Angus.ai cloud to provide remote 
artificial intelligence algorithms. Access is restricted and you need some credentials
to be authorized. For a demo purpose you can use the same as the example.
When angus-sdk-python is installed, a new command is available.
This unique help you to configure your environment:

.. parsed-literal::
  $ angusme
  Please copy/paste your client_id: 7f5933d2-cd7c-11e4-9fe6-490467a5e114
  Please copy/paste your access_token: db19c01e-18e5-4fc2-8b81-7b3d1f44533b
  $ 

You could explore all options by typing:

.. parsed-literal::
  $ angusme --help

Hello, world
------------

Here is a simple "Hello, world" example for Angus SDK (replace macgyver.jpg by your own image with a face to detect)::

     import angus

     conn = angus.connect()
     service = conn.services.get_service('face_detection', version=1)
     job = service.process({'image': open('./macgyver.jpg')})
     print job.result['faces']

Go further
----------

- Request your own credentials, currently send us an email at `contact@angus.ai <mailto:contact@angus.ai>`_
- The complete documentation is on the way.
- See "Discussion and support" bellow.


Discussion and support
----------------------

You can discuss Angus SDK on `the Angus SDK developer mailing list <https://groups.google.com/d/forum/angus-sdk-python-dev>`_, and report bugs on the `GitHub issue tracker <https://github.com/angus-ai/angus-sdk-python/issues>`_.

This web site and all documentation is licensed under `Creative
Commons 3.0 <http://creativecommons.org/licenses/by/3.0/>`_.

Angus Python SDK is Angus.ai open source technologies It is available under the `Apache License, Version 2.0. <https://www.apache.org/licenses/LICENSE-2.0.html>`_. Please read LICENSE and NOTICE files for more information.

Copyright 2015, Angus.ai
