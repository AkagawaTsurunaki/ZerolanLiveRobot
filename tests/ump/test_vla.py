from zerolan.data.pipeline.vla import ShowUiQuery, WebAction

from common.utils.file_util import read_yaml
from pipeline.synch.vla import ShowUIPipeline
from pipeline.config.config import ShowUIConfig

_config = read_yaml("./resources/config.test.yaml")
showui = ShowUIPipeline(ShowUIConfig(
    model_id=_config["showui"]["model_id"],
    predict_url=_config["showui"]["predict_url"],
    stream_predict_url=_config["showui"]["stream_predict_url"],
))


def test_showui():
    query = ShowUiQuery(img_path="resources/imgcap-test.png", query="Click the Ciallo")
    prediction = showui.predict(query)
    assert prediction.actions
    for action in prediction.actions:
        print(action.model_dump_json())

    query = ShowUiQuery(img_path="resources/imgcap-test.png", query="Click the Ciallo",
                        action=WebAction(action="CLICK"))
    prediction = showui.predict(query)
    assert prediction.actions
    for action in prediction.actions:
        print(action.model_dump_json())
    history = [WebAction(action="INPUT", value="Hello", position=None),
               WebAction(action="SELECT_TEXT", value=None, position=[0.2, 0.3])]
    query = ShowUiQuery(img_path="resources/imgcap-test.png", query="Click the Ciallo", env="web", history=history)
    prediction = showui.predict(query)
    assert prediction.actions
