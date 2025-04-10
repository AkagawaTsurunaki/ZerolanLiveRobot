from zerolan.data.pipeline.img_cap import ImgCapQuery

from common.utils.file_util import read_yaml
from ump.pipeline.img_cap import ImgCapPipeline
from ump.config import ImgCapPipelineConfig

_config = read_yaml("./resources/config.test.yaml")
imgcap = ImgCapPipeline(ImgCapPipelineConfig(model_id=_config['imgcap']['model_id'],
                                             predict_url=_config['imgcap']['predict_url'],
                                             stream_predict_url=_config['imgcap']['stream_predict_url'], ))


def test_imgcap():
    query = ImgCapQuery(img_path="resources/imgcap-test.png")
    prediction = imgcap.predict(query)
    assert prediction, f"Test failed."
    print(prediction.caption)
    assert "girl" in prediction.caption
