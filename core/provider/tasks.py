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
        self._is_thread_running = False
        self._start_loop = threading.Event()
        self._stop_thread = threading.Event()
        self._pause_thread = threading.Event()
        self._block_coroutine_addition = threading.RLock()
        self._block_function_addition = threading.RLock()
        self._coroutines_q = []
        self._coro_results = []
        self._functions_q = []
        self._function_results = []
        self._jobs = []
        self._loop = asyncio.new_event_loop()
        #thread will be in pause status initially and will resume
        #once coroutines or function are added and start_forever() is
        #called
        self._pause_thread.set()
        logger.info('HybridThread {0} has been init..')

    def loop():
        doc = "The asyncio :attr:`~loop` instance created for this thread only. This is a readonly property"
        def fget(self):
            return self._loop
        return locals()
    loop = property(**loop())

    def functions():
        doc="List of sync functions that will execute in this thread"
        def fget(self):
            return self._functions_q
        return locals()
    functions = property(**functions())

    def function_results():
        doc="Contains result of the sync functions executed in this thread"
        def fget(self):
            return self._function_results
        return locals()
    function_results = property(**function_results())

    def coroutines():
        doc = "All the :attr:`~coroutines` registered with this thread. This is a readonly property"
        def fget(self):
            return self._coroutines_q
        return locals()
    coroutines = property(**coroutines())

    def coroutine_results():
        doc = "Contains result from all the :attr:`~coroutines` in this thread"
        def fget(self):
            return self._coro_results
        return locals()
    results = property(**results())

    def is_thread_running():
        doc = "The is_thread_running property."
        def fget(self):
            return self._is_thread_running
        return locals()
    is_thread_running = property(**is_thread_running())

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
        self._block_coroutine_addition.acquire() 
        if coroutine is not None:
            _task_details = (coroutine, args, kwargs)
            self._coroutines_q.append(_task_details)
            logger.debug('New coroutine added to thread...{0}'.format(coroutine))
        else:
            logger.error('Invalid reference to the coroutine provided')
            raise ValueError('Invalid reference to the coroutine provided')
        self._block_coroutine_addition.release()

    def add_function(self, function_def, *args, **kwargs):
        """Adds a function to queue which will be scheduled and executed by thread's event loop
        Args:
            function_def (:obj:`func`): The function definition to be added in the queue
            *args: Paramters that needs to be passed to the function
            **kwargs: Keyword parameters for passing it to function

        Returns:
            None

        """
        self._block_function_addition.acquire()
        if function_def is not None:
            _func_details = (function_def, args, kwargs)
            self._functions_q.append(_func_details)
            logger.debug('Function added to thread...{0}'.format(function))
        else:
            logger.debug('Not a valid function definition')
            raise ValueError('Not a valid function definition')
        self._block_function_addition.release()

    def start_forever(self):
        """Starts the thread, executes the coroutines and sync functions registered with this thread
        
        Args:
            None

        Returns:
            None

        """
        if self.isAlive:
            
            if len(self._coroutines_q) > 0 or len(self._functions_q) > 0:
                self._resume_main_thread()
            else:
                raise Exception('No coroutines or functions available to run')

            if self._is_thread_running == False:
                super(HybridThread, self).start()
        else:
            raise Exception('Thread is not alive and will not start again')

    def run(self):
        """Executes the main :meth:`run` method of the class :class:`Thread`. This method will create a new event :attr:`loop` for this thread, schedule all the :attr:`coroutines` to run and waits for the completion of the :attr:`coroutines`
        Args:
            None

        Returns:
            None

        """
        self._is_thread_running = True
        while not self._stop_thread.isSet():
        if len(self._coroutines_q) > 0 or len(self._functions_q) > 0:
            self._run_coro_and_func_in_loop()
            if len(self._coroutines_q) <=0 and len(self._functions_q) <= 0:
                self._pause_main_thread()

    def _pause_main_thread(self):
        """TODO: Docstring for _pause_main_thread.
        :returns: TODO

        """
        while self._pause_thread.isSet():
            self._pause_thread.wait()

    def _resume_main_thread(self):
        """TODO: Docstring for _resume_main_thread.
        :returns: TODO

        """
        self._pause_thread.clear()

    def _run_coro_and_func_in_loop(self):
        if self.loop is not None and self.loop.is_running() == False:
            asyncio.set_event_loop(self.loop)
            logger.debug('New event loop set for this thread')
        elif self.loop is None:
            raise Exception('Loop is invalid state')
        elif self.loop.is_running():
            #do nothing
            logger.debug('Event loop is already running')

        if len(self._coroutines_q) > 0:
            coro_list=[]
            for coro in self._coroutines_q:
                coro_list.append(coro[0](*coro[1], **coro[2]))
            self.loop.run_until_complete(asyncio.gather(*coro_list))
                logger.debug('"run_until_complete" method finished successfully')
        if len(self._functions_q) > 0:
                for f in self._functions_q:
                    func_def = f[0]
                    args = f[1]
                    kwargs == f[2]
                    self.loop.call_soon(func_def(*args, **kwargs))
                logger.debug('All functions have been called')

        if self.loop.is_running() and not self.loop.is_closed():
            self.loop.stop()
            logger.debug('Loop has been stopped after completion of coro and func queues')

    def stop(self):
        """Stop the current thread and it's coroutines
        """
        if self.isAlive:
            if self._is_thread_running and not self._stop_thread.isSet():
                self._stop_thread.set()

class ThreadManager(object):

    """Docstring for ThreadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.name = 'ThreadManager'
        self.id = id_mgr.get_id(self.name)


