"""
..  module:: tasks
    :platform: Unix, Windows
    :synopsis: Threads & Async provider lib

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
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

class G(object):

    """Contains condition and flag to pause/resume an thread 
    
    Attributes:
        tcond (Condition): An object of :class:`Condition` to notify instance of :class:`Thread`
        can_work (bool): Determines whether an thread can execute or should wait for the notification
        lock_coro_queue (Lock): An object of :class:`Lock` to lock coroutine queues while adding/removing coroutines from queue
        lock_result_list (Lock): Used to lock the shared **results** list of an thread
    """
    tcond = threading.Condition()
    can_work = False
    lock_coro_queue = threading.Lock()
    lock_results_list = threading.Lock()


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
        self._coroutines = []
        self._results = []
        self._loop = asyncio.new_event_loop()
        logger.info('HybridThread {0} has been init..')

    def loop():
        doc = "The asyncio :attr:`loop` instance created for this thread only. This is a readonly property"
        def fget(self):
            return self._loop
        return locals()
    loop = property(**loop())

    def coroutines():
        doc = "All the coroutines registered with this thread. This is a readonly property"
        def fget(self):
            return self._coroutines
        return locals()
    coroutines = property(**coroutines())

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
        if coroutine is not None:
            with G.lock_coro_queue:
                _task_details = (coroutine, args, kwargs)
                self._coroutines.append(_task_details)
                logger.debug('New coroutine added to thread...{0}'.format(coroutine))
        else:
            logger.error('Invalid reference to the coroutine provided')
            raise ValueError('Invalid reference to the coroutine provided')

    async def schedule_jobs(self):
        """Schedule all coroutines/jobs which are available in the :attr:`~coroutines`

        Returns: 
            None

        """
        scheduler = await aiojobs.create_scheduler()
        logger.debug('The job scheduler''s instance created')
        for coro_details in self.coroutines:
            coro = coro_details[0]
            args = coro_details[1]
            kwargs = coro_details[2]
            with G.lock_results_list:
                res = await scheduler.spawn(coro(*args, **kwargs))
                self._results.append(res)

        [await coro.wait() for coro in self._results]
        await scheduler.close()
        logger.debug('All coroutines have been finished')

    def run(self):
        """Executes the main :meth:`run` method of the class :class:`Thread`.
            This method will create a new event :attr:`loop` for this thread,
            schedule all the :attr:`coroutines` to run and waits for the 
            completion of the :attr:`coroutines`

        Args:
            None

        Returns: 
            None

        """
        asyncio.set_event_loop(self.loop)
        logger.debug('New event loop created for this thread')
        self.loop.run_until_complete(self.schedule_jobs())
        logger.debug('"run_until_complete" method finitshed successfully')

    def toggle_pause(self):
        """Toogle the :attr:`G.tcond` property of thread to pause of resume thread
        """
        if G.can_work == True:
            G.can_work = False
            G.tcond.notify()
        else:
            G.can_work = True
            G.tcond.notify()

class ThreadManager(object):

    """Docstring for ThreadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.name = 'ThreadManager'
        self.id = id_mgr.get_id(self.name)


