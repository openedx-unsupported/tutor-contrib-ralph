ralph plugin for `Tutor <https://docs.tutor.overhang.io>`__
===================================================================================

Installs the `Ralph <https://github.com/openfun/ralph>`__ Learning Records System (LRS).

Installation
------------

The Ralph LRS relies on a couple other Tutor plugins:

::

    pip install git+https://github.com/openedx/tutor-contrib-ralph
    pip install git+https://github.com/openedx/tutor-contrib-clickhouse
    pip install git+https://github.com/openedx/tutor-contrib-oars

Usage
-----

1. Enable the plugins::

    tutor plugins enable clickhouse
    tutor plugins enable oars
    tutor plugins enable ralph

2. Save the changes to the environment::

    tutor config save

3. Run the initialization scripts in your chosen environment (dev or local)::

    tutor [dev|local] do init


License
-------

This software is licensed under the terms of the AGPLv3.
