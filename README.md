# gosh_sync
Update a google sheet with data from Plentymarkets for a Facebook data feed.

## Requirements:

- Create a Elastic Export format on Plentymarkets:  
    + Data -> FormatDesigner -> add format:  
        Type: item  
    + Assign mandatory fields:  
        Variation.number  
        VariationStock.physicalStock.{Name of Warehouse}  
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
