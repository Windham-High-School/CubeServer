""" Represents serializable configuration with groups of fields
"""

from typing import Optional

from cubeserver_common.models import PyMongoModel


ConfigFieldType = int | str | float | bytes | bool


class GroupedConfigField(PyMongoModel):
    """
    A single, serializable configuration field and the info needed to nicely render it.
    """

    def __init__(
        self,
        name: str = "my field",
        description: str = "a description of the field",
        default_value: ConfigFieldType = "default value",
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.default: ConfigFieldType = default_value
        self.value: ConfigFieldType = default_value
        self.index: Optional[int] = None

    def reset(self) -> None:
        """
        Resets the value of this field to the default
        """
        self.value = self.default


class GroupedConfigCategory(PyMongoModel):
    """
    A serializable category of GroupedConfigFields
    """

    def __init__(
        self,
        name: str = "Config Category Name",
        description: str = "A description of this category of configuration",
    ) -> None:
        self.fields: list[GroupedConfigField] = []
        self.name: str = name
        self.description: str = description

    def reset(self) -> None:
        """Resets all fields in this category to the default"""


class GroupedConfig(PyMongoModel):
    """
    A serializable set of GroupedConfigCategory objects
    Multiple of these may exist in the database, but only one should be the default.
    """

    def __init__(
        self, name: str = "CubeServer Configuration", default: bool = True
    ) -> None:
        self.name: str = name
        self.categories: dict[int, GroupedConfigCategory] = {}
        self.default: bool = default

    def add_category(self, category: GroupedConfigCategory) -> None:
        """Adds a category.
        An index will be assigned to this category.
        """
        new_index = max(self.categories.keys()) + 1
        self.categories[new_index] = category

    def __setitem__(self, key: any, value: GroupedConfigCategory) -> None:
        raise TypeError(
            "You cannot assign an item of a GroupedConfig.\nPlease use add_category() instead."
        )

    def __getitem__(self, key: int | str) -> GroupedConfigCategory:
        """
        Returns a given category by name or index
        """
