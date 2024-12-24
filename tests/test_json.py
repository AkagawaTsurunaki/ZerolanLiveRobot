import json

from common.utils.json_util import smart_load_json_like

json_vals = [
    """
    {
        "text": "Hello",
        "number": 1.1
    }
    """,
    """
    {
    "text": "Hello",
    "number": 1.1
    }}
    """
    ,
    """
    ```json
    {
        "text": "Hello",
        "number": 1.1
    }
    ```
    """,
    """
    ```json
    {
        "text": "Hello",
        "number": 1.1
    }}
    ```
    """,
    """
    以下是生成的 json 数据：
    ```json
    {
        "text": "Hello",
        "number": 1.1
    }}
    ```
    如果你还有其他需要，请随时使用我。
    """,
    """
    以下是生成的 json 数据：
    ```json
    {"name": "游戏对象创建器", "args": {"instance_id": 1, "gameobject_name": "绿色立方体", "object_type": "cube", "color": "#008000", "transform": {"scale": 1, "position": {"x": 0, "y": 0, "z": 0}}}}}}
    ```
    如果你还有其他需要，请随时使用我。
    """,
    """
    以下是生成的 json 数据：
    ```json
    {"name": "游戏对象创建器", "args": {"instance_id": 1, "gameobject_name": "绿色立方体", "object_type": "cube", "color": "#008000", "transform": {"scale": 1, "position": {"x": 0, "y": 0, "z": 0}}}}}}}}}
    ```
    如果你还有其他需要，请随时使用我。
    """
]


def test_json():
    for i, json_val in enumerate(json_vals):
        json_val = smart_load_json_like(json_val)
        print(f"Test case {i} passed:")
        print(json.dumps(json_val, indent=4, ensure_ascii=False))
