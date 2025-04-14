import importlib
import inspect
import pkgutil

from pydantic import BaseModel

from common.utils.time_util import get_time_iso_string


def _get_all_classes(package):
    """
    Get all classes from a package and its submodules.
    :param package: The package to inspect (must be imported)
    :return: List of class objects found in the package
    """
    classes = []

    # Iterate through all modules in the package
    for importer, modname, _ in pkgutil.iter_modules(package.__path__):
        # Import the module
        module = importlib.import_module(f"{package.__name__}.{modname}")

        # Find all classes in the module
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                classes.append(obj)

    return classes


def _get_sub_packages(package_name: str):
    """
    Get subpackages from a package.
    :param package_name: The name of the package to inspect.
    :return: List of package objects.
    """
    # Import parent package
    parent_package = importlib.import_module(package_name)

    # Iter packages in the parent package
    package_path = parent_package.__path__
    sub_packages = []
    for _, name, ispkg in pkgutil.iter_modules(package_path):
        if ispkg:  # Only handle package object
            sub_package = importlib.import_module(f"{package_name}.{name}")
            sub_packages.append(sub_package)

    return sub_packages


def doc_gen(package_name: str, author: str, file: str):
    m_ls = _get_sub_packages("zerolan.data")

    lines = ["# Zerolan Data Documentation\n\n",
             f"Generated from the project `{package_name}` by **{author}** at `{get_time_iso_string()}`\n\n"]

    for m in m_ls:  # Iter each module
        lines.append(f"## {m.__name__}\n\n")
        all_classes = _get_all_classes(m)

        for cls in all_classes:  # Iter all classes
            lines.append(f"### {cls.__name__}\n\n")
            lines.append(f"*In module `{cls.__module__}`*\n\n")
            if cls.__doc__ is not None:
                lines.append(f"{cls.__doc__}\n\n")
            if issubclass(cls, BaseModel):
                lines.append("| Field Name | Type | Description|\n")
                lines.append("|--|--|--|\n")
                for field_name, field_info in cls.model_fields.items():
                    desc = field_info.description
                    if desc is None:
                        desc = ""
                    else:
                        desc = field_info.description.replace("\n", "<br>")
                    type = str(field_info.annotation)
                    if type is None:
                        desc = "?"
                    else:
                        type = type.replace("|", r"\|")
                    line = f"|`{field_name}`|`{type}`|{desc}|\n"
                    lines.append(line)
                lines.append("\n\n")
    # Save as a file
    with open(file, "w+", encoding='utf-8') as f:
        f.writelines(lines)


if __name__ == "__main__":
    doc_gen(
        package_name="zerolan.data",
        author="AkagawaTsurunaki",
        file="doc.md"
    )
