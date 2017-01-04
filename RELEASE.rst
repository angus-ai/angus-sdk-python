Angus python SDK - Release Note v0.0.11
=======================================

Bug fixed
---------

* Typo in default configuration loader


Angus python SDK - Release Note v0.0.11
=======================================

Bug fixed
---------

* Update support information

Features added
--------------

* Add global timeout for a connection
* Enable mjpeg streaming


Angus python SDK - Release Note v0.0.10
=======================================

Bug fixed
---------

* angusme is now working properly when called for the first time

Features added
--------------

* None

Angus python SDK - Release Note v0.0.9
======================================

Bug fixed
---------

* it is now possible to use sessions and composite services

Features added
--------------

* enabling client side asynchronous calls
* it is now easier to set credentials programmatically


Angus python SDK - Release Note v0.0.8
======================================

Bug fixed
---------

* None

Features added
--------------

* angusme enable gateway modification

Angus python SDK - Release Note v0.0.7
======================================

Bug fixed
---------

* Fixed Python 3 compatibility of composite calls.
* When using composites, return json is now much simpler.

Features added
--------------

* Parameters initially passed in ``process()`` can now be passed in ``enable_session()``.
* Add a test function in angusme to check sucessful SDK installation.


Angus python SDK - Release Note v0.0.6
======================================

Bug fixed
---------

* Raising an exception when the service called does not exist.
* Raising an exception when the sdk is not correctly configured.


Features added
--------------

* The sdk is now Python 3 compatible.
* It is now possible to call multiple services in one call (see `Composite services <http://angus-doc.readthedocs.org/en/latest/sdk/python-sdk/guide.html#composite-services>`_)
* It is now possible to make multiple calls inside a session (see `Working with a session <http://angus-doc.readthedocs.org/en/latest/sdk/python-sdk/guide.html#session-for-statefull-services>`_).
