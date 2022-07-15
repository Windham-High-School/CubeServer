"""Defines custom column types for flask-table"""

from enum import Enum
from typing import List, Mapping, Optional, Tuple
from flask_table import Col, html
from flask_wtf import FlaskForm
from wtforms import SelectField, HiddenField, SubmitField

__all__ = ['EnumCol', 'DropDownEnumCol']

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
    """A Column for Enums, hence the name, EnumCol."""

    def td_format(self, content: Enum):
        return content.value

class DropDownEnumCol(Col):
    """A Column with a drop-down box to select an option from an Enum"""

    def __init__(self, name, enum_class, *args, exclude_option=None, **kwargs):
        """Specify the column name and the class of the Enum"""
        super().__init__(name, *args, **kwargs)
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
            action=f"table_endpoint/{identifier}/{attr_name}",
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
