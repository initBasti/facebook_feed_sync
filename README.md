# fb_feed_sync
Update a google sheet with data from Plentymarkets for a Facebook data feed.

## Requirements:

- Create FormatDesigner format/s on Plentymarkets:  
    [**Stock Export**]
    + Data -> FormatDesigner -> add format:  
        Type: item  
    + Assign mandatory fields:  
        Variation.number  
        VariationStock.physicalStock.{Name of Warehouse}  

    [**Color & Size upload**]
    + Data -> FormatDesigner -> add format:  
        Type: item  
    + Assign mandatory fields:  
        Variation.number  
        VariationAttributeValues.attributeValues  

    [**Price upload**]
    + Data -> FormatDesigner -> add format:  
        Type: item  
    + Assign mandatory fields:  
        Variation.number  
        VariationSalesPrice.price  
        (Assign the price, that you use on your webshop [Arrow To Box Button on the right])  

    [**Text upload**]
    + Data -> FormatDesigner -> add format:  
        Type: item  
    + Assign mandatory fields:  
        Variation.number  
        ItemDescription.Webshopname  
        ItemDescription.description  

- Create ElasticExport formats for the FormatDesigner formats:  
    + Data -> ElasticExport -> new Export:  
        Type: Item  
        Limit: 99999  
        Serve as URL  
        Name {name of file}.csv  
        Create a token  
        Save the resulting URL into the config.ini file.  

- Fill out a google sheet with your data in the facebook data feed format.  
- Get your Google Sheet ID:  
    + Example URL: `https://docs.google.com/spreadsheets/d/`**{SHEET ID}**`/edit?pli=1#gid=0`  
      Insert into the config.ini file.  
- Specify the number of rows to be read @ config.ini => General => google_sheet_rows  
