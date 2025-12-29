def check_pydantic_ver():
    """
    Check whether pydantic version is ok.
    Warning: PydanticDeprecatedSince211: Accessing the 'model_fields' attribute on the instance is deprecated.
             Instead, you should access this attribute from the model class.
             Deprecated in Pydantic V2.11 to be removed in V3.0.
    """
    import pydantic
    pydantic_ver = pydantic.version.VERSION.split(".")
    if not (int(pydantic_ver[0]) <= 2 and int(pydantic_ver[1]) <= 11):
        raise Exception("Too high version of Pydantic, try install pydantic<=2.11")


def is_live2d_py_version_less_than(req: str):
    from importlib.metadata import version, PackageNotFoundError
    from packaging.version import parse as vparse
    try:
        ver = vparse(version("live2d-py"))
        return ver <= vparse(req)
    except PackageNotFoundError:
        return None
