import pydantic


def check_pydantic_ver():
    """
    Check whether pydantic version is ok.
    Warning: PydanticDeprecatedSince211: Accessing the 'model_fields' attribute on the instance is deprecated.
             Instead, you should access this attribute from the model class.
             Deprecated in Pydantic V2.11 to be removed in V3.0.
    """
    #
    pydantic_ver = pydantic.version.VERSION.split(".")
    if not (int(pydantic_ver[0]) <= 2 and int(pydantic_ver[1]) <= 11):
        raise Exception("Too high version of Pydantic, try install pydantic<=2.11")