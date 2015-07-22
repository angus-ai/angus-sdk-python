Angus python SDK - Release Note v0.0.7
======================================

Bug fixed
---------

* Fixed Python 3 compatibility of composite calls.
* When using composites, return json is now much simpler.

Features added
--------------

* Parameters initially passed in ``process()`` can now be passed in ``enable_session()``.


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
