sync_to_plenty_map = {
    'inventory':['Variation.number', 'VariationStock.physicalStock.'],
    'price':['Variation.number', 'VariationSalesPrice.price'],
    'text':['Variation.number', 'ItemDescription.Webshopname',
            'ItemDescription.description'],
    'attr':['Variation.number', 'VariationAttributeValues.attributeValues']
}

sync_to_gsheet_map = {
    'inventory':['inventory'],
    'price':['price'],
    'text':['title', 'description'],
    'attr':['color', 'size']
}

sync_to_gsheet_range_map = {
    'inventory':['E'],
    'price':['G'],
    'text':['B', 'C'],
    'attr':['P', 'Q']
}

sync_to_gsheet_index_map = {
    'inventory':[4],
    'price':[6],
    'text':[1,2],
    'attr':[15,16]
}

log_location = ''
