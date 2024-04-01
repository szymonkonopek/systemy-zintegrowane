import pandas as pd
import json

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
    print(json_data)

# Input parameters responsible for GHP - Główny Harmonogram Produkcji (eng. MPS - master production schedule)
current_on_hand = int(input("Enter current number of products on hand: "))
lead_assemble_time = int(input("Enter lead assemble time for chair: "))

# Sample data before calculation
json_data['production'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
json_data['on_hand'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# On_hand array updated
on_hand = []

for week in range(0, len(json_data['week'])):

    # Check if there is no orders planned
    if json_data['orders'][week] == 0:
        # Check if it's first week
        if json_data['week'][week] == 1:
            # If it's first week, append the current value from week 0 - it's a constant value, entered by user
            on_hand.append(current_on_hand)
        else:
            # Other way, append the same value like week ago - as we don't need to produce anything 
            on_hand.append(on_hand[week - 1])
    
    # Check if the number of orders is more than 0
    if json_data['orders'][week] > 0:
        # If it's first week, calculate the production based on current_on_hand products
        if json_data['week'][week] == 1:
            # as on first week, we can't go back and produce any more product on week 0
            # so we need to use the current_on_hand value, entered by user
            json_data['production'][week] = json_data['orders'][week] - current_on_hand
            on_hand.append(current_on_hand - json_data['orders'][week] + json_data['production'][week])
        else:
            # Other way, the calculation will depend on the last calculated week
            json_data['production'][week] = json_data['orders'][week] - on_hand[week-1]
            on_hand.append(on_hand[week - 1] - json_data['orders'][week] + json_data['production'][week])
    # Append updated on_hand array to JSON
    json_data['on_hand'] = on_hand

with open('planned_orders_ghp.json', 'w') as f:
    json.dump(json_data, f, indent=2)


data_pd = pd.read_json("planned_orders_ghp.json")
transposed_df = data_pd.transpose()

print(transposed_df.to_string(header=False))