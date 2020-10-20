# For running the project, in the project directory in Terminal,
# run 'streamlit run project.py' 

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# The path may differ in your computer
path = (
    './CSV/Motor_Vehicle_Collisions_-_Crashes.csv'
)

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used"
"to analyze motor vehicle collisions in NYC 🗽💥🚗")

# Since the following function is computational expensive we put:
@st.cache(persist=True) # For not running it continuosly
def load_data(nrows):
    data = pd.read_csv(path, nrows=nrows, parse_dates=[['CRASH DATE', 'CRASH TIME']])
    # In streamlit you cannot have missing values
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    # Let's rename some columns
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash date_crash time':'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

st.header("Wher are the most people injured in NYC?")
# We want the user to input the number of persons injured
# We need the minimum and maximum value / min and max return a numpy
min_injured = int(data['number of persons injured'].min())
max_injured = int(data['number of persons injured'].max())
injured_people = st.slider('Number of persons injured in vehicle collisions', min_injured, max_injured)
st.map(data.query('`number of persons injured` >= @injured_people')[['latitude', 'longitude']].dropna(how='any'))

st.header('How many collisions occur during a given time of day?')
# hour = st.selectbox('Hour to look at', range(0,24), 1) # Message, range, separation
# st.sidebar.slider('Hour to look at', 0, 23) # For a slider sidebar
hour = st.slider('Hour to look at', 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown('Vehicle collisions between %i:00 and %i:00' % (hour, (hour + 1) % 24))

midpoint = (np.average(data['latitude']), np.average(data['longitude']))

# Let's initialize a map using pydeck framework for a 3d map plot
st.write(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state={
        'latitude':midpoint[0],
        'longitude': midpoint[1],
        'zoom': 11,
        'pitch': 50
    },
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0,1000]
        )
    ]
))

st.subheader('Breakdown by minute between %i:00 and %i:00' % (hour, (hour + 1) % 24))
filtered = data[
    (data['date/time'].dt.hour >= hour)&(data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header('Top 5 dangerous streets by affected type os people')
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])
if select == 'Pedestrians':
    st.write(original_data.query('`number of pedestrians injured` >= 1')[['on street name', 'number of pedestrians injured']].sort_values(by=['number of pedestrians injured'], ascending=False).dropna(how='any')[:5])
elif select == 'Cyclists':
    st.write(original_data.query('`number of cyclist injured` >= 1')[['on street name', 'number of cyclist injured']].sort_values(by=['number of cyclist injured'], ascending=False).dropna(how='any')[:5])
else:
    st.write(original_data.query('`number of motorist injured` >= 1')[['on street name', 'number of motorist injured']].sort_values(by=['number of motorist injured'], ascending=False).dropna(how='any')[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)

