import pytest
from zerolan.data.pipeline.img_cap import ImgCapQuery

from manager.config_manager import get_config
from pipeline.imgcap.imgcap_async import ImgCapAsyncPipeline
from pipeline.imgcap.imgcap_sync import ImgCapSyncPipeline

_config = get_config()
_imgcap_sync = ImgCapSyncPipeline(_config.pipeline.img_cap)
_imgcap_async = ImgCapAsyncPipeline(_config.pipeline.img_cap)


def test_imgcap_sync():
    query = ImgCapQuery(img_path="resources/imgcap-test.png")
    prediction = _imgcap_sync.predict(query)
    assert prediction, f"Test failed: No response."
    print(prediction.caption)
    assert "girl" in prediction.caption, f"Test failed: Wrong result."


@pytest.mark.asyncio
async def test_imgcap_async():
    query = ImgCapQuery(img_path="resources/imgcap-test.png")
    prediction = await _imgcap_async.predict(query)
    assert prediction, f"Test failed: No response."
    print(prediction.caption)
    assert "girl" in prediction.caption, f"Test failed: Wrong result."
