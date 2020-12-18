# facebook_feed_sync
Update a google sheet with data from the Plentymarkets API for a Facebook catalog feed.

## Installation:

**Prepare the folder structure and get google sheet API access**
1. Place the credentials file from : [Google Sheet API](https://developers.google.com/sheets/api/quickstart/python) as **'credentials.json'** (example: mv ~/Downloads/credentials.json /home/$USER/.config/gspread/credentials.json) into the config folder for `gspread`.
2. Place the `config.ini` file into the `facebook_feed_sync` config folder
    + Linux: /home/$USER/.config/facebook_feed_sync/config.ini
    + Windows: C:\\\\$USER\\.config\\facebook_feed_sync\\config.ini

Here is an example for the config file:
```ini
[General]
google_sheet_id=
plenty_api_url=
lang=
[Mapping]
facebook_referrer=
image_match_criteria=
item_name_number=
gender_item_property=
age_item_property=
google_product_category_item_property=
material_variation_property=
url_variation_property=
sales_price_id=
color_attribute_id=
size_attribute_id=
main_warehouse=
```
3. Get the ID of the target marketplace or Create a new marketplace availability:
    + `{plenty-cloud-domain}/plenty/terra/system/orders/referrer`
    + activate it and add the ID to the configuration.
4. Set the marketplace availability for every variation you want to present on facebook.
5. Create new variation or item properties(characteristics) for these fields or link existing properties:
    + Item properties (characteristics)  
    `{plenty-cloud-domain}/plenty/terra/system/item/character`
        * **gender_item_property** [facebook: `gender`] (target audience gender: 'Men', 'Women', 'Unisex')
        * **age_item_property** [facebook: `age_group`] (target audience age group: 'Adult' or 'Child')
        * **google_product_category_item_property** [facebook: `google_product_category`] (Text value of your google product category, see: [list](https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt))
    + Variation properties  
     `{plenty-cloud-domain}/plenty/terra/system/settings/properties/configuration/overview`
        * **material_variation_property** [facebook: `material`] (material type of the product e.g. Cotton, Hemp etc.)
        * **url_variation_property** [facebook: `link`] (Link to your webshop)
6. Choose the criteria by which valid pictures are chosen for each variation, the picture with the lowest position of the images found is used for Facebook.  
   Example values: `image_match_criteria=mandant;12345`, `image_match_criteria=marketplace;4.01`.
7. Add the IDs of the properties to the matching configuration entry
8. Assign the facebook market availability to on of your prices: `{plenty-cloud-domain}/plenty/terra/system/item/sales-price` and make sure that all variations contain a price. Then add the ID of the price to the configuration field: `sales_price_id`
9. Choose one of the three possible item names: `name1`, `name2` or `name3` and add the number of the name to the configuration field: `item_name_number`
10. Assign the IDs of your color and size attribute to the configuration fields: `color_attribute_id` and `size_attribute_id`
11. Assign the ID of the warehouse used for shipping to the configuration field: `main_warehouse`
12. Fill the properties with values and then add the IDs of the properties to the configuration
13. Create a google sheet and add the following header to it:
    - `id,title,description,availability,inventory,condition,price,link,image_link,brand,google_product_category,sale_price,sale_price_effective_date,item_group_id,gender,color,size,age_group,material,pattern,product_type,shipping,shipping_weight`
    - Insert the text then select the field and go to **Data->Split text into columns**
14. Get your Google Sheet ID:
    + Example URL: `https://docs.google.com/spreadsheets/d/`**{SHEET ID}**`/edit?pli=1#gid=0`
    + Insert it into the configuration.
15. Make an initial setup of the sheet with: `python3 -m facebook_feed_sync -t all`
16. Check if the google sheet looks good and go on **Share** at the top right and change access rights to anyone with the link
17. Go to your business manager (catalogs) [https://business.facebook.com/products/catalogs/](https://business.facebook.com/products/catalogs/), create a new datafeed: Catalog -> data-feeds -> Add products -> Use bulk upload -> Google Spreadsheets -> Next -> Insert the full link -> Choose the upload schedule.
18. Setup the cronjob to run the script preferably on a device, which has a constant uptime (I use a raspberry Pi for example)
