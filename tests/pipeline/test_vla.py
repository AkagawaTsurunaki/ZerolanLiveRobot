from zerolan.data.pipeline.vla import ShowUiQuery, WebAction

from manager.config_manager import get_config
from pipeline.vla.showui.showui_sync import ShowUISyncPipeline

_config = get_config()
_showui_sync = ShowUISyncPipeline(_config.pipeline.vla.showui)


def test_showui():
    query = ShowUiQuery(img_path="resources/imgcap-test.png", query="Click the Ciallo")
    prediction = _showui_sync.predict(query)
    assert prediction.actions
    for action in prediction.actions:
        print(action.model_dump_json())

    query = ShowUiQuery(img_path="resources/imgcap-test.png", query="Click the Ciallo",
                        action=WebAction(action="CLICK"))
    prediction = _showui_sync.predict(query)
    assert prediction.actions
    for action in prediction.actions:
        print(action.model_dump_json())
    history = [WebAction(action="INPUT", value="Hello", position=None),
               WebAction(action="SELECT_TEXT", value=None, position=[0.2, 0.3])]
    query = ShowUiQuery(img_path="resources/imgcap-test.png", query="Click the Ciallo", env="web", history=history)
    prediction = _showui_sync.predict(query)
    assert prediction.actions
