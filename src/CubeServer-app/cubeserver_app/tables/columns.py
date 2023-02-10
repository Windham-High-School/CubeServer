"""Defines custom column types for flask-table"""

from enum import Enum
from typing import List, Mapping, Optional, Tuple, Any
from flask import render_template_string, url_for
from flask_table import Col, html
from flask_wtf import FlaskForm
from wtforms import SelectField, HiddenField, SubmitField
from abc import ABCMeta, abstractmethod

from cubeserver_common.models.datapoint import DataClass

__all__ = ['EnumCol', 'DropDownEnumCol', 'OptionsCol', 'ManualScoring']

def _render_form(
    form: FlaskForm,
    action: str = "table_endpoint",
    form_id: Optional[str] = None,
    form_attributes: List[Tuple[str]] = None,
    auto_submit: Optional[bool] = None
) -> str:
    """Renders a form into HTML.
    If there is no submit field in the form, any field changes will
    auto-submit the form unless otherwise specified.
    If any weird custom attributes are needed on specific fields, it
    may be easiest to add them client-side with JQuery.
    (see static/js/common.js or add a script to the applicable template)
    """
    # Decide whether or not to auto-submit:
    field_attributes: Mapping[str, str] = {}
    if auto_submit or (  # If not explicitly given, check the form for SubmitFields:
        auto_submit is None and
        not any(isinstance(field, SubmitField) for field in form)
    ):
        field_attributes["onchange"] = "this.form.submit()"
    # List of (name, value) HTML attributes for the form:
    attributes = (form_attributes if form_attributes else []) + \
                 [('action', action),
                  ('method', "POST")]
    if form_id:
        attributes.append(('id', form_id))
    attributes_string = ' '.join(
        [f"{key}=\"{val}\"" for key, val in attributes]
    )
    html = f"<form {attributes_string}>"
    html += '\n'.join(["\t"+field(**field_attributes) for field in form])
    html += "</form>"
    return html


class EnumCol(Col):
    """A Column for Enums, hence the name, EnumCol.
    :) """

    def td_format(self, content: Enum):
        if content:
            return content.value
        return ""

class TeamNameCol(Col):
    """A column for team names"""
    def td_format(self, content):
        return f"<b><a href='{url_for('home.team_info', team_name=content)}'>{content}</a></b>"
class AdminTeamNameCol(Col):
    """A column for team names"""
    def td_format(self, content):
        return f"<b><a href='{url_for('admin.team_info', team_name=content)}'>{content}</a></b>"


class HTMLCol(Col):
    """A Column with custom HTML"""

    @abstractmethod
    def generate_html(
        self,
        content: Any,
        identifier: str,
        attr_list: List[str]
    ) -> str:
        """An abstract method for generating a cell's HTML

        Args:
            content (Any): The Python object represented by the cell
            identifier (str): If item.id exists, the string value of item.id for use in pymongo document-modifying forms
            attr_list (List[str]): attr_list from Col.__init__

        Returns:
            str: HTML for this cell
        """

    def generate_attrs(
        self,
        content: Any
    ) -> Mapping[str, str]:
        """Generate any attributes to the td element

        Args:
            content (Any): the python object from which the cell contents are derived

        Returns:
            Mapping[str, str]
        """
        return {
            'data-search': str(content),
            'data-order': str(content)
        }

    def __init__(self, name, *args, **kwargs):
        """Specify the column name"""
        super().__init__(name, *args, **kwargs)
        self.constructor_kwargs = kwargs

    def custom_td_format(
        self,
        content: Any,
        identifier: str,
        attr_list: List[str]
    ):
        """A custom version of td_format, renamed to avoid
        PyLint from getting upset from the different parameter list
        This creates a form for each cell."""
        return self.generate_html(content, identifier, attr_list)

    def td_contents(self, item, attr_list):
        return (
            self.custom_td_format(
                self.from_attr_list(item, attr_list=attr_list),
                str(item.id) if item.id else None,
                attr_list
            )
        )

    def td(self, item, attr):
        content = self.td_contents(item, self.get_attr_list(attr))
        item: Any = self.from_attr_list(item, attr_list=attr)
        td_attrs = self.generate_attrs(item)
        return html.element(
            'td',
            content=content,
            escape_content=False,
            attrs=td_attrs | self.td_html_attrs)

