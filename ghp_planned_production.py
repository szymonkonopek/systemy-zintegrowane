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

# Input parameters responsible for GHP - Główny Harmonogram Produkcji (eng. MPS - master production schedule)
current_on_hand = int(input("Enter current number of products on hand: "))
lead_assemble_time = int(input("Enter lead assemble time for chair: "))

# Read json data from planned_orders.json
json_data = read_json_file('planned_orders.json')
if json_data:
    print("JSON Data:")
    data_pd = pd.read_json("planned_orders.json")
    transposed_df = data_pd.transpose()
    print(transposed_df.to_string(header=False))

planned_production = []

for week in range(0,len(json_data['week'])):
    planned_production.append(int(input(f"Enter YOUR planned production for week nr {week+1}: ")))

# Sample data before calculation
json_data['planned_production'] = planned_production
json_data['on_hand'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

data_pd['planned production'] = planned_production
transposed_df = data_pd.transpose()
print("Planned orders and planned production:")
print(transposed_df.to_string(header=False))

# On_hand array updated
on_hand = []

for week in range(0, len(json_data['week'])):

    # Check if there is no orders planned
    if json_data['orders'][week] == 0:
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

# fix when there is no on_hand and planned equals 0