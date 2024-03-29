from flask import Flask, render_template_string, request , make_response, jsonify, send_file , render_template
import plotly.express as px
import json
import plotly.utils
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from flask_socketio import SocketIO, emit


import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder


from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
socketio = SocketIO(app)
auth = HTTPBasicAuth()

users = {
    "aaron": "hmmm",
    # Add other users here as needed
}


@auth.error_handler
def auth_error(status):
    return make_response("Hmm.", status)



@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

@socketio.on('broadcast_sound')  # Changed to 'broadcast_sound'
def handle_click(message):
    emit('notification', {'msg': 'Button was clicked!'}, broadcast=True)

@app.route('/')
def index():
    return render_template('tester.html')








#@socketio.on('housing_avalible')
#def handle_click(message):
    emit('notification', {'msg': 'ROOMS AVALIBLE!'}, broadcast=True)


parameters_list = []

@app.route("/casa")
def housingportal():

    # Define the correct password for adding to the list
    correct_password = "whyfuckwithme"

    # Get the parameters from the URL
    password = request.args.get('password')
    status = request.args.get('status')
    timestamp = request.args.get('timestamp')

    # Check if all parameters are provided and the password is correct
    if password and status and timestamp:
        if password == correct_password:
            # Save the parameters as a dictionary in the list
            parameters_list.append({'password': password, 'status': status, 'timestamp': timestamp})
            if status =='room_available':
                 handle_click("Room available")

            return "Parameters added successfully"
        else:
            return "Incorrect password"
    elif not password and not status and not timestamp:
        # If no parameters are provided, display the graph
        fig = create_table(parameters_list)
        line_fig = create_line_graph()
        # Encode the figures in JSON
        graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
        line_graphJSON = json.dumps(line_fig, cls=PlotlyJSONEncoder)
        return render_template("casa.html", graphJSON=graphJSON, line_graphJSON=line_graphJSON)
    else:
        return "Missing parameters"

def create_table(parameters_list):
    # Create a table figure
    header_values = ["Status", "Timestamp"]
    cell_colors = [
        ['Red' if entry['status'] == 'no_room' else 'Green' if entry['status'] == 'room_available' else 'Grey' for entry in parameters_list]
    ]
    cell_values = [
        [entry['status'] for entry in parameters_list],
        [entry['timestamp'] for entry in parameters_list]
    ]

    fig = go.Figure(data=[go.Table(
        header=dict(values=header_values),
        cells=dict(values=cell_values, fill_color=cell_colors))
    ])
    return fig

def create_line_graph():
    # Create a line graph figure
    x_values = list(range(10)) # Replace with actual x values if necessary
    y_values = [ 100 -x*10 for x in x_values]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='lines'))
    fig.update_layout(
        title='Time vs % Change of Getting a Room',
        xaxis_title='Days',
        yaxis_title='% Change of Getting a Room'
    )
    return fig

    # casa?password=password&status=no room&timestamp=test


def create_plot(file_paths):
    data = []
    for file_path in file_paths:
        # Load the data
        df = pd.read_csv(file_path)

        # Convert the 'date' column to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Generate a label from the file name
        label = os.path.splitext(os.path.basename(file_path))[0]

        # Add trace to the data
        data.append(go.Scatter(x=df['date'], y=df['price'], mode='lines+markers', name=label))

    layout = go.Layout(title='Price Comparison Over Time', xaxis=dict(title='Date'), yaxis=dict(title='Price'))
    fig = go.Figure(data=data, layout=layout)
    return json.dumps(fig, cls=PlotlyJSONEncoder)

@app.route('/tahoe')
def tahoe():
    file_paths = ['/home/alexlamstein/mysite/valley_data.csv', '/home/alexlamstein/mysite/mountain_data.csv','/home/alexlamstein/mysite/four_bedroom_residence_data.csv']  # Example file paths
    plot_json = create_plot(file_paths)
    return render_template('tahoe.html', plot_json=plot_json)



@app.route('/message')
def message():
    return render_template('message.html')

@socketio.on('send_message')
def handle_message(data):
    socketio.emit('broadcast_message', data)

    
if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
