#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load data
terr2 = pd.read_csv('modified_globalterrorismdb_0718dist.csv')

# Prepare location data
list_locations = terr2[['country_txt', 'latitude', 'longitude']]     .set_index('country_txt')[['latitude', 'longitude']].T.to_dict('dict')

# Define app title and layout
st.title("Global Terrorism Database (1970 - 2017)")
st.markdown("**Visualizing terrorism incidents around the world.**")

# Create sidebar for filters
st.sidebar.header("Filters")
region = terr2['region_txt'].unique()
selected_region = st.sidebar.selectbox("Select Region", region, index=4)  # Default to South Asia

# Update country options based on region selection
if selected_region:
    countries_in_region = terr2[terr2['region_txt'] == selected_region]['country_txt'].unique()
    selected_country = st.sidebar.selectbox("Select Country", countries_in_region, index=0)

selected_years = st.sidebar.slider("Select Years", 1970, 2017, (2010, 2017))

# Create Mapbox scatter plot
st.subheader("Map of Terrorism Incidents")
map_data = terr2.groupby(['region_txt', 'country_txt', 'provstate', 'city', 'iyear', 'latitude', 'longitude'])[['nkill', 'nwound']].sum().reset_index()
filtered_data = map_data[
    (map_data['region_txt'] == selected_region) &
    (map_data['country_txt'] == selected_country) &
    (map_data['iyear'] >= selected_years[0]) &
    (map_data['iyear'] <= selected_years[1])
]

