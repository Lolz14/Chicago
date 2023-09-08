import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

df = pd.read_csv('Crimes_-_2001_to_Present.csv')


df = df.drop(columns=['ID', 'Case Number',  'Beat',
       'District', 'Ward', 'Community Area', 'FBI Code', 'X Coordinate',
       'Y Coordinate', 'Latitude', 'Longitude',
       'Location'])
df['Block'] = df['Block'].str[:3]

grouped_data = df.groupby(['Primary Type', 'Block', 'Year']).size().reset_index(name='Count')

total_crimes = grouped_data.groupby('Primary Type')['Count'].sum().reset_index()
total_crimes['Primary Type'] = total_crimes['Primary Type'] + ' (Total)'

all_crimes = pd.concat([grouped_data['Primary Type'], total_crimes['Primary Type']])

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='crime-dropdown',
        options=[{'label': crime, 'value': crime} for crime in all_crimes.unique()],
        value=all_crimes.unique()[0],
        multi=False
    ),
    dcc.Graph(id='heatmap-graph')
])

@app.callback(
    Output('heatmap-graph', 'figure'),
    [Input('crime-dropdown', 'value')]
)
def update_heatmap(selected_crime):
    if "(Total)" in selected_crime:
        total_data = grouped_data.groupby(['Block', 'Year'])['Count'].sum().reset_index()
        pivot_table = total_data.pivot_table(index='Block', columns='Year', values='Count', aggfunc='sum', fill_value=0)
    else:
        filtered_data = grouped_data[grouped_data['Primary Type'] == selected_crime]
        pivot_table = filtered_data.pivot_table(index='Block', columns='Year', values='Count', aggfunc='sum', fill_value=0)

    heatmap = go.Heatmap(z=pivot_table.values,
                         x=pivot_table.columns,
                         y=pivot_table.index,
                         colorscale="YlOrRd")

    layout = go.Layout(title=f"Interactive Heatmap for {selected_crime}",
                       xaxis=dict(title="Year"),
                       yaxis=dict(title="Block"))

    fig = go.Figure(data=[heatmap], layout=layout)
    return fig

# Step 8: Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)