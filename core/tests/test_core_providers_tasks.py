import asyncio
import logging
import cmd
from ui_builder.core import init_log
from ui_builder.core.provider import tasks


init_log.config_logs()
logger = logging.getLogger(__name__)


async def coro1():
    logger.debug('coro1 started...')
    print('coro1 started...')
    await asyncio.sleep(5)
    logger.debug('coro1 ended....')
    print('coro1 ended...')

async def coro2():
    logger.debug('coro2 started...')
    print('coro2 started...')
    await asyncio.sleep(4)
    logger.debug('coro2 ended....')
    print('coro2 ended...')

async def coro3():
    logger.debug('coro3 started...')
    print('coro3 started...')
    await asyncio.sleep(3)
    logger.debug('coro3 ended....')
    print('coro3 ended...')

async def coro4():
    logger.debug('coro4 started...')
    print('coro4 started...')
    await asyncio.sleep(2)
    logger.debug('coro4 ended....')
    print('coro4 ended...')

class Prompt(cmd.Cmd):
    def start(self):
        logger.debug('StartCMD: Starting up the thread...')
        self.t = tasks.HybridThread(name='MyThread')
        self.t.add_coroutine(coro1)
        self.t.add_coroutine(coro2)
        self.t.add_coroutine(coro3)
        self.t.add_coroutine(coro4)
        self.t.start()
        self.t.join()
        logger.debug('Thread started!')

    def pause(self):
        logger.debug('PauseCMD: Pausing thead...')
        self.t.pause()
        logger.debug('Thread paused')

    def resume(self):
        logger.debug('ResumeCMD: Resuming thread...')
        self.t.resume();
        logger.debug('Thread resumed')

    def results(self):
        logger.debug('ResultsCMD: Display results...')
        print(self.t.results)
        logger.debug('Results printed')

    def exit(self):
        logger.debug('StopCMD: Stopping thread...')
        self.t.stop()
        logger.debug('Thread stopped')
        logger.debug('System Exit')
        raise SystemExit

if __name__=='__main__':
    prompt = Prompt()
    prompt.prompt = '>'
    prompt.cmdloop('Starting tasks tester. Type help for more....')

