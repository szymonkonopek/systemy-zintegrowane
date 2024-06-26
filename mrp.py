import json
import pandas as pd


# ========== CONIFG ==========
showNegativeNetRequirement = False

# ============================

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
    mrpObject = read_json_file('./mrp/input/' + mrpObjectNameChild +  '.json')
    
    storageElementParent = read_json_file('storage.json')[storageElementParentName]
    storageElementChild = read_json_file('storage.json')[mrpObjectNameChild]

    waitingTimeInWeeks = storageElementParent["waiting_time_in_weeks"]
    currentLevel = storageElementChild['level']

    mrpOrders = mrpObject["orders"]

    if currentLevel == 1:
        ghpObject = read_json_file('planned_orders_ghp_summary.json')
        ghpOrders = ghpObject["orders"]
    else:
        mrpParentOrders = read_json_file('./mrp/output/' + storageElementParentName + '.json')

    ## SETTING GROSS REQUIREMENTS

    if currentLevel == 1:
        for weekDataGhp in ghpOrders:

            if weekDataGhp["planned_production"] != 0:
                mrpIndex = weekDataGhp["week"] - waitingTimeInWeeks - 1 # for example 5 (week) - 1 (waiting_time_in_weeks) - 1 (array difference)
                if mrpIndex < 0:
                    mrpIndex = 0
                mrpOrders[mrpIndex]["gross_requirements"] = (int(weekDataGhp["planned_production"]) * int(storageElementChild['required_elements']))
    else:
        for weekDataMrp in mrpParentOrders:

            if weekDataMrp["planned_order_releases"] != 0:
                mrpIndex = weekDataMrp["week"] - waitingTimeInWeeks - 1
                if mrpIndex < 0:
                    mrpIndex = 0
                mrpOrders[mrpIndex]["gross_requirements"] = (int(weekDataMrp["planned_order_releases"]) * int(storageElementChild['required_elements']))

    def calcInitialOnHand(weekDataMrp, weekDataMrpIndex):
        prevOnHandIndex = weekDataMrpIndex - 1

        # GROSS REQUIREMENTS == 0
        if weekDataMrp['gross_requirements'] == 0:
            # week 1 - if there is no prev. on hand value and no gross requirements 
            if prevOnHandIndex < 0:
                return storageElementChild['initial_quantity']
        
            # when there is no gross requirements but there is prev. hand value
            elif prevOnHandIndex >= 0:
                return mrpOrders[prevOnHandIndex]['on_hand'] + weekDataMrp['planned_order_receipts']
        
        # GROSS REQUIREMENTS != 0
        else:
            # if there is prev. on hand
            if prevOnHandIndex >= 0:
                isPrevOnHandPositive = mrpOrders[prevOnHandIndex]['on_hand'] >= 0

                if isPrevOnHandPositive:
                    return mrpOrders[prevOnHandIndex]['on_hand'] - weekDataMrp['gross_requirements'] + weekDataMrp['planned_order_receipts']
                else:
                    return mrpOrders[prevOnHandIndex]['on_hand'] - weekDataMrp['gross_requirements'] + weekDataMrp['planned_order_receipts']
                
            # if there is no prev. on hand
            else:
                return storageElementChild['initial_quantity'] - weekDataMrp['gross_requirements']
            

    def isPrevProductionNotBiggerThanDemand( index):
        totalPlannedProduction = storageElementChild['initial_quantity']
        totalGrossRequirements = 0

        for i in range(index + 1): # because index is 0 based
            totalPlannedProduction += mrpOrders[i]['planned_order_releases']
            totalGrossRequirements += mrpOrders[i]['gross_requirements']

        return totalPlannedProduction < totalGrossRequirements

    
    def calcNetRequirements(weekDataMrp):
        if showNegativeNetRequirement:
            return weekDataMrp['planned_order_receipts'] - weekDataMrp['on_hand'] 
        else:
            return max(0, weekDataMrp['planned_order_receipts'] - weekDataMrp['on_hand'])


    weekDataMrpIndex = 0

    
    for weekDataMrp in mrpOrders:
        weekDataMrp['on_hand'] = calcInitialOnHand(weekDataMrp, weekDataMrpIndex)


        # IF PRODUCTION MANUALY OVERWRITTEN
        if weekDataMrp['planned_order_releases'] != 0:
            plannedOrderReceiptsIndex = weekDataMrpIndex + storageElementChild['waiting_time_in_weeks']

            if plannedOrderReceiptsIndex < len(mrpOrders):
                mrpOrders[plannedOrderReceiptsIndex]['planned_order_receipts'] = storageElementChild['units_per_batch']


        # SCHEDULE PRODUCTION
        elif weekDataMrp['on_hand'] < 0 and isPrevProductionNotBiggerThanDemand(weekDataMrpIndex):

            plannedOrderReceiptsIndex = weekDataMrpIndex - storageElementChild['waiting_time_in_weeks']

            # Case 1: Production can be scheduled in the past and automatically set in current week
            if plannedOrderReceiptsIndex >= 0:
                

                mrpOrders[plannedOrderReceiptsIndex]['planned_order_releases'] = storageElementChild['units_per_batch']
                # set order receipt
                # if can set production
                if plannedOrderReceiptsIndex < len(mrpOrders):
                    weekDataMrp['planned_order_receipts'] = storageElementChild['units_per_batch']
                    weekDataMrp['on_hand'] = weekDataMrp['planned_order_receipts'] + mrpOrders[weekDataMrpIndex - 1]['on_hand'] - weekDataMrp['gross_requirements']
                else:
                    print('Production can not be scheduled in the past and in the future')
            
            # Case 2: Production can't be scheduled in the past
            else:
                
                weekDataMrp['planned_order_releases'] = storageElementChild['units_per_batch']

                # Calculating when to set order receipt
                plannedOrderReceiptsIndex = weekDataMrpIndex + storageElementChild['waiting_time_in_weeks']

                # set order receipt
                # if can set production
                if plannedOrderReceiptsIndex < len(mrpOrders):
                    mrpOrders[plannedOrderReceiptsIndex]['planned_order_receipts'] = storageElementChild['units_per_batch']
                else:
                    print('Production can not be scheduled in the past and in the future')
        
        
        # CALCULATE NET REQUIREMENTS
        weekDataMrp['net_requirements'] = calcNetRequirements(weekDataMrp)
        
        weekDataMrpIndex += 1
    
    with open('./mrp/output/' + mrpObjectNameChild + '.json', 'w') as f:
        json.dump(mrpOrders, f, indent=2)
    
    pdMrpOrders = pd.DataFrame(mrpOrders)
    pdMrpOrders = pdMrpOrders.transpose()
    print("MRP Data:", mrpObjectNameChild)
    print(pdMrpOrders.to_string(header=False))
    print('Lead time', storageElementChild['waiting_time_in_weeks'], 'weeks')
    print('Lot size', storageElementChild['units_per_batch'], 'units per batch')
    print('Level', storageElementChild['level'], 'level')
    print('Initial quantity', storageElementChild['initial_quantity'], 'units')

    print("\n")
            
