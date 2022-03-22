from socket import timeout
from time import sleep, time
from data_models import HistoricTelemetry
from threading import Thread
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
from collections.abc import Callable


class TelemetryThread:
    '''
    # TelemetryThread
    A wrapper class to a asynchronous telemetry thread.
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

        # Request loop params
        self.rate = rate
        self.max_requests = max_concurrent_requests
        self.timeout = timeout

        self.thread = Thread(target=self.start_loop, daemon=True)
        self.thread.start()

    def start_loop(self):
        '''
        # TelemetryThread
        ## Start Loop
        This is the target to the thread spawned in this classes __init__ method. This
        method starts an async loop by calling update_loop.
        '''

        asyncio.run(self.update_loop())

    async def update_loop(self) -> None:
        '''
        # TelemetryThread
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
                        "http://localhost:8111/state",
                        semaphore,
                        self.telemetry.state_from_json)
                    )

                async with limiter:
                    await semaphore.acquire()

                    asyncio.create_task(self.fetch_data(
                        "http://localhost:8111/indicators",
                        semaphore,
                        self.telemetry.indicators_from_json)
                    )

                    self.telemetry.time = time()

    async def fetch_data(self, url: str, semaphore: asyncio.Semaphore, callback: Callable):
        '''
        # TelemetryThread
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
