import json
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import pandas as pd
from dictionary import *

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
            data_by_attribute = {
                attribute: {f'Week {order["week"]}': order[attribute] for order in json_data['orders']}
                for attribute in attributes
            }
        else:
            attributes = set(json_data[0].keys()) - {'week'}
            data_by_attribute = {
                attribute: {f'Week {entry["week"]}': entry[attribute] for entry in json_data}
                for attribute in attributes
            }
        return [{'Production Data': production_data_map.get(attr, attr), **values} for attr, values in data_by_attribute.items()]
    return []

def createDash():
    planned_order_data = read_json_file('planned_order.json')
    planned_orders_ghp_summary_data = read_json_file('planned_orders_ghp_summary.json')
    padding_data = read_json_file('padding.json')
    
    # Przekazujemy production_data do funkcji prepare_table_data
    data_rows_planned_order = prepare_table_data(planned_order_data, production_data_map)
    data_rows_planned_orders_ghp_summary = prepare_table_data(planned_orders_ghp_summary_data, production_data_map)
    data_rows_padding = prepare_table_data(padding_data, production_data_map)

    columns = [{'name': '', 'id': 'Production Data'}] + \
              [{'name': f'Week {i}', 'id': f'Week {i}'} for i in range(1, 11)]

    app.layout = html.Div([
        html.H1("Tabelki z danymi produkcji"),
        dash_table.DataTable(
            id='table-planned-order',
            columns=columns,
            data=data_rows_planned_order,
            editable=True
        ),
        html.H1("Tabelka podsumowania GHP"),
        dash_table.DataTable(
            id='table-planned-orders-ghp-summary',
            columns=columns,
            data=data_rows_planned_orders_ghp_summary,
            editable=True
        ),
        html.H1("Dodatkowa Tabelka z Padding Data"),
        dash_table.DataTable(
            id='table-padding-data',
            columns=columns,
            data=data_rows_padding,
            editable=True
        ),
        html.Div(id='output')
    ])

    @app.callback(
        Output('output', 'children'),
        [Input('table-planned-order', 'data'), Input('table-planned-orders-ghp-summary', 'data'), Input('table-padding-data', 'data')]
    )
    def update_output(rows_planned_order, rows_planned_orders_ghp_summary, rows_padding):
        df1 = pd.DataFrame(rows_planned_order)
        df2 = pd.DataFrame(rows_planned_orders_ghp_summary)
        df3 = pd.DataFrame(rows_padding)
        return html.Div([
            html.H3('Dane z tabeli planowania:'),
            html.Pre(df1.to_json(indent=2)),
            html.H3('Dane z tabeli GHP:'),
            html.Pre(df2.to_json(indent=2)),
            html.H3('Dane z tabeli Padding:'),
            html.Pre(df3.to_json(indent=2))
        ])

if __name__ == '__main__':
    createDash()
    app.run_server(debug=True)
