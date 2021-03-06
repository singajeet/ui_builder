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

    """
    .. attribute: Loop Types
    """
    THREAD_LOOP = 0
    EVENT_LOOP = 1

    """
    .. attribute: Callable Types
    """
    FUNCTIONS = 0
    COROUTINES = 1

    def __init__(self, name=None, owner=None, notify_on_all_done=None, notify_on_coroutine_done=None, notify_on_function_done=None, args=(), kwargs={}):
        """HybridThread constructor takes name, args and kwargs parameters.
        The args and kwargs will be used internally by this thread and will be
            passed to the :func:`run` function

        Args:
            name (str): Name of the thread, usefull if you want to categorize coroutines
            owner (str): Name of the owner who initiated the call
            notify_on_all_done (func): Calls back the :func:`notify_on_all_done` after all coroutines and functions are done. This callback will get 2 params - results of all coroutines or functions and type of callables called - coroutines or functions
            notify_on_coroutine_done (func): Calls back the :func:`notify_on_coroutine_done` after completion of each coroutine. Future instance will be passed to it as param
            notify_on_function_done (func): Same as :attr:`notify_on_coroutine_done` but it works for functions only
            *args: Parameters to be passed over to :func:`run` function
            **kwargs: Same as args but accepts only keyword arguments

        """
        super(HybridThread, self).__init__(name=name, args=args, kwargs=kwargs)
        self.__owner = owner
        self.__is_internal_call = False
        self.__stop_thread = threading.Event()
        self.__resume_thread = threading.Event()
        self.__all_coros_done_event = threading.Event()
        self.__all_funcs_done_event = threading.Event()
        self.__block_coroutine_addition = threading.RLock()
        self.__block_function_addition = threading.RLock()
        self._coroutines_q = []
        self._coro_results = []
        self.__coro_futures = []
        self._functions_q = []
        self._function_results = []
        self.__function_futures = []
        self.__notify_on_all_done = notify_on_all_done
        self.__notify_on_coroutine_done = notify_on_coroutine_done
        self.__coroutine_completed_percentage_callback = None
        self.__notify_on_function_done = notify_on_function_done
        self.__function_completed_percentage_callback = None
        self.__coroutine_counter = 0
        self.__function_counter = 0
        self._loop = asyncio.new_event_loop()
        self._is_thread_running = False
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
    coroutines_results = property(**coroutine_results())

    def is_thread_running():
        doc = "The is_thread_running property."
        def fget(self):
            return self._is_thread_running
        return locals()
    is_thread_running = property(**is_thread_running())

    def register_notify_on_coroutine_completed(self, coroutine_completed_callback):
        """Registers an function passed as parameter to this method to be called everytime an coroutine is completed
        Args:
            coroutine_completed_callback (func): Function to be called on completion of coroutine
        """
        self.__notify_on_coroutine_done = coroutine_completed_callback

    def register_coroutine_completed_percentage(self, percentage_completed_callback):
        """Registers an callback function passed as parameter to this method to be called everytime an coroutine is completed. The callback function will receive an parameter which will provide the percentage of coroutines completed from total number of coroutines. Below is the formula for calculating the percentage::

            >>> coroutine_completed_percentage = ((number_of_coroutines_completed / total_number_of_coroutines_in_queue) * 100)

            The callback function should have the following signature::

                >>> def percentage_completed_callback(percentage_of_completion):
                    pass

        """
        self.__coroutine_completed_percentage_callback = percentage_completed_callback

    def register_notify_on_function_completed(self, function_completed_callback):
        """Registers an function passed as parameter to this method to be called everytime an function is completed
        Args:
            function_completed_callback (func): Function to be called on completion of functions in queue
        """
        self.__notify_on_function_done = function_completed_callback

    def register_function_completed_percentage(self, percentage_completed_callback):
        """Registers an callback function passed as parameter to this method to be called everytime an function is completed. The callback function will receive an parameter which will provide the percentage of functions completed from total number of functions in queue. Below is the formula for calculating the percentage::

            >>> function_completed_percentage = ((number_of_functions_completed / total_number_of_functions_in_queue) * 100)

            The callback function should have the following signature::

                >>> def percentage_completed_callback(percentage_of_completion):
                    pass

        """
        self.__function_completed_percentage_callback = percentage_completed_callback

    def set_owner(self, owner_name):
        """ Sets the owner of the thread and same will be passed to the coro and function completion callbacks

        Args:
            owner_name (str): Name of the owner of the thread
        """
        self.__owner = owner_name

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
        self.__block_coroutine_addition.acquire()
        if coroutine is not None:
            _task_details = (coroutine, args, kwargs)
            self._coroutines_q.append(_task_details)
            logger.debug('New coroutine added to thread...{0}'.format(coroutine))
        else:
            logger.error('Invalid reference to the coroutine provided')
            raise ValueError('Invalid reference to the coroutine provided')
        self.__block_coroutine_addition.release()

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
        self.__block_function_addition.acquire()
        if function_def is not None:
            _func_details = (function_def, args, kwargs)
            self._functions_q.append(_func_details)
            logger.debug('Function added to thread...{0}'.format(function))
        else:
            logger.debug('Not a valid function definition')
            raise ValueError('Not a valid function definition')
        self.__block_function_addition.release()

    def start(self):
        """Overwritten :meth:`start` method! Can be called internally only by this class members.
        If called by another class, method or thread, :exc:`RuntimeError` will be thrown.
        Use :meth:`start_forever` method to start this thread
        """
        if self.__is_internal_call:
            self.__is_internal_call = False
            super(HybridThread, self).start()
            self.__schedule()
        else:
            raise RuntimeError('Call to start is not allowed. Please use "start_forever()" for same')

    def start_forever(self):
        """Starts the thread, executes the coroutines and sync functions registered with this thread
        """
        if self.isAlive:
            self.__is_internal_call = True
            self.start()
        else:
            raise Exception('Thread is not alive and will not start again')

    def __coroutine_done_cb(self, future):
        """Coroutine done callback will be called once for each coroutine in queue.
            An instance of furure will be passed to this callback

        Args:
            future (Future): An instance of :mod:`asyncio`.:class:`Future`
        """
        self.__coroutine_counter += 1
        if self.__notify_on_coroutine_done is not None:
            self.__notify_on_coroutine_done(future, self.__owner)
        if self.__coroutine_completed_percentage_callback is not None:
            self.__coroutine_completed_percentage_callback((self.__coroutine_counter/len(self._coroutines_q))*100)
        if len(self._coroutines_q) == self.__coroutine_counter and self.__notify_on_all_done is not None:
            self._coro_results = [future.result() for future in self.__coro_futures]
            self.__notify_on_all_done(self._coro_results, self.__owner, HybridThread.COROUTINES)

    def wait_for_all_coroutines(self):
        """Blocks the call until all the coroutines are finished.Once coroutines are done,
            it clears the coroutines queue so that new can be added for another run
        """
        if not self.__all_coros_done_event.isSet():
            self.__all_coros_done_event.wait()
            self._coroutines_q.clear()

    def __function_done_cb(self, future):
        """Function done callback will be called once for each function in queue.
            An instance of furure will be passed to this callback

        Args:
            future (Future): An instance of :mod:`asyncio`.:class:`Future`
        """
        self.__function_counter += 1
        if self.__notify_on_function_done is not None:
            self.__notify_on_functon_done(future, self.__owner)
        if self.__function_completed_percentage_callback is not None:
            self.__function_completed_percentage_callback((self.__function_counter/len(self._function_q))*100)
        if len(self._functions_q) == self.__function_counter and self.__notify_on_all_done is not None:
            self._function_results = [future.result() for future in self.__function_futures]
            self.__notify_on_all_done(self._function_results, self.__owner, HybridThread.FUNCTIONS)

    def wait_for_all_functions(self):
        """Blocks the call until all the functions are finished. Once all the functions are done,
            it clears the function queue do that new can be added for another run
        """
        if not self.__all_funcs_done_event.isSet():
            self.__all_funcs_done_event.wait()
            self._functions_q.clear()

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
        while not self.__stop_thread.isSet():
            self.__resume_thread.clear() #<--This makes sure, thread will go in wait
            # if event loop is not running, start it forever
            if not self.loop.is_running():
                asyncio.set_event_loop(self.loop)
                logger.debug('New event loop set for this thread')
                self.loop.run_forever() #<-- Call blocked until event loop is stopped

            # The blocking call to "loop.run_forever" from previous line has been done,
            # so we will wait until we get another request to resume and restart the
            # event loop
            if not self.__resume_thread.isSet():
                self.__resume_thread.wait()

    def __schedule(self):
        """Executes all callable objects (coroutines and functions) available in the queue
        """
        if self.loop is None:
            raise Exception('Loop is in invalid state')
        if len(self._coroutines_q) > 0:
            self.__coro_futures.clear()
            self._coro_results.clear()
            self.__coroutine_counter = 0
            self.__all_coros_done_event.clear()
            #run all coroutines
            for coro in self._coroutines_q:
                future = asyncio.run_coroutine_threadsafe(coro[0](*coro[1], **coro[2]), self.loop)
                future.add_done_callback(self.__coroutine_done_cb)
                self.__coro_futures.append(future)
        if len(self._functions_q) > 0:
            self.__function_futures.clear()
            self._function_results.clear()
            self.__function_counter = 0
            self.__all_funcs_done_event.clear()
            #run all functions
            for func in self._functions_q:
                future = self.loop.call_soon_threadsafe(func[0](*func[1], **func[2]))
                future.add_done_callback(self.__function_done_cb)
                self.__function_futures.append(future)

    def reschedule(self):
        """Rerun the event loop if its stopped and schedule all callables again to run
        """
        if not self.loop.is_running():
            self.__resume_thread.set()
        self.__schedule()

    async def _fake_call(self):
        logger.debug("Called fake call")
        await asyncio.sleep(0.5)

    def stop_event_loop(self):
        """Stop the event loop if it is running
        """
        if self.loop.is_running():
            self.loop.stop()
            # Hack to force event loop to complete its last loop by calling an
            # empty coroutine
            asyncio.run_coroutine_threadsafe(self._fake_call(), self.loop)

    def stop(self):
        """Stop the main thread loop
        """
        if self.isAlive:
            self.stop_event_loop()
            self.__stop_thread.set() #<-- it will break the thread's while loop
            self.__resume_thread.set() #<-- make sure the thread loop don''t go into wait


class ThreadManager(object):

    """Docstring for ThreadManager. """

    def __init__(self):
        """TODO: to be defined1. """
        self.name = 'ThreadManager'
        self.id = id_mgr.get_id(self.name)