class DropDownEnumCol(Col):
    """A Column with a drop-down box to select an option from an Enum"""

    # TODO: Neaten this constructor:
    def __init__(self, name, enum_class, *args, model_type: str="Team", exclude_option=None, **kwargs):
        """Specify the column name and the class of the Enum"""
        super().__init__(name, *args, **kwargs)
        self.model_type = model_type
        self.enum_class = enum_class
        options = [(option.value, option.value) for option in enum_class]
        if exclude_option is not None:
            options.remove(
                (exclude_option.value, exclude_option.value)
            )
        class ColDropDownForm(FlaskForm):
            """A custom form for just this column"""
            item = SelectField(choices=options)
            parameter = HiddenField()
            identifier = HiddenField()
        self.form = ColDropDownForm

    def custom_td_format(
        self,
        content: Enum,
        identifier: str,
        attr_list: List[str]
    ):
        """A custom version of td_format, renamed to avoid
        PyLint from getting upset from the different parameter list
        This creates a form for each cell."""
        form_instance = self.form()
        form_instance.item.data = content.value
        attr_name = attr_list[0]
        return _render_form(
            form_instance,
            action=f"table_endpoint/{self.model_type}/{identifier}/{attr_name}",
        )

    def td_contents(self, item, attr_list):
        return (
            self.custom_td_format(
                self.from_attr_list(item, attr_list=attr_list),
                str(item.id),
                attr_list
            )
        )

    def td(self, item, attr):
        content = self.td_contents(item, self.get_attr_list(attr))
        item: Enum = self.from_attr_list(item, attr_list=attr)
        td_attrs = {
            'data-search': item.value,
            'data-order': item.value
        }
        return html.element(
            'td',
            content=content,
            escape_content=False,
            attrs=td_attrs | self.td_html_attrs)

# TODO: Add more options? Perhaps the ability to make custom BSON modifications
class OptionsCol(HTMLCol):
    """A Column with a menu of options
    Requires the inclusion of static/js/admin.js to communcate with the api"""

    def __init__(self, *args, model_type: str="Team", **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = model_type

    def generate_html(
        self,
        content: Any,
        identifier: str,
        attr_list: List[str]
    ) -> str:
        return render_template_string(
            (
                (
                    "<div>\n"
                    "<button title=\"delete\" "
                    f"onclick=\"deleteItem('{self.model_type}', '{{{{id}}}}')\" "
                    "class=\"btn btn-danger\">&#10060;</button>\n"
                    +((
                        "<button title=\"Adjust Score\" "
                        f"onclick=\"adjustScore('{self.model_type}', '{{{{id}}}}')\" "
                        "class=\"btn btn-info\">&#x2696;</button>\n"
                    ) if self.model_type == "Team" else "")
                ) +
                "</div>\n"
            ),
            id=identifier
        )

class ManualScoring(HTMLCol):
    """A Column for manually scoring"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generate_html(
        self,
        content: Any,
        identifier: str,
        attr_list: List[str]
    ) -> str:
        return render_template_string(
            (
                '\n'.join([(
                    "<div>\n"
                    "<button title=\"add datapoint\" "
                    f"onclick=\"add_datapoint('{{{{id}}}}', '{dataclass.value}', {str(dataclass.datatype == bool).lower()})\" "
                    f"class=\"btn btn-info\">{dataclass.value}</button>\n"
                    "</div>\n"
                ) for dataclass in DataClass.manual])
            ),
            id=identifier
        )

class ScoreDeltaCol(HTMLCol):
    """A Column that has class text-success if content is positive, otherwise text-danger"""
    
    def generate_html(self, content: Any, identifier: str, attr_list: List[str]) -> str:
        number = int(content)
        text_class = "text-warning"
        if number > 0:
            text_class = "text-success"
        elif number < 0:
            text_class = "text-danger"
        prefix = '+' if number >= 0 else '-'
        return (
                f"<span class=\"{text_class}\">\n",
                f"{prefix} {abs(content)}\n",
                "</span>\n"
        )

class PreCol(HTMLCol):
    """A Column that displays its contents between <pre /> tags"""

    def __init__(self, name, pre_classes="", *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.pre_classes=pre_classes

    def generate_html(self, content: Any, identifier: str, attr_list: List[str]) -> str:
        return (
                f"<pre class=\"{self.pre_classes}\">\n",
                f"{content}\n",
                "</pre>\n"
        )


# TODO: Finish BoolCol implementation with pretty coloring!
#class BoolCol(HTMLCol):
#    """A Column for displaying boolean values"""
#
#    def generate_html(self, content: Any, identifier: str, attr_list: List[str]) -> str:
#        return ""
#

