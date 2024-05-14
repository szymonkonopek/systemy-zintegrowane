import json
import dash
from dash import html, dcc, dash_table, callback_context
from dash.dependencies import Input, Output
import pandas as pd
from dictionary import *
from collections import OrderedDict
import dash_bootstrap_components as dbc

import ghp
import mrp


import os
import sys



app = dash.Dash(__name__, suppress_callback_exceptions=True,     external_stylesheets=[dbc.themes.BOOTSTRAP])
def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' does not contain valid JSON.")
        return None

def prepare_table_data(json_data, production_data_map):
    if json_data:
        if 'orders' in json_data:
            attributes = set(json_data['orders'][0].keys()) - {'week'}
            data_by_attribute = OrderedDict({
                production_data_map[attr]: {f'Week {order["week"]}': order[attr] for order in json_data['orders'] if attr in order}
                for attr in production_data_map if attr in attributes
            })
        else:
            attributes = set(json_data[0].keys()) - {'week'}
            data_by_attribute = OrderedDict({
                production_data_map[attr]: {f'Week {entry["week"]}': entry[attr] for entry in json_data if attr in entry}
                for attr in production_data_map if attr in attributes
            })
        return [{'Production Data': attr, **values} for attr, values in data_by_attribute.items()]
    return []

def prepare_storage_table_data(id, data_map):
    if id == 'chairs2':
        id = 'chairs'
    elif id == 'frame2':
        id = 'frame'    
    json_data = read_json_file('storage.json')
    if json_data and id in json_data:
        storage_data = json_data[id]
        data = []
        for attr in data_map:
            if attr in storage_data:
                data.append({'Attribute': data_map[attr], 'Value': storage_data[attr]})
        return data
    else:
        print(f"Error: Data for ID '{id}' not found in storage.")
        return []

def create_table(file_name, map_name, table_name, editable, storage_id, storage_map_name):
    json_data = read_json_file(file_name)
    data_rows = prepare_table_data(json_data, map_name)
    storage_data_rows = prepare_storage_table_data(storage_id, storage_map_name)

    columns = [{'name': '', 'id': 'Production Data'}] + \
              [{'name': f'Week {i}', 'id': f'Week {i}'} for i in range(1, 11)]
    storage_columns = [{'name': '', 'id': 'Attribute'}, {'name': 'Value', 'id': 'Value'}]

    production_table_id = file_name.replace('.json', '') + '_table'
    storage_table_id = f"{storage_id}_storage_table"
    div_id = file_name.replace('.json', '') + '_div'

    table_container = html.Div([
        html.H1(table_name),
        dash_table.DataTable(
            id=production_table_id,
            columns=columns,
            data=data_rows,
            editable=editable
        ),
        dash_table.DataTable(
            id=storage_table_id,
            columns=storage_columns,
            data=storage_data_rows,
            style_header={'display': 'none'},
            style_data={'width': 135},
            fill_width=False,
            css=[{'selector': 'tr:first-child', 'rule': 'display: none'}],
            editable=True
        ),
        html.Div(id='output_' + div_id),
    ])
    @app.callback(
        Output('output_' + div_id, 'children'),
        [Input(production_table_id, 'data'),
        Input(storage_table_id, 'data')]
    )
    def update_output(production_rows, storage_rows):
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if not production_rows and not storage_rows:
            return html.Div("Brak danych do wyświetlenia")

        if production_table_id in triggered_id:
            production_data = json.dumps(production_rows, indent=4)
            orders = []
            for week in range(1, 11):
                order = {
                    "week": week,
                    "demand": int(production_rows[0][f"Week {week}"]),
                    "planned_production": int(production_rows[1][f"Week {week}"]),
                    "on_hand": int(production_rows[2][f"Week {week}"])
                }
                orders.append(order)
            new_data = {"orders": orders}
            
            file_path = file_name
            try:
                with open(file_path, 'w') as file:
                    json.dump(new_data, file, indent=4)
                print(f"Updated JSON file '{file_path}' with new data.")
                ghp.ghp()
                mrp.mrp('chairs', 'frame')
                mrp.mrp('frame', 'wooden_construction_elements')
                mrp.mrp('frame', 'nails')
                mrp.mrp('chairs', 'padding')
            except Exception as e:
                print(f"Error while updating JSON file: {e}")

        elif storage_table_id in triggered_id:
            storage_data = json.dumps(storage_rows, indent=4)
            updated_storage_data = {}
            for row in storage_rows:
                attribute = row['Attribute']
                value = row['Value']
                if attribute == "Waiting Time in Weeks":
                    key = "waiting_time_in_weeks"
                elif attribute == "Initial Quantity":
                    key = "initial_quantity"
                elif attribute == "Units per Batch":
                    key = "units_per_batch"
                elif attribute == "Level":
                    key = "level"     
                else:
                    key = None
                
                if key:
                    updated_storage_data[key] = int(value)

            with open('storage.json', 'r') as file:
                storage_data = json.load(file)
            
            if storage_id in storage_data:
                if 'chairs2' in storage_id:
                    new_id = 'chairs'
                elif 'frame2' in storage_id:
                    new_id = 'frame'
                else:
                    new_id = storage_id
                for key, value in updated_storage_data.items():
                    if key in storage_data[new_id]:
                        storage_data[new_id][key] = value
            
            with open('storage.json', 'w') as file:
                json.dump(storage_data, file, indent=4)
            ghp.ghp()
            mrp.mrp('chairs', 'frame')
            mrp.mrp('frame', 'wooden_construction_elements')
            mrp.mrp('frame', 'nails')
            mrp.mrp('chairs', 'padding')

        

    return table_container

    
def runDashApp():
    app.layout = html.Div([
    html.Button('🔄 RELOAD 🔄', id='button'),
    html.Div(id='output-div'),
    create_table("planned_order.json", production_data_ghp_map, "Initial GHP Data:", True, "chairs", storage_ghp_data_map),
    create_table("planned_orders_ghp_summary.json", production_data_ghp_map, "Final GHP structure:", True, "chairs2", storage_ghp_data_map),
    create_table("mrp/output/padding.json", production_data_map, "MRP Data: padding", False, "padding", storage_data_map),
    create_table("mrp/output/frame.json", production_data_map, "MRP Data: frame", False, "frame", storage_data_map),
    create_table("mrp/output/nails.json", production_data_map, "MRP Data: nails", False, "nails", storage_data_map),
    create_table("mrp/output/wooden_construction_elements.json", production_data_map, "MRP Data: wooden construction elements", False, "wooden_construction_elements", storage_data_map),



    ])

    @app.callback(
        Output('output-div', 'children'),
        [Input('button', 'n_clicks')]
    )
    def update_output(n_clicks):
        if n_clicks is not None:
            print('reload...')
            os._exit(0)
        return None


    
    app.run_server(debug=True)
