""" Represents serializable configuration with groups of fields
"""

from enum import Enum
from typing import Self

from cubeserver_common.utils import classproperty
from cubeserver_common.models import PyMongoModel
from cubeserver_common.models.utils.codecs import ListCodec
from cubeserver_common.models.utils import AutoEncodable, EncodableCodec


__all__ = ["ConfigFieldType", "GroupedConfigField"]

ConfigFieldType = int | str | float | bytes | bool


class FieldInputType(Enum):
    """Types of input"""

    INTEGER = 1
    DECIMAL = 2
    CHECKBOX = 3
    TEXTBOX = 4
    TEXTAREA = 5


class GroupedConfigField(AutoEncodable):
    """
    A single, serializable configuration field and the info needed to nicely render it.
    """

    def __init__(
        self,
        name: str = "my field",
        description: str = "a description of the field",
        default_value: ConfigFieldType = "default value",
        input_type: FieldInputType = FieldInputType.TEXTBOX,
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.default_value: ConfigFieldType = default_value
        self.value: ConfigFieldType = default_value
        self.input_type = input_type

    def reset(self) -> None:
        """
        Resets the value of this field to the default
        """
        self.value = self.default_value


class GroupedConfigCategory(AutoEncodable):
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

        self._fields["fields"] = ListCodec(EncodableCodec(GroupedConfigField))

    def reset(self) -> None:
        """Resets all fields in this category to the default"""
        for field in self.fields:
            field.reset()

    def add_field(self, field: GroupedConfigField) -> None:
        """Adds a field.
        An index will be assigned to this field.
        """
        self.fields.append(field)

    def __setitem__(self, key, value: GroupedConfigField) -> None:
        """Items cannot be set. The list of fields is intended to be rather immutable."""
        raise TypeError(
            "You cannot assign an item of a GroupedConfigCategory.\nPlease use add_field() instead."
        )

    def __getitem__(self, key: int | str) -> GroupedConfigField:
        """
        Returns a given field by name or index from the category
        """
        if isinstance(key, int):
            return self.fields[key]
        return {field.name: field for field in self.fields}[key]

    def __iter__(self):
        return iter(self.fields)


class GroupedConfig(PyMongoModel):
    """
    A serializable set of GroupedConfigCategory objects
    Multiple of these may exist in the database, but only one should be the default.

    Because multiple GroupedConfig objects can be stored, there is provision for
    having multiple sets of configuration values that could be switched between.

    Whichever is currently selected (which *should* only ever be one at a time) can be found
    with GroupedConfig.selected
    """

    def __init__(
        self, name: str = "CubeServer Configuration", selected: bool = True
    ) -> None:
        self.name: str = name
        self.categories: list[GroupedConfigCategory] = []
        self.selected: bool = selected

        self._fields["categories"] = ListCodec(EncodableCodec(GroupedConfigCategory))

    def add_category(self, category: GroupedConfigCategory) -> None:
        """Adds a category.
        An index will be assigned to this category.
        """
        self.categories.append(category)

    def __setitem__(self, key, value: GroupedConfigCategory) -> None:
        """Items cannot be set. The list of categories is intended to be rather immutable."""
        raise TypeError(
            "You cannot assign an item of a GroupedConfig.\nPlease use add_category() instead."
        )

    def __getitem__(self, key: int | str) -> GroupedConfigCategory:
        """
        Returns a given category by name or index
        """
        if isinstance(key, int):
            return self.categories[key]
        return {category.name: category for category in self.categories}[key]

    def __iter__(self):
        return iter(self.categories)

    @classmethod
    @classproperty
    def selected(cls) -> Self:
        return cls.find_one(selected=True)
