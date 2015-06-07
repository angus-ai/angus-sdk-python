.. Angus Python SDK documentation master file, created by
   sphinx-quickstart on Mon Mar 30 23:21:16 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Angus Python SDK's documentation!
=================================

Angus Python SDK is a python client library for Angus.ai Cloud.

Instalation
-----------

Linux
+++++

**Automatic installation**::

  pip install angus-sdk-python

Angus SDK is listed in `PyPI <http://pypi.python.org/pypi/angus-sdk-python>`_ and
can be installed with ``pip`` or ``easy_install``.  Note that the
source distribution includes demo applications that are not present
when Angus SDK is installed in this way, so you may wish to download a
copy of the source tarball as well.

**Manual installation**: Download `here <https://pypi.python.org/packages/source/a/angus-sdk-python/angus-sdk-python-0.0.2.tar.gz>`_

.. parsed-literal::

   tar xvfz angus-sdk-python-|version|.tar.gz
   cd angus-sdk-python-|version|
   python setup.py build
   sudo python setup.py install

The Angus SDK source code is `hosted on GitHub <https://github.com/angus-ai/angus-sdk-python>`_.

**Platforms**: Angus SDK can be use on any platform.

Windows
+++++++

**Automatic installation**::

  python -m pip instsall angus-sdk-python


Initialisation
--------------

Angus SDK needs some information to connect to the angus.ai cloud:
  * **the root url**, this is the main entry point of the targeted server
  * **client id / access token** (equivalent to login/password for a machine)
  * **certificates**: currently the angus.ai platform certificate is not available
    on every platform, then we provide them into a bundle.
All these parameters can be stored by default in the `~/.angusdk/` directory.
The sdk provide a tools namely `angusme` that generates the directory and
configuration files::

  > angusme
  Please copy/paste your client_id (current: None): <your client_id>
  Please copy/paste your access_token(current: None): <your access_token>
  Configuration directory successfully created in (/home/yienyien/.angusdk), credentials can be modified there directly


Hello, world
------------

Here is a simple "Hello, world" example for Angus SDK (replace macgyver.jpg by your own image with a face to detect)::

     import angus

     conn = angus.connect()
     service = conn.services.get_service('face_detection', version=1)
     job = service.process({'image': open('./macgyver.jpg')})
     print job.result['faces']



Documentation
-------------

Connect to a angus.ai cloud
+++++++++++++++++++++++++++

Angus.ai provides a "resource oriented" API, each asset is represented as a
resource. It enables a good RESTful architecture.
But to increase usability, the SDK provides some wrappers for a more conventional
style. For example, to "connect" to the cloud, in a pure RESTful way, the SDK
provide a resource ``Root`` and you create a resource very easy like this:

.. code-block:: python

   myconf = Configuration()
   myconf.set_ca_path("/home/username/.angusdk/certificate.pem")
   myconf.set_credential("7f5933d2-cd7c-11e4-9fe6-490467a5e114",
                         "db19c01e-18e5-4fc2-8b81-7b3d1f44533b")
   root = Root(url="https://gate.angus.ai", conf=myconf)

If you are initialized your environment thanks to angusme, the resource ``Root``
find the default configuration:

.. code-block:: python

   root = Root()

If you prefer a more programatic style, the SDK provide a wrapper:

.. code-block:: python

   root = angus.connect()

Get services
++++++++++++

Once you have a ``Root`` resource, you can get a handle on a service. The
root resource has a ``services`` sub-resource that is the service list.
You can get one by using ``get_service`` method:

.. code-block:: python

   service = root.services.get_service('face_detection', 1)
   print(service.endpoint)

You get back a handler on the first version of "face_detection" service.
The version is optional, if it not provided, the last version is used.

Get a composite service
+++++++++++++++++++++++

The sdk provide you a convenient wrapper to call several service
at the same time:

.. code-block:: python

   services = root.services.get_services([('face_detection', 1), ('dummy', 2)])

You get back a service handler that enables using 'face_detection' and 'dummy'
services at the same time.
Versions are optional:

.. code-block:: python

   services = root.services.get_services(['face_detection', 'dummy'])

And service list are also optional, if it not provided, all services are used:

.. code-block:: python

   services = root.services.get_services()


Process a job
+++++++++++++

Each ``Service`` resource contains a jobs sub-resource that is the list of
processed jobs. This resource enables job manipulation (list, create, delete).
The SDK provides a easy way to create a new job:

.. code-block:: python

   parameters = { 'image': open('/tmp/macgyver.jpg', 'rb') }
   new_job = service.process(parameters)

The ``new_job`` object is a handler on the job resource created in the cloud.
This is exactly the same interface for composite services:

.. code-block:: python

   new_job = services.process(parameters)


Discussion and support
----------------------

You can discuss Angus SDK on `the Angus SDK developer mailing list <http://groups.google.com/group/angus-sdk-python>`_, and report bugs on the `GitHub issue tracker <https://github.com/angus-ai/angus-sdk-python/issues>`_.

This web site and all documentation is licensed under `Creative
Commons 3.0 <http://creativecommons.org/licenses/by/3.0/>`_.
