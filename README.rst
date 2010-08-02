#############################################
 timer - Schedule Python functions.
#############################################

:Version: 0.1.0

Introduction
------------

The timer module lets you schedule Python functions at specific times,
or at an interval. It can be used as a replacement to ``threading.Timer``,
the difference is that ``timer`` is always only using a single thread (unless
you manually start more of them)

Documentation
-------------

Timer is using Sphinx, and the latest documentation is available at GitHub:

    http://ask.github.com/timer

Installation
============

You can install ``timer`` either via the Python Package Index (PyPI)
or from source.

To install using ``pip``,::

    $ pip install timer

To install using ``easy_install``,::

    $ easy_install timer


If you have downloaded a source tarball you can install it
by doing the following,::

    $ python setup.py build
    # python setup.py install # as root


Examples
========

Apply function after ``n`` msecs::

    >>> import timer
    >>> timer.apply_after(msecs, fun, args, kwargs, priority=0)

Apply function every ``n`` msecs::

    >>> timer.apply_interval(msecs, fun, args, kwargs, priority=0)

Apply function at a specific date (a ``datetime`` object)::

    >>> timer.apply_at(datetime, fun, args, kwargs, priority=0)

Cancelling timers
-----------------

The ``apply_*`` functions returns a ``timer.Entry`` instance,
you can use this to cancel the execution::

    >>> tref = timer.apply_after(msecs, fun, args, kwargs)
    >>> tref.cancel()


Running custom ``Timer`` threads
--------------------------------

When using the module interface a default timer thread is started
as soon as you schedule something. If you want to keep track of the
thread manually, you can use the ``timer.Timer`` class::

    >>> timer = timer.Timer()
    >>> timer.apply_after(msecs, fun, args, kwargs)
    >>> timer.stop() # stops the thread and joins it.

Bug tracker
===========

If you have any suggestions, bug reports or annoyances please report them
to our issue tracker at http://github.com/ask/timer/issues/

Contributing
============

Development of ``timer`` happens at Github: http://github.com/ask/timer

You are highly encouraged to participate in the development. If you don't
like Github (for some reason) you're welcome to send regular patches.

License
=======

This software is licensed under the ``New BSD License``. See the ``LICENSE``
file in the top distribution directory for the full license text.
