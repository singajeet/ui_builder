"""
.. module:: tasks
   :platform: Unix, Windows
   :synopsis: Threads & Async provider lib

.. moduleauthor:: Ajeet Singh <singajeet@gmail.com>
"""
import threading
import asyncio
import logging
import warnings
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
        self._is_internal_call = False
        self._stop_thread = threading.Event()
        self._pause_thread = threading.Event()
        self._block_coroutine_addition = threading.RLock()
        self._block_function_addition = threading.RLock()
        self._coroutines_q = []
        self._coro_results = []
        self._functions_q = []
        self._function_results = []
        self._loop = asyncio.new_event_loop()
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

        Examples:
            The parameters args and kwargs should be passed to this method as shown below:

            >>> args = (10, 20, 30, 40)
            >>> kwargs = {'a': 1, 'b': 2, 'c': 3}
            >>> thread_instance = HybridThread(name='MyThread')

            >>> async def my_coro(*args, **kwargs):
                    print('I am in coro')
                    asyncio.sleep(2)

            >>> thread_instance.add_coroutine(my_coro, *args, **kwargs)
            >>> thread_instance.start_forever() #; thread_instance.join() #join() if required
            I am in coro
        """
        self._block_coroutine_addition.acquire() 
        if coroutine is not None:
            _task_details = (coroutine, *args, **kwargs)
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

        Examples:
            The parameters args and kwargs should be passed to this method as shown below:

            >>> args = (10, 20, 30, 40)
            >>> kwargs = {'a': 1, 'b': 2, 'c': 3}
            >>> thread_instance = HybridThread(name='MyThread')

            >>> def my_func(*args, **kwargs):
                    print('I am in func')
                    time.sleep(2)

            >>> thread_instance.add_function(my_func, *args, **kwargs)
            >>> thread_instance.start_forever() #; thread_instance.join() #join() if required
            I am in func
        """
        self._block_function_addition.acquire()
        if function_def is not None:
            _func_details = (function_def, *args, **kwargs)
            self._functions_q.append(_func_details)
            logger.debug('Function added to thread...{0}'.format(function))
        else:
            logger.debug('Not a valid function definition')
            raise ValueError('Not a valid function definition')
        self._block_function_addition.release()

    def start(self):
        """Overwrite the :meth:`start` method so that it can be called from :class:`HybridThread` only.
        If called by another class, method or thread, :exc:`RuntimeError` will be thrown.
            Use :meth:`start_forever` method to start this thread
        """
        if self._is_internal_call:
            self._is_internal_call = False
            super(HybridThread, self).start()
        else:
            raise RuntimeError('Call to start is not allowed. Please use "start_forever()" for same')

    def start_forever(self):
        """Starts the thread, executes the coroutines and sync functions registered with this thread
        """
        if self.isAlive:
            if not self._is_thread_running:
                self._is_internal_call = True
                self.start()
                self._schedule()
        else:
            raise Exception('Thread is not alive and will not start again')

    def run(self):
        """ Executes the main :meth:`run` method of the class :class:`Thread`. 
            This method will create a new event :attr:`loop` for this thread, 
            and will run it forever. To stop the event loop and thread, 
            :meth:`stop` needs to be called

        Note:
            This method contains a loop that will run until :meth:`stop` is called.
            The loop will start the event loop if its not running and will go to
            waiting state while the event loop is running. In case event loop is
            stopped for any reason, the event loop can be started using 
            :meth:`schedule_again`. Calling :meth:`stop` will stop the event loop
            and thread and can''t be started again
        """
        self._is_thread_running = True
        #starts the main thread and keep running until :attr:`_stop_thread` event is called
        while not self._stop_thread.isSet():
            #if event loop is not running, start it forever
            if not self.loop.is_running():
                asyncio.set_event_loop(self.loop)
                logger.debug('New event loop set for this thread')
                self.loop.run_forever()
            #pause main thread as event loop is already running
            self._pause_thread.set()
            if self._pause_thread.isSet():
                self._pause_thread.wait()

    def _schedule(self):
        """Executes all callable objects (coroutines and functions) available in the queue
        """
        if self.loop is None:
            raise Exception('Loop is in invalid state')
        
        if len(self._coroutines_q) > 0:
            #run all coroutines
            for coro in self._coroutines_q:
                asyncio.run_coroutine_threadsafe(coro[0](coro[1], coro[2]), self.loop)
        
        if len(self._functions_q) > 0:
            #run all functions
            for func in self._functions_q:
                self.loop.call_soon_threadsafe(func[0](func[1], func[2]))

    def schedule_again(self):
        if not self.loop.is_running():
            self._pause_thread.clear()
        self._schedule()

    async def fake_call(self):
        logger.debug("Called fake call")

    def stop(self):
        """Stop the current thread and it's coroutines
        """
        if self.isAlive:
            if self.loop.is_running():
                self.loop.stop()
                asyncio.run_coroutine_threadsafe(fake_call(), self.loop)
            if self._is_thread_running:
                self._stop_thread.set()

class ThreadManager(object):

    """Docstring for ThreadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.name = 'ThreadManager'
        self.id = id_mgr.get_id(self.name)


