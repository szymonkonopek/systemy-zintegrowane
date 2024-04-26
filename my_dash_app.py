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

def create_table(file_name, map_name, table_name, editable):
    json_data = read_json_file(file_name)
    
    data_rows = prepare_table_data(json_data, map_name)

    columns = [{'name': '', 'id': 'Production Data'}] + \
              [{'name': f'Week {i}', 'id': f'Week {i}'} for i in range(1, 11)]

    table_id = file_name.replace('.json', '') + '_table'
    div_id = file_name.replace('.json', '') + '_div'

    # Stwórz oddzielny kontener dla tabeli i wyników
    table_container = html.Div([
        html.H1(table_name),
        dash_table.DataTable(
            id=table_id,
            columns=columns,
            data=data_rows,
            editable=editable
        ),
        html.Div(id='output_' + div_id)
    ])
    
    @app.callback(
        Output('output_' + div_id, 'children'),
        [Input(table_id, 'data')]
    )
    def update_output(rows):
        df1 = pd.DataFrame(rows)
        return html.Div([
            html.H3('Dane:' + table_id),
            html.Pre(df1.to_json(indent=2))
        ])
    
    return table_container

    
def runDashApp():
    app.layout = html.Div([
    create_table("planned_order.json", production_data_ghp_map, "Initial GHP Data:", True),
    create_table("planned_orders_ghp_summary.json", production_data_ghp_map, "Final GHP structure:", True),
    create_table("padding.json", production_data_map, "MRP Data: padding", True)
    ])
    
    app.run_server(debug=True)    
