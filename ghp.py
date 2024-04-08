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

# Read json data from planned_orders.json
json_data = read_json_file('planned_orders.json')
if json_data:
    print("JSON Data:")
    data_pd = pd.read_json("planned_orders.json")
    transposed_df = data_pd.transpose()
    print(transposed_df.to_string(header=False))

# Input storage data
storage_data = read_json_file('storage.json')
if storage_data:
    print("Storage Data:")
    data_pd = pd.read_json("storage.json")
    transposed_df = data_pd.transpose()
    print(transposed_df.to_string(header=False))


# Input parameters responsible for GHP - Główny Harmonogram Produkcji (eng. MPS - master production schedule)
current_on_hand = storage_data["chairs"]["initial_quantity"]
lead_assemble_time = storage_data["chairs"]["waiting_time_in_weeks"]


# On_hand array updated
on_hand = []

for week in range(0, len(json_data['week'])):

    # Check if there is no orders planned
    if json_data['orders'][week] == 0:
        # Planned_production field can be entered by user, but if the planned_production will not be enough for orders, the rest production will be calculated automatically
        if json_data['planned_production'][week] == 0:
            # If there is any production planned by user, then calculate the rest
            if json_data['week'][week] == 1:
                # If it's first week, append the current value from week 0 - it's a constant value, entered by user
                on_hand.append(current_on_hand)
            else:
                # Other way, append the same value like week ago - as we don't need to produce anything 
                on_hand.append(on_hand[week - 1])
        else:
            if json_data['week'][week] == 1:
                # If it's first week, append the current value from week 0 - it's a constant value, entered by user
                on_hand.append(current_on_hand - json_data['orders'][week] + json_data['planned_production'][week])
            else:
                # Other way, append the same value like week ago - as we don't need to produce anything 
                on_hand.append(on_hand[week - 1] - json_data['orders'][week] + json_data['planned_production'][week])
    
    # Check if the number of orders is more than 0
    if json_data['orders'][week] > 0:
            # If it's first week, calculate the production based on current_on_hand products
            if json_data['week'][week] == 1:
                # as on first week, we can't go back and produce any more product on week 0
                # so we need to use the current_on_hand value, entered by user
                if (current_on_hand < json_data['orders'][week]) and json_data['planned_production'][week] == 0:
                    # the planned production condition is checked if it was setup by user, so the user's input won't be omitted
                    json_data['planned_production'][week] = json_data['orders'][week] - current_on_hand
                on_hand.append(current_on_hand - json_data['orders'][week] + json_data['planned_production'][week])
            else:
                # Other way, the calculation will depend on the last calculated week
                # Also we need to check if the planned production won't override the calculations, so if planned_production is 0
                # then we can modify the planned production
                if (json_data['on_hand'][week-1] < json_data['orders'][week]) and json_data['planned_production'][week] == 0:
                    json_data['planned_production'][week] = json_data['orders'][week] - on_hand[week-1]
                on_hand.append(on_hand[week - 1] - json_data['orders'][week] + json_data['planned_production'][week])
        
    # Append updated on_hand array to JSON
    json_data['on_hand'] = on_hand

with open('planned_orders_ghp_test.json', 'w') as f:
    json.dump(json_data, f, indent=2)

data_pd = pd.read_json("planned_orders_ghp_test.json")
transposed_df = data_pd.transpose()
print("Final MPS structure:")
print(transposed_df.to_string(header=False))