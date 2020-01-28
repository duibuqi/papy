import streamlit as st
import pandas as pd
import numpy as np  

@st.cache
def load_data():
    useful_cols = [2,4,6,12]
    df = pd.read_csv("/Users/jms3/Projects/mouse-ox/new_data/KP032B.csv", usecols=useful_cols)
    df.columns = ['subject', 'err','heart_rate','clock']
    
    actual_start = pd.to_datetime(df.iloc[0]['clock'])
    normal_start = actual_start.replace(hour=10, minute=0, second=0)
    time_lag = actual_start - normal_start
    offset = int(time_lag.total_seconds())
    df['second'] = list(range(offset, offset + len(df)))
    df['clock'] = pd.to_datetime(df['clock'], dayfirst=True)
    
    return df
    

st.title("Mice")
df = load_data()
hour = st.selectbox('select hour', range(0,24), 1)
mouse = st.slider('select mouse', 1, 10, 1, 1)
#df = df[(df['clock'].dt.day==day) & (df['clock'].dt.hour==hour)]
df = df[(df['clock'].dt.hour==hour) & (df['subject']==mouse)]
st.subheader('Mice')

st.write(df)
st.subheader('Data points for mouse ' + str(mouse) + ' in hour ' + str(hour))
st.bar_chart(np.histogram(df['clock'].dt.minute, bins=60, range=(0,60))[0])
    

