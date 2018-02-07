"""
.. module:: tasks
   :platform: Unix, Windows
   :synopsis: Threads & Async provider lib

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
import threading
import asyncio
import logging
from ui_builder.core import constants, init_log
from ui_builder.core.provider import id_mgr
from ui_builder.core.constants import ThreadStatus

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

        Args:
            name (str): Name of the thread, usefull if you want to categorize coroutines
            *args: Parameters to be passed over to :func:`run` function
            **kwargs: Same as args but accepts only keyword arguments

        """
        super(HybridThread, self).__init__(name=name, args=args, kwargs=kwargs)
        self.can_thread_work = True
        self.have_coroutines = False
        self.status = ThreadStatus.STOPPED
        self.stop_thread = threading.Event()
        self.resume_thread = threading.Event()
        self._coroutines = []
        self._results = []
        self._jobs = []
        self._loop = asyncio.new_event_loop()
        logger.info('HybridThread {0} has been init..')

    def loop():
        doc = "The asyncio :attr:`~loop` instance created for this thread only. This is a readonly property"
        def fget(self):
            return self._loop
        return locals()
    loop = property(**loop())

    def coroutines():
        doc = "All the :attr:`~coroutines` registered with this thread. This is a readonly property"
        def fget(self):
            return self._coroutines
        return locals()
    coroutines = property(**coroutines())

    def results():
        doc = "Contains result from all the :attr:`~coroutines` in this thread"
        def fget(self):
            return self._results
        return locals()
    results = property(**results())

    def is_paused():
        doc = "The is_paused property returns the status of the thread"
        def fget(self):
            if not C.can_work:
                return True
            else:
                return False
        return locals()
    is_paused = property(**is_paused())

    def add_coroutine(self, coroutine, *args, **kwargs):
        """Adds a coroutine to queue which will be scheduled and executed by thread's event loop
        Args:
            coroutine (:obj:`func`): The coroutine to be added in the queue
            *args: Paramters that needs to be passed to the coroutine
            **kwargs: Keyword parameters for passing it to coroutine

        Returns:
            None

        Examples:
            The parameters args and kwargs should be passed to this method as shown below:

            >>> args = (10, 20, 30, 40)
            >>> kwargs = {'a': 1, 'b': 2, 'c': 3}
            >>> thread_instance = HybridThread(name='MyThread')

            >>> async def my_coro(*args, **kwargs):
                    print('I am in coro')
                    asyncio.sleep(2)

            >>> thread_instance.add_coroutine(my_coro, *args, **kwargs)
            >>> thread_instance.start(); thread_instance.join()
            I am in coro
        """
        if self.status != ThreadStatus.INVALID:
            if coroutine is not None:
                _task_details = (coroutine, args, kwargs)
                self._coroutines.append(_task_details)
                logger.debug('New coroutine added to thread...{0}'.format(coroutine))
            else:
                logger.error('Invalid reference to the coroutine provided')
                raise ValueError('Invalid reference to the coroutine provided')
        else:
            logger.error('Thread is in invalid state, can''t add more coroutines')

    def scheduler_exception_handler(self, scheduler, context):
        """Handles exception raised by any of the :attr:`coroutines` registered with the :attr:`scheduler`

        Args:
            scheduler (scheduler): Instance of the scheduler raising the exception
            context (dict): A dictionary containing following attributes::

                {
                    message
                    job
                    exception
                    source_traceback
                }

        Returns:
            None

        """
        logger.error('Error while scheduling job [{0}]. Please see below details...\nmessage: {1}\nexception:{2}\ntraceback:{3}'.format(context.job, context.message, context.exception, context.source_traceback))

    async def schedule_jobs(self):
        """Schedule all coroutines/jobs which are available in the :attr:`~coroutines`

        Returns:
            None

        """
        if self.scheduler is None:
            self._scheduler = await aiojobs.create_scheduler(exception_handler=self.scheduler_exception_handler)
        logger.debug('The job scheduler''s instance created')
        #lock the coro queue while scheduling all coro's to run
        with C.lock_coro_queue:
            self._jobs = []
            for coro_details in self.coroutines:
                coro = coro_details[0]
                args = coro_details[1]
                kwargs = coro_details[2]
                with C.lock_jobs_list:
                    job = await self.scheduler.spawn(coro(*args, **kwargs))
                    self._jobs.append(job)
        #lock the results list again while waiting for coro's to be finished
        #with C.lock_results_list:
            #self._results = [await job.wait() for job in self._jobs]
        #release the scheduler instance
        #await self.scheduler.close()
        #self._scheduler = None
        logger.debug('All coroutines have been finished')

    def run(self):
        """Executes the main :meth:`run` method of the class :class:`Thread`. This method will create a new event :attr:`loop` for this thread, schedule all the :attr:`coroutines` to run and waits for the completion of the :attr:`coroutines`
        Args:
            None

        Returns:
            None

        """
        while not self.stop_thread.isSet():
            while not self.resume_thread.isSet():
                self.resume_thread.wait()
            if self.loop is not None and self.loop.is_running() == False:
                asyncio.set_event_loop(self.loop)
                logger.debug('New event loop set for this thread')
                self.loop.run_forever()
                logger.debug('"run_until_complete" method finitshed successfully')
            else:
                msg='No event loop found for this thread - {0}.\nThe thread will be stopped immediately'.format(self.name)
                logger.error(msg)
                raise Exception(msg)

    def stop(self):
        """Stop the current thread and it's coroutines
        """
        if self.loop is not None:
            self.loop.stop()


class ThreadManager(object):

    """Docstring for ThreadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.name = 'ThreadManager'
        self.id = id_mgr.get_id(self.name)


