import json
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import pandas as pd
from dictionary import *
from collections import OrderedDict

app = dash.Dash(__name__)

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

def create_table(file_name, map_name, table_name, editable):
    json_data = read_json_file(file_name)
    
    data_rows = prepare_table_data(json_data, map_name)

    columns = [{'name': '', 'id': 'Production Data'}] + \
              [{'name': f'Week {i}', 'id': f'Week {i}'} for i in range(1, 11)]

    table_id = file_name.replace('.json', '') + '_table'
    div_id = file_name.replace('.json', '') + '_div'

    table_container = html.Div([
        html.H1(table_name),
        dash_table.DataTable(
            id=table_id,
            columns=columns,
            data=data_rows,
            editable=editable
        ),
        html.Div(id='output_' + div_id),
    ])
    
    # Tutaj to jest tylko po to żeby wyświetlić jsona jak on się zmienia, ale jest to na razie nie potrzebne
    
    @app.callback(
        Output('output_' + div_id, 'children'),
        [Input(table_id, 'data')]
    )
    def update_output(rows):
        df1 = pd.DataFrame(rows)

        # otwieram jsona

        # skrypt ktory aktualzuje dane w jsonie i podmienia je z danymi z rows

        # zapisuje jsona

        # refresh

        return html.Div([
            html.H3('Dane:' + table_id),
            html.Pre(json.dumps(rows,indent=4))
        ])

    
    return table_container

def create_storage_table(id, map_name, editable):
    table_data = prepare_storage_table_data(id, map_name)

    columns = [{'name': '', 'id': 'Attribute'},
               {'name': 'Value', 'id': 'Value'}]

    table_id = f"{id}_storage_table"

    table_container = html.Div([
        dash_table.DataTable(
            id=table_id,
            columns=columns,
            data=table_data,
            style_header={'display': 'none'},
            style_data={
            'width': 135,
            },
            fill_width=False,
            css=[ { 'selector': 'tr:first-child', 'rule': 'display: none'},],
            
        ),
    ])
    
    return table_container
    
def runDashApp():
    app.layout = html.Div([
    create_table("planned_order.json", production_data_ghp_map, "Initial GHP Data:", True),
    html.Button(
        ['Update'],
        id='btn1'
    ),
    create_storage_table("chairs", storage_ghp_data_map, True),
    create_table("planned_orders_ghp_summary.json", production_data_ghp_map, "Final GHP structure:", True),
    create_storage_table("chairs", storage_ghp_data_map, True),
    create_table("mrp/output/padding.json", production_data_map, "MRP Data: padding", True),
    create_storage_table("padding", storage_data_map, True),
    create_table("mrp/output/frame.json", production_data_map, "MRP Data: frame", True),
    create_storage_table("frame", storage_data_map, True),
    create_table("mrp/output/nails.json", production_data_map, "MRP Data: nails", True),
    create_storage_table("frame", storage_data_map, True),
    create_table("mrp/output/wooden_construction_elements.json", production_data_map, "MRP Data: wooden construction elements", True),
    create_storage_table("wooden_construction_elements", storage_data_map, True),
    html.Button(
        ['Update'],
        id='btn2'
    ),
    ])
    
    app.run_server(debug=True)    
