"""
Synchronize a google sheet with data from PlentyMarkets.
The google sheet is used as a data feed for a facebook product catalog.

Copyright (C) 2020  Sebastian Fricke, Panasiam

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

---

This module is used to share data from the config and from certain API
calls between multiple modules. Reason being that some API calls like
getting all variations take a lot of time and stress your plentymarkets
call limit. The data could be shared through parameters, but that is ugly.
"""


import pandas


lang:                           str = ''
referrer:                       str = ''
img_match_criteria:            dict = {'type': '', 'value': ''}
item_name_number:               int = 0
gender_property_id:             int = 0
age_property_id:                int = 0
google_category_property_id:    int = 0
url_property_id:                int = 0
material_property_id:           int = 0
price_id:                       int = 0
warehouse_id:                   str = ''
color_attribute_id:             int = 0
size_attribute_id:              int = 0
plenty_variations: pandas.DataFrame = None
plenty_api_instance:         object = None
