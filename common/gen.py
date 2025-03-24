from pydantic import BaseModel

from common.config import ZerolanLiveRobotConfig


def gen_config():
    config = ZerolanLiveRobotConfig()
    return config


yaml_str = ""


def model_to_yaml_with_comments(model: BaseModel, indent: int = 0) -> str:
    global yaml_str
    """
    将 Pydantic 模型转换为带描述注释的 YAML 字符串。
    :param model: Pydantic 模型实例
    :param indent: 当前缩进级别（默认为 0）
    :return: 带描述注释的 YAML 字符串
    """
    # 获取模型的字段信息
    fields = model.model_fields

    # yaml_str = yaml.dump(model.model_dump(), allow_unicode=True)

    for field_name, field_info in fields.items():
        description = field_info.description or ""
        field_val = model.__getattribute__(field_name)
        if isinstance(field_val, BaseModel):
            # print(type(field_val))
            if field_info.description:
                for description_line in field_info.description.split("\n"):
                    yaml_str += " " * indent + f"# {description_line}\n"
            yaml_str += " " * indent + f"{field_name}:\n"
            model_to_yaml_with_comments(field_val, indent + indent)
        else:
            if field_info.description:
                for description_line in field_info.description.split("\n"):
                    yaml_str += " " * indent + f"# {description_line}\n"
            # kv = yaml.dump({field_name: field_val}, sys.stdout, allow_unicode=True)
            # yaml_str += " " * indent + f"{kv}\n"
            if isinstance(field_val, str):
                yaml_str += " " * indent + f"{field_name}: '{field_val}'\n"
            else:
                yaml_str += " " * indent + f"{field_name}: {field_val}\n"
            # yaml_str += yaml.dump(field_val, allow_unicode=True) + "\n"
        # print(field_name, description)
    return yaml_str
