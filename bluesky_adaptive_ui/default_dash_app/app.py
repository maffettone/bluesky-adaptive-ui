import argparse
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import requests

agent_address = "localhost"  # Default address
agent_port = 60615


def set_agent_address(address):
    global agent_address
    agent_address = address


def set_agent_port(port):
    global agent_port
    agent_port = port


app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.Div(
            className="dashboard-column",
            style={"width": "50%", "display": "inline-block", "vertical-align": "top"},
            children=[
                html.H1("Variable Dashboard"),
                html.Div(
                    id="variable-container",
                    children=[
                        dcc.Input(
                            id="variable-name-input",
                            type="text",
                            placeholder="Enter variable name",
                        ),
                        html.Button("Get Variable", id="get-variable-button", n_clicks=0),
                        html.Div(id="variable-output"),
                        dcc.Input(
                            id="variable-name-update-input",
                            type="text",
                            placeholder="Enter variable name",
                        ),
                        dcc.Input(
                            id="new-value-input",
                            type="text",
                            placeholder="Enter new value",
                        ),
                        html.Button(
                            "Update Variable",
                            id="update-variable-button",
                            n_clicks=0,
                        ),
                        html.Div(id="variable-input-success"),
                    ],
                ),
                html.H1("Available Variables and Methods"),
                html.Button("Refresh Available", id="get-names-button", n_clicks=0),
                html.Div(id="names-output"),
            ],
        ),
        html.Div(
            className="dashboard-column",
            style={"width": "50%", "display": "inline-block", "vertical-align": "top"},
            children=[
                html.H1("Method Dashboard"),
                html.P(
                    "This is a little less user-friendly, but can be used to call an arbitrary method that has been "
                    "registered for your agent. You are responsible for knowing the expected arguments and keyword "
                    "arguments. A responsible use case would be a method that takes no arguments, like "
                    "enable_continuous_reporting."
                ),
                html.Div(
                    id="method-container",
                    children=[
                        dcc.Input(
                            id="method-name-input",
                            type="text",
                            placeholder="Enter method name",
                        ),
                        dcc.Textarea(
                            id="method-args-input",
                            placeholder="Enter list of arguments, e.g., \n['det1', 10, 'det2', 15]",
                            style={"width": "100%", "height": "50px"},
                        ),
                        dcc.Textarea(
                            id="method-kwargs-input",
                            placeholder='Enter dictionary of keyword arguments using double-quotes ("), e.g.,\n'
                            '{"det": "det1", "pos", 15}',
                            style={"width": "100%", "height": "50px"},
                        ),
                        html.Button("Call method", id="call-method-button", n_clicks=0),
                        html.Div(id="call-method-success"),
                    ],
                ),
            ],
        ),
        dcc.Interval(
            id="refresh-page",
            interval=0.1 * 1000,
            n_intervals=0,
            max_intervals=1,
            disabled=False,
        ),
    ],
    className="dashboard-container",
)


@app.callback(
    dash.dependencies.Output("variable-output", "children"),
    [
        dash.dependencies.Input("get-variable-button", "n_clicks"),
        dash.dependencies.Input("variable-name-input", "n_submit"),
    ],
    [dash.dependencies.State("variable-name-input", "value")],
)
def get_variable(n_clicks, n_submit, variable_name):
    if n_clicks > 0 or n_submit > 0:
        response = requests.get(f"http://{agent_address}:{agent_port}/api/variable/{variable_name}")
        if response.status_code == 200:
            return response.json().get(variable_name, "UNKNOWN")
        else:
            return f"http://{agent_address}:{agent_port}/api/variable/{variable_name}"


@app.callback(
    dash.dependencies.Output("variable-input-success", "children"),
    [
        dash.dependencies.Input("update-variable-button", "n_clicks"),
        dash.dependencies.Input("new-value-input", "n_submit"),
    ],
    [
        dash.dependencies.State("variable-name-update-input", "value"),
        dash.dependencies.State("new-value-input", "value"),
    ],
)
def update_variable(n_clicks, n_submit, variable_name, new_value):
    if n_clicks > 0 or n_submit > 0:
        payload = {"value": new_value}
        response = requests.post(f"http://{agent_address}:{agent_port}/api/variable/{variable_name}", json=payload)
        if response.status_code == 200:
            return response.json().get(variable_name, "UNKNOWN")


@app.callback(
    dash.dependencies.Output("call-method-success", "children"),
    [dash.dependencies.Input("call-method-button", "n_clicks")],
    [
        dash.dependencies.State("method-name-input", "value"),
        dash.dependencies.State("method-args-input", "value"),
        dash.dependencies.State("method-kwargs-input", "value"),
    ],
)
def call_method(n_clicks, method_name, args=None, kwargs=None):
    if n_clicks:
        args = json.loads(args) if args is not None else []
        kwargs = json.loads(kwargs) if kwargs is not None else {}
        payload = {"value": {"args": args, "kwargs": kwargs}}
        response = requests.post(f"http://{agent_address}:{agent_port}/api/variable/{method_name}", json=payload)
        if response.status_code == 200:
            return "Success"
        else:
            html.Div(payload)


@app.callback(
    dash.dependencies.Output("names-output", "children"),
    [
        dash.dependencies.Input("get-names-button", "n_clicks"),
        dash.dependencies.Input("refresh-page", "n_intervals"),
    ],
)
def get_names(n_clicks, n_intervals):
    if n_clicks > 0 or n_intervals > 0:
        response = requests.get(f"http://{agent_address}:{agent_port}/api/variables/names")
        if response.status_code == 200:
            data = response.json()
            names = data.get("names", [])
            table = dash_table.DataTable(
                data=[{"Names": name} for name in names],
                columns=[{"name": "Names", "id": "Names"}],
                style_data={"whiteSpace": "normal", "height": "auto"},
                style_cell={"padding": "8px", "textAlign": "left"},
                style_header={"fontWeight": "bold"},
                fill_width=False,
            )
            return table


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=str, default="8050", help="Dash server port")
    parser.add_argument("--agent-address", type=str, default="localhost", help="Agent API address")
    parser.add_argument("--agent-port", type=str, default="60615", help="Agent API address")
    args = parser.parse_args()
    set_agent_address(args.agent_address)
    set_agent_port(args.agent_port)

    app.run_server(debug=True, port=args.port)
