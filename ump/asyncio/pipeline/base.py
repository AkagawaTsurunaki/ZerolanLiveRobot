import aiohttp


class BaseAsyncPipeline:

    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self):
        if self._session is not None:
            return self._session
        self._session = aiohttp.ClientSession(self._base_url)
        return self._session

    async def _dispose_client_session(self):
        if self._session is None:
            return
        await self._session.close()

    async def close(self):
        await self._dispose_client_session()
