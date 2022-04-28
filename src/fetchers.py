from time import time
from data_models import HistoricTelemetry, MapState
from threading import Thread
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
from collections.abc import Callable
from os import getenv


class DataThread:
    '''
    # DataThread
    A wrapper class to an asynchronous data-fetching thread.
    The thread feeds a HistoricTelemetry object, accessible as a property of this
    classes' objects called 'telemetry'.
    '''

    def __init__(
        self,
        rate: float = 1.0,
        buffer_size: int = 100,
        max_concurrent_requests: int = 10,
        timeout: float = 1.0
    ) -> None:

        if rate <= 0:
            raise Exception('Rate must be bigger than zero.')

        self.telemetry = HistoricTelemetry(buffer_size)
        self.map = MapState()

        # Request loop params
        self.rate = rate
        self.max_requests = max_concurrent_requests
        self.timeout = timeout
        self.start_time = time()

        # Determine game's API url
        self.host = 'host.docker.internal' if getenv('DOCKER_DESKTOP') == 'y' else "http://localhost"
        self.port = '8111'

        self.thread = Thread(target=self.start_loop, daemon=True)
        self.thread.start()

    def start_loop(self):
        '''
        # DataThread
        ## Start Loop
        This is the target to the thread spawned in this classes __init__ method. This
        method starts an async loop by calling update_loop.
        '''

        asyncio.run(self.update_loop())

    async def update_loop(self) -> None:
        '''
        # DataThread
        ## Update Loop
        This method is the main async coroutine of this class.
        It handles the control of the rate of http requests made.
        '''

        semaphore = asyncio.Semaphore(value=self.max_requests)
        limiter = AsyncLimiter(1, 1/self.rate)
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=0.2))

        async with session:
            self.session = session

            while True:

                async with limiter:
                    await semaphore.acquire()

                    asyncio.create_task(self.fetch_data(
                        f"http://{self.host}:{self.port}/state",
                        semaphore,
                        self.telemetry.state_from_json)
                    )

                async with limiter:
                    await semaphore.acquire()

                    asyncio.create_task(self.fetch_data(
                        f"http://{self.host}:{self.port}/indicators",
                        semaphore,
                        self.telemetry.indicators_from_json)
                    )

                async with limiter:
                    await semaphore.acquire()

                    asyncio.create_task(self.fetch_data(
                        f"http://{self.host}:{self.port}/map_obj.json",
                        semaphore,
                        self.map.objects_from_json)
                    )

                    self.telemetry.time = time() - self.start_time

    async def fetch_data(self, url: str, semaphore: asyncio.Semaphore, callback: Callable):
        '''
        # DataThread
        ## Fetch Data
        Performs a GET request to a given URL asynchronously. Its response is passed to
        the provided callback function as a Dict.

        Args:

            url: str containing the URL to which the request is performed.

            semaphore: semaphore object from asyncio. It's released once the request is done

            callback: a function with one positional argument. It's called once the request
            is done with the request's response as the argument formated as a dict.
        '''

        try:
            async with self.session.get(url) as resp:

                content = await resp.json()
                print(f"Finished downloading: {url}")
                callback(content)
                semaphore.release()

        except asyncio.exceptions.TimeoutError:
            print('Request timed-out')

        except Exception as error:

            print(f'Failed to fetch: {error}')

        finally:
            semaphore.release()
