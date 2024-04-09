import json
import pandas as pd

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' does not contain valid JSON.")
        return None

def mrp(mrpJson, storageElementParent, mrpObjectNameChild):
    # GHP json after calculations
    ghpObject = read_json_file('planned_orders_ghp_summary.json')
    mrpObject = read_json_file(mrpJson)
    
    storageElementParent = read_json_file('storage.json')[storageElementParent]
    storageElementChild = read_json_file('storage.json')[mrpObjectNameChild]
    

    waitingTimeInWeeks = storageElementParent["waiting_time_in_weeks"]

    ghpOrders = ghpObject["orders"]
    mrpOrders = mrpObject["orders"]
    

    fillOrder = True
    for weekDataGhp in ghpOrders:

        if weekDataGhp["planned_production"] != 0:
            mrpIndex = weekDataGhp["week"] - waitingTimeInWeeks - 1 # for example 5 (week) - 1 (waiting_time_in_weeks) - 1 (array difference)
            mrpOrders[mrpIndex]["gross_requirements"] = weekDataGhp["planned_production"]

      
    weekDataMrpIndex = 0
    for weekDataMrp in mrpOrders:

        if weekDataMrp["gross_requirements"] == 0 and fillOrder:
            mrpOrders[weekDataMrpIndex]["on_hand"] = storageElementChild["initial_quantity"]
        elif fillOrder:
            fillOrder = False
            weekDataMrp['net_requirements'] = weekDataMrp['gross_requirements'] - mrpOrders[weekDataMrpIndex - 1]['on_hand']
            weekDataMrp['planned_order_receipts'] = storageElementChild['units_per_batch']
            mrpOrders[weekDataMrpIndex - storageElementChild['waiting_time_in_weeks']]['planned_order_releases'] = storageElementChild['units_per_batch']
            weekDataMrp['on_hand'] = weekDataMrp['planned_order_receipts'] + mrpOrders[weekDataMrpIndex - 1]['on_hand'] - weekDataMrp['gross_requirements']
            

        weekDataMrpIndex += 1
 
    
    # with open('mrp.json', 'w') as f:
    #     json.dump(mrpOrders, f, indent=2)
    
    # jsonFile = read_json_file('mrp.json')

    pdMrpOrders = pd.DataFrame(mrpOrders)
    pdMrpOrders = pdMrpOrders.transpose()
    print(pdMrpOrders.to_string(header=False))
            
