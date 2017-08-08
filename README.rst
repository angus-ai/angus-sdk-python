Angus Python SDK's documentation
================================

Angus Python SDK is a python client library for `Angus.ai <http://www.angus.ai>`_ perception web services.
Please look at Angus.ai full API `here <http://angus-doc.readthedocs.io/en/latest/services/index.html>`_.


Installation
-----------

**Automatic installation**::

  pip install angus-sdk-python

Angus SDK is listed in `PyPI <http://pypi.python.org/pypi/angus-sdk-python>`_ and
can be installed with ``pip`` or ``easy_install``.  Note that the
source distribution includes demo applications that are not present
when Angus SDK is installed in this way, so you may wish to download a
copy of the source tarball as well.

**Manual installation**: Download `here <https://github.com/angus-ai/angus-sdk-python/releases/download/0.0.14/angus-sdk-python-0.0.14.tar.gz>`_

.. parsed-literal::

   tar xvfz angus-sdk-python-0.0.14.tar.gz
   cd angus-sdk-python-0.0.14
   python setup.py build
   sudo python setup.py install

The Angus SDK source code is `hosted on GitHub <https://github.com/angus-ai/angus-sdk-python>`_.

angus-sdk-python ships with a simple command tool 'angusme' that makes it easy to configure your environment.

You can explore all options by typing:

.. parsed-literal::
  $ angusme --help


Configuration
-------------

In order to authenticate your request to Angus.ai servers, you must register `here <http://www.angus.ai/request-credentials/>`_, and use the provided credentials as shown below.
It is free and takes 1 minute.

In a terminal, type:

.. parsed-literal::

    $ angusme
    Please choose your gateway (current: https://gate.angus.ai): [Just press Enter]
    Please copy/paste your client_id: ********-****-****-****-************
    Please copy/paste your access_token: ********-****-****-****-************

Note that on ``Windows`` system, the previous command might not work.
In that case use this command instead (replace by your Python installation path):

.. parsed-literal::

   $ python C:\\full\\path\\to\\Python<version>\\Scripts\\angusme


Hello, world
------------

Here is a simple "Hello, world" example for Angus SDK (replace macgyver.jpg by your own image with a face to detect)::

     import angus

     conn = angus.connect()
     service = conn.services.get_service('face_detection', version=1)
     job = service.process({'image': open('./macgyver.jpg')})
     print job.result['faces']


Hello, world (asynchronous)
---------------------------

Here is the same simple example but with a non-blocking call to 'process'. The provided callback is called whenever the request terminates::

    import angus

    def f(job):
        print job.result['faces']

    conn = angus.connect()
    service = conn.services.get_service('face_detection', version=1)
    job = service.process({'image': open('./macgyver.jpg')}, callback=f)
    ### do stuff here while waiting for the server response.


Go further
----------

- The complete API documentation is available `here <http://doc.angus.ai>`_.
- See "Discussion and support" bellow.


Discussion and support
----------------------

You can contact Angus.ai team at `contact@angus.ai <mailto:contact@angus.ai>`_, and report bugs on the `GitHub issue tracker <https://github.com/angus-ai/angus-sdk-python/issues>`_.

For technical issues or question, start on Angus forum to get support
by sending email on `support@angus.ai <mailto:support@angus.ai>`_ or
by using online web interface https://groups.google.com/a/angus.ai/d/forum/support

This web site and all documentation is licensed under `Creative
Commons 3.0 <http://creativecommons.org/licenses/by/3.0/>`_.

Angus Python SDK is an Angus.ai open source technology. It is available under the `Apache License, Version 2.0. <https://www.apache.org/licenses/LICENSE-2.0.html>`_. Please read LICENSE and NOTICE files for more information.

Copyright 2015-2017, Angus.ai
