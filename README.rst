THIS REPOSITORY IS DEPRECATED
=============================

This functionality now lives in `tutor-contrib-oars <https://github.com/openedx/tutor-contrib-oars>`__ as we work to consolidate the Open edX analytics functionality into one place.

This repository was experimental as we worked on OARS and will be archived soon.

ralph plugin for `Tutor <https://docs.tutor.overhang.io>`__
===================================================================================

Runs `Ralph <https://github.com/openfun/ralph>`__ Learning Records System (LRS) in the Tutor environment.

This plugin is speculative and being used to test new Open edX analytics features. It is not configured for production use at this time, use at your own risk!

See https://github.com/openedx/openedx-oars for more details.

This plugin is intended to be used with the `tutor-contrib-oars <https://github.com/openedx/tutor-contrib-oars>`__ plugin but can be used independently.

Installation
------------

::

    pip install git+https://github.com/openedx/tutor-contrib-ralph


Compatibility
-------------

This plugin is compatible with Tutor 15.0.0 and later.


Usage
-----

1. Enable the plugins::

    tutor plugins enable ralph

2. Optionally, you can allow the LRS API to accesible by domain by setting the following variables in you **config.yml** (only if you are running **tutor local**):

    RALPH_ENABLE_PUBLIC_URL: true
    RALPH_HOST: ralph.local.overhang.io

3. Save the changes to the environment::

    tutor config save

4. Run the initialization scripts in your chosen environment (dev or local)::

    tutor [dev|local] do init


If you are operating Ralph service in a different environment than the one you are
running Tutor, you can set the following variables in your **config.yml**:

.. code-block:: yaml

    RUN_RALPH: false
    RALPH_HOST: <ralph host>
    RALPH_RUN_HTTPS: true|false
    RALPH_LMS_USERNAME: <ralph lms username>
    RALPH_LMS_PASSWORD: <ralph lms password>

License
-------

This software is licensed under the terms of the AGPLv3.
