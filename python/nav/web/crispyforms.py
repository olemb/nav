#
# Copyright (C) 2013 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""A collection of forms using the django crispy forms framework"""

from crispy_forms.layout import BaseInput
from crispy_forms_foundation.layout import Field


class NavSubmit(BaseInput):
    """Displays proper Foundation submit button"""
    input_type = 'submit'
    field_classes = 'button small'


class CheckBox(Field):
    """Checkbox suited for the NAV layout"""
    template = 'custom_crispy_templates/horizontal_checkbox.html'
