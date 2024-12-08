import asyncio
# from gc import freeze
from threading import  Thread
from traceback import format_exc
from typing import Callable, Coroutine
from asyncio import Future

import logging

logger = logging.getLogger(__name__)
# class ThreadCoroutineRunner:
#     def __init__(self, interval: int): #interval time in milliseconds
#         self.loop = asyncio.new_event_loop()
#         self.thread_ = Thread(daemon=False, target=self.loop.run_forever)
#         self.thread_.start()
#         self.interval = interval
#         self.stop_flag = False
#
#     def stop(self) -> None:
#         self.stop_flag = True
#
#     def __del__(self):
#         self.stop()
#         self.loop.close()

class ThreadRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread_ = Thread(daemon=True, target=self.loop.run_forever)
        self.thread_.start()

    def __del__(self):
        try:
            # self.stop()
            self.loop.stop()
        except Exception as ex:
            print('exception while closing loop')
            print(ex.args)
        finally:
            self.loop.close()

class DelayedCoroutineRunner(ThreadRunner):
    def __init__(self, interval: int): #interval time in milliseconds
        ThreadRunner.__init__(self)
        self.interval = interval

class SaveDataCoroutineRunner(ThreadRunner):
    def callback(self, ftr: Future) -> None:
        try:
            #use result() to obtain real result or exception
            res = ftr.result()
        except Exception as ex:
            print(f'exception in callback with reason: {ex.args}')

    def start(self, coro: Coroutine, *args) -> Future:
        try:
            fut = asyncio.run_coroutine_threadsafe(coro(*args), self.loop)
            fut.add_done_callback(self.callback)
            return fut
        except Exception as ex:
            print(ex.args)


class GameTimer(DelayedCoroutineRunner):

    def __init__(self, interval: int ):
        DelayedCoroutineRunner.__init__(self, interval)
        self.stop_flag = False

    # async def sleep_and_run(self, coro: Callable[[], None]) -> None:
    async def sleep_and_run(self, coro) -> None:
        try:
            period = float(self.interval) / 1000
            while not self.stop_flag:
                await asyncio.sleep(period)
                await coro()
        except Exception as ex:
            logger.exception(format_exc())

    def start(self, coro: Callable[[], None]) -> None:
        asyncio.run_coroutine_threadsafe(self.sleep_and_run(coro), self.loop)

    def stop(self) -> None:
        self.stop_flag = True