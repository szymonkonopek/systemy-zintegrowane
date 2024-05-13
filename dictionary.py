from collections import OrderedDict

production_data_ghp_map = OrderedDict({
    'demand': 'Demand',
    'planned_production': 'Planned Production',
    'on_hand': 'On Hand'
})

production_data_map = OrderedDict({
    'gross_requirements': 'Gross Requirements',
    'scheduled_receipts': 'Scheduled Receipts',
    'on_hand': 'On hand',
    'net_requirements': 'Net Requirements',
    'planned_order_releases': 'Planned Order Releases',
    'planned_order_receipts': 'Planned Order Receipts',
})

storage_ghp_data_map = OrderedDict({
    'waiting_time_in_weeks': 'Waiting Time in Weeks',
    'initial_quantity': 'Initial Quantity'    
})

storage_data_map = OrderedDict({
    'waiting_time_in_weeks': 'Waiting Time in Weeks',
    'units_per_batch': 'Units per Batch',
    'level': 'Level',
    'initial_quantity': 'Initial Quantity',
})

table_file_name_map = OrderedDict({
    'demand': 'Demand',
    'on_hand': 'On Hand',
    'planned_production': 'Planned Production'
})
