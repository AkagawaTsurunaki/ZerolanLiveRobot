import pytest

from services.controller.webui import ZerolanControllerWebUI

_webui = ZerolanControllerWebUI()


@pytest.mark.asyncio
async def test_webui():
    await _webui.start()
