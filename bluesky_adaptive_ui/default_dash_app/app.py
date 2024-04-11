import argparse
import json
import os

import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
import requests
from dash.dependencies import Input, Output, State

agent_address = "localhost"  # Default address
agent_port = 60615

DASH_REQUEST_PATHNAME_PREFIX = str(os.getenv("DASH_REQUEST_PATHNAME_PREFIX", "/"))
print(DASH_REQUEST_PATHNAME_PREFIX)


def set_agent_address(address):
    global agent_address
    agent_address = address


def set_agent_port(port):
    global agent_port
    agent_port = port


def initial_bool_query(variable_name):
    response = requests.get(f"http://{agent_address}:{agent_port}/api/variable/{variable_name}")
    if response.status_code == 200:
        return str(response.json().get(variable_name, "UNKNOWN")) in ["True", "true", "on", "front"]
    else:
        return f"http://{agent_address}:{agent_port}/api/variable/{variable_name}"


app = dash.Dash(__name__, requests_pathname_prefix=f"{DASH_REQUEST_PATHNAME_PREFIX}")
app.layout = html.Div(
    children=[
        html.Div(
            className="dashboard-column",
            style={
                "width": "100%",
                "display": "inline-block",
                "vertical-align": "top",
                "horizontal-align": "center",
                "border": "2px solid black",
                "padding": "5",
                "margin": "0px",
            },
            children=[
                html.H1(id="agent-header", children="Agent Switchboard", style={"text-align": "center"}),
                html.Div(
                    style={"display": "flex", "justify-content": "space-evenly"},
                    children=[
                        html.Div(
                            style={
                                "display": "flex",
                                "flex-direction": "column",
                                "align-items": "center",
                                "justify-content": "center",
                            },
                            children=[
                                daq.Indicator(
                                    id="indicator-ask-on-tell",
                                    label="Continuous Asking",
                                    labelPosition="top",
                                    width=20,
                                    height=20,
                                    color="black",
                                ),
                                html.Button("On/Off", id="button-ask-on-tell", n_clicks=0),
                                html.Div(id="ask-on-tell-output", style={"text-align": "center", "color": "red"}),
                            ],
                        ),
                        html.Div(
                            style={
                                "display": "flex",
                                "flex-direction": "column",
                                "align-items": "center",
                                "justify-content": "center",
                            },
                            children=[
                                daq.Indicator(
                                    id="indicator-report-on-tell",
                                    label="Continuous Reporting",
                                    labelPosition="top",
                                    width=20,
                                    height=20,
                                    color="black",
                                ),
                                html.Button("On/Off", id="button-report-on-tell", n_clicks=0),
                                html.Div(
                                    id="report-on-tell-output", style={"text-align": "center", "color": "red"}
                                ),
                            ],
                        ),
                        html.Div(
                            style={
                                "display": "flex",
                                "flex-direction": "column",
                                "align-items": "center",
                                "justify-content": "center",
                            },
                            children=[
                                daq.Indicator(
                                    id="indicator-queue-front",
                                    label="Add to Front",
                                    labelPosition="top",
                                    width=20,
                                    height=20,
                                    color="black",
                                ),
                                html.Button("On/Off", id="button-queue-front", n_clicks=0),
                                html.Div(id="queue-front-output", style={"text-align": "center", "color": "red"}),
                            ],
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    "Generate Report",
                                    id="trigger-generate-report",
                                    n_clicks=0,
                                    style={"background-color": "darkgreen", "color": "white"},
                                ),
                                html.Div(id="generate-report-output"),
                            ]
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    "Generate Suggestion for Queue",
                                    id="trigger-add-suggestion-queue",
                                    n_clicks=0,
                                    style={"background-color": "darkgreen", "color": "white"},
                                ),
                                html.Div(id="add-to-queue-output"),
                            ]
                        ),
                    ],
                ),
                html.Div(style={"margin-bottom": "30px"}),
                html.Div(
                    style={
                        "display": "flex",
                        "flex-direction": "column",
                        "align-items": "center",
                        "justify-content": "center",
                    },
                    children=[
                        html.Button(
                            "Tell Agent By UID",
                            id="submit-uids-button",
                            n_clicks=0,
                            style={
                                "background-color": "darkgreen",
                                "color": "white",
                                "margin": "auto",
                                "display": "block",
                                "width": "45%",
                            },
                        ),
                        dcc.Textarea(
                            id="submit-uids-input",
                            placeholder="Enter list of UIDs to tell the agent about.\
                                \nThis can be in a comma separated list, or with one UID per line.",
                            style={
                                "width": "80%",
                                "height": "100px",
                                "horizontal-align": "center",
                            },
                        ),
                        html.Div(id="submit-uids-output"),
                    ],
                ),
                html.Div(style={"margin-bottom": "15px"}),
            ],
        ),
        html.Div(
            className="dashboard-column",
            style={"width": "50%", "display": "inline-block", "vertical-align": "top"},
            children=[
                html.H1("Variable Dashboard", style={"text-align": "center"}),
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
                html.H1("Method Dashboard", style={"text-align": "center"}),
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


def _toggle(n_clicks, n_intervals, variable_name):
    if n_clicks > 0:
        response = requests.get(f"http://{agent_address}:{agent_port}/api/variable/{variable_name}")

        if response.status_code == 200:
            resp_str = str(response.json().get(variable_name, "UNKNOWN"))
            new_value = resp_str not in ["True", "true", "on"]
            payload = {"value": new_value}
            response = requests.post(
                f"http://{agent_address}:{agent_port}/api/variable/{variable_name}", json=payload
            )
            if response.status_code == 200:
                return ("", "green" if new_value else "gray")
            else:
                return ("FAILING", "black")

        else:
            return (f"http://{agent_address}:{agent_port}/api/variable/{variable_name}", "black")

    if n_intervals > 0:
        response = requests.get(f"http://{agent_address}:{agent_port}/api/variable/{variable_name}")
        if response.status_code == 200:
            resp_str = str(response.json().get(variable_name, "UNKNOWN"))
            return ("", "green" if resp_str in ["True", "true", "on"] else "grey")
        else:
            return (f"http://{agent_address}:{agent_port}/api/variable/{variable_name}", "black")
    else:
        return "", "black"


@app.callback(
    [Output("ask-on-tell-output", "children"), Output("indicator-ask-on-tell", "color")],
    [
        Input("button-ask-on-tell", "n_clicks"),
        dash.dependencies.Input("refresh-page", "n_intervals"),
    ],
)
def toggle_ask_on_tell(n_clicks, n_intervals):
    ret = _toggle(n_clicks, n_intervals, "ask_on_tell")
    return ret


@app.callback(
    [Output("report-on-tell-output", "children"), Output("indicator-report-on-tell", "color")],
    [
        Input("button-report-on-tell", "n_clicks"),
        dash.dependencies.Input("refresh-page", "n_intervals"),
    ],
)
def toggle_report_on_tell(n_clicks, n_intervals):
    return _toggle(n_clicks, n_intervals, "report_on_tell")


@app.callback(
    [Output("queue-front-output", "children"), Output("indicator-queue-front", "color")],
    [Input("button-queue-front", "n_clicks"), Input("refresh-page", "n_intervals")],
)
def toggle_queue_add_position(n_clicks, n_intervals):
    variable_name = "queue_add_position"
    if n_clicks > 0:
        response = requests.get(f"http://{agent_address}:{agent_port}/api/variable/{variable_name}")

        if response.status_code == 200:
            resp_str = str(response.json().get(variable_name, "UNKNOWN"))
            new_value = "front" if resp_str != "front" else "back"
            payload = {"value": new_value}
            response = requests.post(
                f"http://{agent_address}:{agent_port}/api/variable/{variable_name}", json=payload
            )
            if response.status_code == 200:
                return ["", "green" if new_value == "front" else "gray"]
            else:
                return ["FAILING", "black"]

        else:
            return [f"http://{agent_address}:{agent_port}/api/variable/{variable_name}", False]

    if n_intervals > 0:
        response = requests.get(f"http://{agent_address}:{agent_port}/api/variable/{variable_name}")
        if response.status_code == 200:
            resp_str = str(response.json().get(variable_name, "UNKNOWN"))
            return ["", "green" if resp_str == "front" else "grey"]
        else:
            return [f"http://{agent_address}:{agent_port}/api/variable/{variable_name}", False]
    else:
        return "", "black"


@app.callback(Output("add-to-queue-output", "children"), Input("trigger-add-suggestion-queue", "n_clicks"))
def trigger_add_to_queue(n_clicks):
    if n_clicks:
        payload = {"value": [[1], {}]}
        response = requests.post(
            f"http://{agent_address}:{agent_port}/api/variable/add_suggestions_to_queue", json=payload
        )
        if response.status_code == 200:
            return html.Div(children=[html.P("Success")], style={"text-align": "center", "color": "green"})
        else:
            return html.Div(children=[html.P("FAILING")], style={"text-align": "center", "color": "red"})


@app.callback(Output("generate-report-output", "children"), Input("trigger-generate-report", "n_clicks"))
def trigger_generate_report(n_clicks):
    if n_clicks:
        payload = {"value": [[], {}]}
        response = requests.post(f"http://{agent_address}:{agent_port}/api/variable/generate_report", json=payload)
        if response.status_code == 200:
            return html.Div(children=[html.P("Success")], style={"text-align": "center", "color": "green"})
        else:
            return html.Div(children=[html.P("FAILING")], style={"text-align": "center", "color": "red"})


@app.callback(
    dash.dependencies.Output("submit-uids-output", "children"),
    [dash.dependencies.Input("submit-uids-button", "n_clicks")],
    [dash.dependencies.State("submit-uids-input", "value")],
)
def submit_uids(n_clicks, args=None):
    if n_clicks:
        if not args:
            return
        else:
            args = [
                item.strip() for input_line in args.split("\n") for item in input_line.split(",") if item.strip()
            ]
        print(args)
        payload = {
            "value": [
                [args],
                {},
            ]
        }
        response = requests.post(
            f"http://{agent_address}:{agent_port}/api/variable/tell_agent_by_uid", json=payload
        )
        if response.status_code == 200:
            return html.Div(children=[html.P("Success")], style={"text-align": "center", "color": "green"})
        else:
            return html.Div(children=[html.P("FAILING")], style={"text-align": "center", "color": "red"})


@app.callback(
    Output("variable-output", "children"),
    [
        Input("get-variable-button", "n_clicks"),
        Input("variable-name-input", "n_submit"),
    ],
    [State("variable-name-input", "value")],
)
def get_variable(n_clicks, n_submit, variable_name):
    if n_clicks or n_submit:
        response = requests.get(f"http://{agent_address}:{agent_port}/api/variable/{variable_name}")
        if response.status_code == 200:
            return str(response.json().get(variable_name, "UNKNOWN"))
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
    if n_clicks or n_submit:
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
        payload = {"value": [args, kwargs]}
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


@app.callback(
    Output("header", "children"),
    Input("refresh-page", "n_intervals"),
)
def refresh_header(n_intervals):
    default_header = html.H1("Agent Switchboard: Unregistered Agent Name", style={"text-align": "center"})
    response = requests.get(f"http://{agent_address}:{agent_port}/api/variable/instance_name")
    if response.status_code == 200:
        return default_header
    else:
        return f"Agent Switchboard: {response.text}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=str, default="8050", help="Dash server port")
    parser.add_argument("--agent-address", type=str, default="localhost", help="Agent API address")
    parser.add_argument("--agent-port", type=str, default="60615", help="Agent API address")
    args = parser.parse_args()
    set_agent_address(args.agent_address)
    set_agent_port(args.agent_port)

    app.run_server(debug=False, port=args.port, host="0.0.0.0")