if not filtered_data.empty:
    zoom = 3
    zoom_lat = list_locations[selected_country]['latitude']
    zoom_lon = list_locations[selected_country]['longitude']

    fig_map = go.Figure(go.Scattermapbox(
        lon=filtered_data['longitude'],
        lat=filtered_data['latitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=filtered_data['nwound'],
            color=filtered_data['nwound'],
            colorscale='hsv',
            showscale=False,
            sizemode='area'
        ),
        hoverinfo='text',
        hovertext=filtered_data[['region_txt', 'country_txt', 'provstate', 'city', 'longitude', 'latitude', 'nkill', 'nwound', 'iyear']].to_string(index=False)
    ))

    fig_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        hovermode='closest',
        mapbox=dict(
            accesstoken='pk.eyJ1IjoicXM2MjcyNTI3IiwiYSI6ImNraGRuYTF1azAxZmIycWs0cDB1NmY1ZjYifQ.I1VJ3KjeM-S613FLv3mtkw',  # Replace with your Mapbox token
            center=go.layout.mapbox.Center(lat=zoom_lat, lon=zoom_lon),
            style='dark',
            zoom=zoom
        ),
        autosize=True
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Bar and Line Chart
    st.subheader("Attack and Death Over Years")
    fig_bar_line = go.Figure()

    terr5 = terr2.groupby(['region_txt', 'country_txt', 'iyear'])['nkill'].sum().reset_index()
    terr6 = terr5[(terr5['region_txt'] == selected_region) & (terr5['country_txt'] == selected_country) & (terr5['iyear'] >= selected_years[0]) & (terr5['iyear'] <= selected_years[1])]

    fig_bar_line.add_trace(go.Scatter(
        x=terr6['iyear'],
        y=terr6['nkill'],
        mode='lines+markers',
        name='Death',
        line=dict(shape="spline", smoothing=1.3, width=3, color='#FF00FF'),
        marker=dict(size=10, symbol='circle', color='white',
                    line=dict(color='#FF00FF', width=2)
                    ),
        hoverinfo='text',
        hovertext=
        '<b>Region</b>: ' + terr6['region_txt'].astype(str) + '<br>' +
        '<b>Country</b>: ' + terr6['country_txt'].astype(str) + '<br>' +
        '<b>Year</b>: ' + terr6['iyear'].astype(str) + '<br>' +
        '<b>Death</b>: ' + [f'{x:,.0f}' for x in terr6['nkill']] + '<br>'
    ))

    terr7 = terr2.groupby(['region_txt', 'country_txt', 'iyear'])[['attacktype1', 'nwound']].sum().reset_index()
    terr8 = terr7[(terr7['region_txt'] == selected_region) & (terr7['country_txt'] == selected_country) & (terr7['iyear'] >= selected_years[0]) & (terr7['iyear'] <= selected_years[1])]

    fig_bar_line.add_trace(go.Bar(
        x=terr8['iyear'],
        y=terr8['attacktype1'],
        text=terr8['attacktype1'],
        texttemplate='%{text:.2s}',
        textposition='auto',
        name='Attack',
        marker=dict(color='orange'),
        hoverinfo='text',
        hovertext=
        '<b>Region</b>: ' + terr8['region_txt'].astype(str) + '<br>' +
        '<b>Country</b>: ' + terr8['country_txt'].astype(str) + '<br>' +
        '<b>Year</b>: ' + terr8['iyear'].astype(str) + '<br>' +
        '<b>Attack</b>: ' + [f'{x:,.0f}' for x in terr8['attacktype1']] + '<br>'
    ))

    fig_bar_line.add_trace(go.Bar(
        x=terr8['iyear'],
        y=terr8['nwound'],
        text=terr8['nwound'],
        texttemplate='%{text:.2s}',
        textposition='auto',
        textfont=dict(color='white'),
        name='Wounded',
        marker=dict(color='#9C0C38'),
        hoverinfo='text',
        hovertext=
        '<b>Region</b>: ' + terr8['region_txt'].astype(str) + '<br>' +
        '<b>Country</b>: ' + terr8['country_txt'].astype(str) + '<br>' +
        '<b>Year</b>: ' + terr8['iyear'].astype(str) + '<br>' +
        '<b>Wounded</b>: ' + [f'{x:,.0f}' for x in terr8['nwound']] + '<br>'
    ))

    fig_bar_line.update_layout(
        barmode='stack',
        plot_bgcolor='#010915',
        paper_bgcolor='#010915',
        title={
            'text': 'Attack and Death: ' + (selected_country) + '  ' + '<br>' + ' - '.join([str(y) for y in selected_years]) + '</br>',
            'y': 0.93,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        titlefont={
            'color': 'white',
            'size': 20},
        hovermode='x',
        xaxis=dict(title='<b>Year</b>',
                   tick0=0,
                   dtick=1,
                   color='white',
                   showline=True,
                   showgrid=True,
                   showticklabels=True,
                   linecolor='white',
                   linewidth=2,
                   ticks='outside',
                   tickfont=dict(
                       family='Arial',
                       size=12,
                       color='white'
                   )
                   ),

        yaxis=dict(title='<b>Attack and Death</b>',
                   color='white',
                   showline=True,
                   showgrid=True,
                   showticklabels=True,
                   linecolor='white',
                   linewidth=2,
                   ticks='outside',
                   tickfont=dict(
                       family='Arial',
                       size=12,
                       color='white'
                   )
                   ),

        legend={
            'orientation': 'h',
            'bgcolor': '#010915',
            'xanchor': 'center', 'x': 0.5, 'y': -0.3},
        font=dict(
            family="sans-serif",
            size=12,
            color='white'),
    )
    st.plotly_chart(fig_bar_line, use_container_width=True)

    # Pie Chart
    st.subheader("Total Casualties")
    fig_pie = go.Figure()

    terr9 = terr2.groupby(['region_txt', 'country_txt', 'iyear'])[['nkill', 'nwound', 'attacktype1']].sum().reset_index()
    death = terr9[(terr9['region_txt'] == selected_region) & (terr9['country_txt'] == selected_country) & (terr9['iyear'] >= selected_years[0]) & (terr9['iyear'] <= selected_years[1])]['nkill'].sum()
    wound = terr9[(terr9['region_txt'] == selected_region) & (terr9['country_txt'] == selected_country) & (terr9['iyear'] >= selected_years[0]) & (terr9['iyear'] <= selected_years[1])]['nwound'].sum()
    attack = terr9[(terr9['region_txt'] == selected_region) & (terr9['country_txt'] == selected_country) & (terr9['iyear'] >= selected_years[0]) & (terr9['iyear'] <= selected_years[1])]['attacktype1'].sum()
    colors = ['#FF00FF', '#9C0C38', 'orange']

    fig_pie.add_trace(go.Pie(
        labels=['Total Death', 'Total Wounded', 'Total Attack'],
        values=[death, wound, attack],
        marker=dict(colors=colors),
        hoverinfo='label+value+percent',
        textinfo='label+value',
        textfont=dict(size=13)
    ))

    fig_pie.update_layout(
        plot_bgcolor='#010915',
        paper_bgcolor='#010915',
        hovermode='closest',
        title={
            'text': 'Total Casualties: ' + (selected_country) + '  ' + '<br>' + ' - '.join([str(y) for y in selected_years]) + '</br>',
            'y': 0.93,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        titlefont={
            'color': 'white',
            'size': 20},
        legend={
            'orientation': 'h',
            'bgcolor': '#010915',
            'xanchor': 'center', 'x': 0.5, 'y': -0.07},
        font=dict(
            family="sans-serif",
            size=12,
            color='white')
    )
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.warning("No data found for the selected filters.")

