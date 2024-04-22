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

def mrp(storageElementParentName, mrpObjectNameChild):
    # GHP json after calculations



    ghpObject = read_json_file('planned_orders_ghp_summary.json')
    mrpObject = read_json_file('base_mrp.json')
    
    storageElementParent = read_json_file('storage.json')[storageElementParentName]
    storageElementChild = read_json_file('storage.json')[mrpObjectNameChild]

    waitingTimeInWeeks = storageElementParent["waiting_time_in_weeks"]
    currentLevel = storageElementChild['level']

    mrpOrders = mrpObject["orders"]

    if currentLevel == 1:
        ghpObject = read_json_file('planned_orders_ghp_summary.json')
        ghpOrders = ghpObject["orders"]
    else:
        mrpParentOrders = read_json_file(storageElementParentName + '.json')


    

    fillOrder = True

    if currentLevel == 1:
        for weekDataGhp in ghpOrders:

            if weekDataGhp["planned_production"] != 0:
                mrpIndex = weekDataGhp["week"] - waitingTimeInWeeks - 1 # for example 5 (week) - 1 (waiting_time_in_weeks) - 1 (array difference)
                mrpOrders[mrpIndex]["gross_requirements"] = (int(weekDataGhp["planned_production"]) * int(storageElementChild['required_elements']))
    else:
        for weekDataMrp in mrpParentOrders:

            if weekDataMrp["gross_requirements"] != 0:
                mrpIndex = weekDataMrp["week"] - waitingTimeInWeeks - 1
                mrpOrders[mrpIndex]["gross_requirements"] = (int(weekDataMrp["gross_requirements"]) * int(storageElementChild['required_elements']))


      
    weekDataMrpIndex = 0
    for weekDataMrp in mrpOrders:

        # 1 2 3 
        if weekDataMrp["gross_requirements"] == 0 and fillOrder:
            mrpOrders[weekDataMrpIndex]["on_hand"] = storageElementChild["initial_quantity"]

        # 5
        elif weekDataMrp["gross_requirements"] == 0 and not fillOrder:
            weekDataMrp['on_hand'] = mrpOrders[weekDataMrpIndex - 1]['on_hand']

        # 4 
        elif fillOrder:
            fillOrder = False
            index = weekDataMrpIndex - storageElementChild['waiting_time_in_weeks']

            if mrpOrders[weekDataMrpIndex - 1]['on_hand'] <= weekDataMrp['gross_requirements']:
                weekDataMrp['on_hand'] = mrpOrders[weekDataMrpIndex - 1]['on_hand'] - weekDataMrp['gross_requirements']
                weekDataMrp['net_requirements'] = weekDataMrp['gross_requirements'] - mrpOrders[weekDataMrpIndex - 1]['on_hand']

            # else:
                weekDataMrp['planned_order_receipts'] = storageElementChild['units_per_batch']
                mrpOrders[index]['planned_order_releases'] = storageElementChild['units_per_batch']

            if index < 0:
                raise Exception("Sorry production is not available in the past 😱")
            weekDataMrp['on_hand'] = weekDataMrp['planned_order_receipts'] + mrpOrders[weekDataMrpIndex - 1]['on_hand'] - weekDataMrp['gross_requirements']

        # 6?
        elif weekDataMrp["gross_requirements"] != 0 and not fillOrder:
            weekDataMrp['net_requirements'] = weekDataMrp['gross_requirements'] - mrpOrders[weekDataMrpIndex - 1]['on_hand']
            weekDataMrp['planned_order_receipts'] = storageElementChild['units_per_batch']
            index = weekDataMrpIndex - storageElementChild['waiting_time_in_weeks']
            if index < 0:
                raise Exception("Sorry production is not available in the past 😱")
            mrpOrders[index]['planned_order_releases'] = storageElementChild['units_per_batch']
            weekDataMrp['on_hand'] = weekDataMrp['planned_order_receipts'] + mrpOrders[weekDataMrpIndex - 1]['on_hand'] - weekDataMrp['gross_requirements']
        

        weekDataMrpIndex += 1
 
    
    with open(mrpObjectNameChild + '.json', 'w') as f:
        json.dump(mrpOrders, f, indent=2)
    
    # jsonFile = read_json_file('mrp.json')

    pdMrpOrders = pd.DataFrame(mrpOrders)
    pdMrpOrders = pdMrpOrders.transpose()
    print("MRP Data:", mrpObjectNameChild)
    print(pdMrpOrders.to_string(header=False))
    print('Lead time', storageElementChild['waiting_time_in_weeks'], 'weeks')
    print('Lot size', storageElementChild['units_per_batch'], 'units per batch')
    print('Level', storageElementChild['level'], 'level')
    print('Initial quantity', storageElementChild['initial_quantity'], 'units')


    print("\n")
            
