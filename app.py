import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

combined_10 = pd.read_csv('bubblechart_slider.csv')
df_2022 = pd.read_csv('bubblechart_change.csv')


color_map = {
    "Sub-Saharan Africa": "#E69F00",        
    "Eastern Europe": "#56B4E9",            
    "Latin America & the Caribbean": "#009E73",  
    "Western Europe": "#F0E442",            
    "South Asia": "#0072B2",               
    "Middle East & North Africa": "#D55E00", 
    "Caucasus & Central Asia": "#CC79A7",  
    "East Asia": "#999999",                
    "North America": "#882255",            
    "Oceania": "#117733",                 
}

quartile_color_map = {
    "Q1: més llibertat": "#2C7BB6",   
    "Q2": "#ABD9E9",                  
    "Q3": "#FDAE61",                  
    "Q4: menys llibertat": "#D7191C"  
}

scaler_combined = MinMaxScaler()
combined_10["scaled_size"] = scaler_combined.fit_transform(combined_10[["Log GDP per capita"]])
scaler_2022 = MinMaxScaler()
df_2022["scaled_size"] = scaler_2022.fit_transform(df_2022[["Log GDP per capita"]])

combined_10 = combined_10.sort_values(by='year')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Situació dels drets de les dones i la felicitat al món"),
    html.H5("Aquesta visualització explora com la llibertat personal de les dones varia segons la regió, a partir 
    de cinc indicadors clau relacionats amb drets i condicions específiques. Aquests drets es projecten juntament 
    amb el nivell de la felicitat dels països, mostrant possibles connexions entre l'igualtat i el benestar."),
    html.Div([
        html.Label("La mida de les bombolles representa el PIB per càpita: com més gran la bombolla, més alt el PIB del país."),
        dcc.RadioItems(
            id='mode',
            options=[
                {'label': 'Evolució temporal', 'value': 'slider'},
                {'label': 'Canvi 2012–2022', 'value': 'delta'}
            ],
            value='slider',
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        )
    ], style={'maxWidth': '1000px', 'margin': 'auto', 'padding': '20px'}),

    dcc.Graph(id='bubble_chart')
])

@app.callback(
    Output('bubble_chart', 'figure'),
    Input('mode', 'value')
)

def update_graph(mode):
    if mode == 'slider':
        fig = px.scatter(
            combined_10,
            x='women_specific_pf',
            y='Life Ladder',
            size="scaled_size",
            color='region',
            animation_frame='year',
            animation_group='countries',
            hover_name='countries',
            color_discrete_map=color_map,
            category_orders={"region": [
                "Western Europe",
                "North America",
                "Oceania",
                "Eastern Europe",
                "East Asia",
                "Middle East & North Africa",
                "Latin America & the Caribbean",
                "Caucasus & Central Asia",
                "South Asia", 
                "Sub-Saharan Africa"]},
            custom_data=['region', 'year', 'women_specific_pf', 'Life Ladder']
        )
        fig.for_each_trace(
            lambda trace: trace.update(
                hovertemplate="<b>%{hovertext}</b><br>" + 
                              "%{customdata[0]}<br><br>" + 
                              "Any: %{customdata[1]}<br>" +
                              "Índex Llibertat: %{customdata[2]:.2f}<br>" +
                              "Índex Felicitat: %{customdata[3]:.2f}<br>" +
                              "<extra></extra>"
            )
        )

        for frame in fig.frames:
            for data in frame.data:
                data.hovertemplate = (
                    "<b>%{hovertext}</b><br>" + 
                    "%{customdata[0]}<br><br>" + 
                    "Any: %{customdata[1]}<br>" +
                    "Índex Llibertat: %{customdata[2]:.2f}<br>" +
                    "Índex Felicitat: %{customdata[3]:.2f}<br>" +
                    "<extra></extra>"
                )

        
        fig.update_layout(title="Evolucio de la Llibertat personal de les dones i la Felicitat per país",
                          xaxis_title="Llibertat dones",
                          yaxis_title="Felicitat",
                          legend_title_text=None,
                          paper_bgcolor='white',
                          plot_bgcolor='white',
                          xaxis=dict(showgrid=False),
                          yaxis=dict(showgrid=False),
                          transition_duration=1000)
    else:
        fig = px.scatter(
            df_2022,
            x='delta_wspf',
            y='delta_life_ladder',
            size='scaled_size',
            color='wspf_quartile',
            color_discrete_map=quartile_color_map,
            hover_name='countries',
            title="Canvi en la Llibertat de les dones i la Felicitat per país (última dècada)",
            category_orders={"wspf_quartile": [
            "Q1: més llibertat",
            "Q2",
            "Q3",
            "Q4: menys llibertat"]},
            custom_data=['region', 'wspf_quartile', 'delta_wspf', 'delta_life_ladder']
            )
        
        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>" +
                "%{customdata[0]}<br><br>" +
                "Quartil %{customdata[1]}<br>" +
                "Variació Llibertat: %{customdata[2]:.2f}<br>" +
                "Variació Felicitat: %{customdata[3]:.2f}<br>" +
                "<extra></extra>"
            )
        )

        fig.add_vline(x=0, line_dash='dash', line_color='gray')
        fig.add_hline(y=0, line_dash='dash', line_color='gray')
        fig.update_layout(legend_title_text="Llibertat Dones (2022)")
        
        min_row = df_2022[df_2022['women_specific_pf'] == df_2022['women_specific_pf'].min()].iloc[0]
        max_row = df_2022[df_2022['women_specific_pf'] == df_2022['women_specific_pf'].max()].iloc[0]
        fig.add_annotation(
            x=min_row['delta_wspf'],
            y=min_row['delta_life_ladder'],
            text=f"{min_row['countries']} (menys llibertat (2022))",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-50,
            bgcolor="#D7191C",
            font=dict(color="white")
        )
        fig.add_annotation(
            x=max_row['delta_wspf'],
            y=max_row['delta_life_ladder'],
            text=f"{max_row['countries']} (més llibertat (2022))",
            showarrow=True,
            arrowhead=2,
            ax=-40,
            ay=100,  
            bgcolor="#2C7BB6",
            font=dict(color="white")
        )

        fig.update_layout(
                          xaxis_title="Llibertat dones", 
                          yaxis_title="Felicitat",
                          paper_bgcolor='white',
                          plot_bgcolor='white',
                          xaxis=dict(showgrid=False),
                          yaxis=dict(showgrid=False),
                          transition_duration=500)

    return fig


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)

