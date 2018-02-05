"""
tasks.py
Description:
    Threads & Async provider lib
Author:
    Ajeet Singh
Date:
    2/4/2018
"""
import threading
import asyncio
import aiojobs
import logging
from ui_builder.core import constants, init_log
from ui_builder.core.provider import id_mgr



#init logs ----------------------------
init_log.config_logs()
logger = logging.getLogger(__name__)

class HybridThread(threading.Thread):

    """HybridThread creates an dedicated thread for running async/coroutines on it.
        The thread keeps running until signalled to stop. It keeps checking for the
        coroutine queue and start executing same once an coroutine is added to queue.
    """

    def __init__(self, name=None, args=(), kwargs={}):
        """HybridThread constructor takes name, args and kwargs parameters.
            The args and kwargs will be used internally by this thread and will be
            passed to the :func:`run` function

            :param name: Name of the thread, usefull if you want to categorize coroutines
            :type name: str
            :param args: Parameters to be passed over to :func:`run` function
            :type args: tuple
            :param kwargs: Same as args but accepts only keyword arguments
            :type kwargs: dict

        """
        super(HybridThread, self).__init__(name=name, args=args, kwargs=kwargs)
        self._coroutines = []
        self._results = []
        self._lock = threading.Lock()
        self._result_lock = threading.Lock()
        self._loop = asyncio.new_event_loop()
        logger.info('HybridThread {0} has been init..')

    def loop():
        doc = "The asyncio :mod:`loop` instance created for this thread only. This is readonly property"
        def fget(self):
            return self._loop
        return locals()
    loop = property(**loop())

    def coroutines():
        doc = "All the coroutines registered with this thread. This is readonly property"
        def fget(self):
            return self._coroutines
        return locals()
    coroutines = property(**coroutines())

    def add_coroutine(self, coroutine, *args, **kwargs):
        """Adds a coroutine to queue which will be scheduled and executed by thread's event loop

        :param coroutine: The coroutine to be added in the queue
        :type coroutine: function
        :param args: Paramters that needs to be passed to the coroutine
        :type args: tuple
        :param kwargs: Keyword parameters for passing it to coroutine

        :returns: None

        The parameters args and kwargs should be passed to this method as shown below:
            >>> args = (10, 20, 30, 40)
            >>> kwargs = {'a': 1, 'b': 2, 'c': 3}
            >>> thread_instance = HybridInstance(name='MyThread')

            >>> async def my_coro(*args, **kwargs):
                    print('I am in coro')
                    asyncio.sleep(2)

            >>> thread_instance.add_coroutine(my_coro, *args, **kwargs)
        """
        if coroutine is not None:
            with self._lock:
                _task_details = (coroutine, args, kwargs)
                self._coroutines.append(_task_details)
                logger.debug('New coroutine added to thread...{0}'.format(coroutine))
        else:
            logger.error('Invalid reference to the coroutine provided')
            raise ValueError('Invalid reference to the coroutine provided')


    async def schedule_jobs(self):
        """TODO: Docstring for schedule_jobs.
        :returns:

        """
        scheduler = await aiojobs.create_scheduler()
        logger.debug('The job scheduler''s instance created')
        for coro_details in self.coroutines:
            coro = coro_details[0]
            args = coro_details[1]
            kwargs = coro_details[2]
            logger.debug('Coroutine with following details will be scheduled...{0}, {1}, {2}'.format(coro, args, kwargs))
            with self._result_lock:
                res = await scheduler.spawn(coro(*args, **kwargs))
                self._results.append(res)
                logger.debug('Coroutine scheduled and its result reference added to results property')

        logger.debug('Waiting for all coroutines to be finished')
        [await coro.wait() for coro in self._results]
        await scheduler.close()
        logger.debug('All coroutines have been finished')

    def run(self):
        """TODO: Docstring for start.

        :arg1: TODO
        :returns: TODO

        """
        asyncio.set_event_loop(self.loop)
        logger.debug('New event loop created for this thread')
        self.loop.run_until_complete(self.schedule_jobs())
        logger.debug('run_until_complete completed')


class ThreadManager(object):

    """Docstring for ThreadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.name = 'ThreadManager'
        self.id = id_mgr.get_id(self.name)


