import pandas as pd
import json

# to do refactor to use storage.json and change the values in jsons

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
    
def ghp():
    # Read json data from planned_orders.json
    json_data = read_json_file('planned_order.json')
    if json_data:
        print("Initial GHP Data:")
        df = pd.DataFrame(json_data["orders"])
        transposed_df = df.transpose()
        print(transposed_df.to_string(header=False))

    print("\n")
    print("***************************************************")
    print("\n")

    # Input storage data
    storage_data = read_json_file('storage.json')
    print("Storage Data:")
    df = pd.DataFrame.from_dict(storage_data, orient='index')
    print(df)

    # Input parameters responsible for GHP - Główny Harmonogram Produkcji (eng. MPS - master production schedule)
    current_on_hand = storage_data["chairs"]["initial_quantity"]
    lead_assemble_time = storage_data["chairs"]["waiting_time_in_weeks"]


    # On_hand array updated
    on_hand_array = []
    planned_production_array = []

    for week in range(len(json_data['orders'])):
        week_data = json_data['orders'][week]
        week_number = week_data['week']
        demand = week_data['demand']
        planned_production = week_data['planned_production']
        on_hand_amount = week_data['on_hand']
        # Check if there is no orders planned
        if demand == 0:
            # Planned_production field can be entered by user, but if the planned_production will not be enough for orders, the rest production will be calculated automatically
            if planned_production == 0:
                planned_production_array.append(planned_production)
                # If there is any production planned by user, then calculate the rest
                if week_number == 1:
                    # If it's first week, append the current value from week 0 - it's a constant value, entered by user
                    on_hand_array.append(current_on_hand)
                else:
                    # Other way, append the same value like week ago - as we don't need to produce anything 
                    on_hand_array.append(on_hand_array[week - 1])
            else:
                
                if week_number == 1:
                    # If it's first week, append the current value from week 0 - it's a constant value, entered by user
                    planned_production_array.append(planned_production)
                    on_hand_array.append(current_on_hand + planned_production)
                else:
                    # Other way, append the same value like week ago - as we don't need to produce anything 
                    planned_production_array.append(planned_production)
                    on_hand_array.append(on_hand_array[week - 1] + planned_production)
        
        # Check if the number of orders is more than 0
        if demand > 0:
                # If it's first week, calculate the production based on current_on_hand products
                if week_number == 1:
                    # as on first week, we can't go back and produce any more product on week 0
                    # so we need to use the current_on_hand value, entered by user
                    if (current_on_hand < demand) and planned_production == 0:
                        
                        planned_production = demand - current_on_hand
                    planned_production_array.append(planned_production)
                    on_hand_array.append(current_on_hand - demand + planned_production)
                    
                else:
                    # Other way, the calculation will depend on the last calculated week
                    # Also we need to check if the planned production won't override the calculations, so if planned_production is 0
                    # then we can modify the planned production
                    if (on_hand_array[week-1] < demand)  and planned_production == 0:
                        planned_production = demand - on_hand_array[week-1]
                    planned_production_array.append(planned_production)
                    on_hand_array.append(on_hand_array[week - 1] - demand + planned_production)
                    
            
        # Update on-hand in the JSON data
    for week in range(len(json_data['orders'])):
        json_data['orders'][week]['on_hand'] = on_hand_array[week]
        json_data['orders'][week]['planned_production'] = planned_production_array[week]

    with open('planned_orders_ghp_summary.json', 'w') as f:
        json.dump(json_data, f, indent=2)

    print("\n")
    print("***************************************************")
    print("\n")

    data_pd = read_json_file("planned_orders_ghp_summary.json")
    print('data_pd', data_pd['orders'])
    data_pd_df = pd.DataFrame(data_pd["orders"])
    transposed_df = data_pd_df.transpose()
    print("Final GHP structure:")
    print(transposed_df.to_string(header=False))
    print("")