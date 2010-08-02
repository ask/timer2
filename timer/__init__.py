"""Timer - Scheduler for Python functions."""

from __future__ import generators

import atexit
import heapq
import warnings

from threading import Thread, Event
from time import time, sleep, mktime

from datetime import datetime, timedelta

VERSION = (0, 1, 0)
__version__ = ".".join(map(str, VERSION))
__author__ = "Ask Solem"
__contact__ = "ask@celeryproject.org"
__homepage__ = "http://github.com/ask/timer/"
__docformat__ = "restructuredtext"

DEFAULT_MAX_INTERVAL = 2

class TimedFunctionFailed(UserWarning):
    pass


class Entry(object):
    cancelled = False

    def __init__(self, fun, args, kwargs):
        self.fun = fun
        self.args = args or []
        self.kwargs = kwargs or {}
        self.tref = self

    def __call__(self):
        try:
            return self.fun(*self.args, **self.kwargs)
        except Exception, exc:
            warnings.warn(repr(exc), TimedFunctionFailed)

    def cancel(self):
        self.tref.cancelled = True


class Schedule(object):
    """ETA scheduler."""

    def __init__(self, max_interval=DEFAULT_MAX_INTERVAL):
        self.max_interval = float(max_interval)
        self._queue = []

    def enter(self, item, eta=None, priority=0):
        """Enter item into the scheduler.

        :param item: Item to enter.
        :param eta: Scheduled time as a :class:`datetime.datetime` object.
        :param priority: Unused.
        :param callback: Callback to call when the item is scheduled.
            This callback takes no arguments.

        """
        if isinstance(eta, datetime):
            try:
                eta = mktime(eta.timetuple())
            except OverflowError:
                pass
        eta = eta or time()
        heapq.heappush(self._queue, (eta, priority, item))
        return item

    def __iter__(self):
        """The iterator yields the time to sleep for between runs."""

        # localize variable access
        nowfun = time
        pop = heapq.heappop

        while 1:
            if self._queue:
                eta, priority, item = verify = self._queue[0]
                now = nowfun()

                if now < eta:
                    yield min(eta - now, self.max_interval)
                else:
                    event = pop(self._queue)

                    if event is verify:
                        if not item.cancelled:
                            item()
                        continue
                    else:
                        heapq.heappush(self._queue, event)
            yield None

    def empty(self):
        """Is the schedule empty?"""
        return not self._queue

    def clear(self):
        self._queue = []

    def info(self):
        return ({"eta": eta, "priority": priority, "item": item}
                    for eta, priority, item in self.queue)

    @property
    def queue(self):
        return map(heapq.heappop, [list(self._queue)]*len(events))


class Timer(Thread):
    Entry = Entry

    precision = 0.3
    running = False

    def __init__(self, schedule=None):
        self.schedule = schedule or Schedule()

        Thread.__init__(self)
        self._scheduler = iter(self.schedule)
        self._shutdown = Event()
        self._stopped = Event()
        self.setDaemon(True)

    def run(self):
        self.running = True
        while not self._shutdown.isSet():
            self.tick()
        self._stopped.set()

    def tick(self):
        delay = self._scheduler.next()
        sleep(delay or self.precision)

    def stop(self):
        if self.running:
            self._shutdown.set()
            self._stopped.wait()
            self.join(1e100)

    def enter(self, entry, eta, priority=None):
        if not self.running:
            self.start()
        return self.schedule.enter(entry, eta, priority)

    def apply_at(self, eta, fun, args=(), kwargs={}, priority=0):
        return self.enter(self.Entry(fun, args, kwargs), eta, priority)

    def enter_after(self, msecs, entry, priority=0):
        eta = datetime.now() + timedelta(seconds=msecs / 1000.0)
        return self.enter(entry, eta, priority)

    def apply_after(self, msecs, fun, args=(), kwargs={}, priority=0):
        return self.enter_after(msecs, Entry(fun, args, kwargs), priority)

    def apply_interval(self, msecs, fun, args=(), kwargs={}, priority=0):
        tref = Entry(fun, args, kwargs)

        def _reschedules(*args, **kwargs):
            try:
                return fun(*args, **kwargs)
            finally:
                self.enter_after(msecs, tref, priority)

        tref.fun = _reschedules
        return self.enter_after(msecs, tref, priority)

    def exit_after(self, msecs, priority=10):
        self.apply_after(msecs, sys.exit, priority)

    def cancel(self, tref):
        tref.cancel()

_default_timer = Timer()
apply_after = _default_timer.apply_after
apply_at = _default_timer.apply_at
apply_interval = _default_timer.apply_interval
enter_after = _default_timer.enter_after
enter = _default_timer.enter
exit_after = _default_timer.exit_after
cancel = _default_timer.cancel

atexit.register(_default_timer.stop)
