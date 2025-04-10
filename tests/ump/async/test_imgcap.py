import pytest
from zerolan.data.pipeline.img_cap import ImgCapQuery

from private import base_url
from pipeline.imgcap.imgcap_async import ImgCapPipeline

_imgcap = ImgCapPipeline(base_url=base_url, model_id="Salesforce/blip-image-captioning-large")


@pytest.mark.asyncio
async def test_imgcap():
    query = ImgCapQuery(img_path="resources/imgcap-test.png")
    prediction = await _imgcap.predict(query)
    assert prediction, f"Test failed: No response."
    print(prediction.caption)
    assert "girl" in prediction.caption, f"Test failed: Wrong result."
