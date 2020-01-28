#!/usr/bin/env python
"""
Web interface (Streamlit) for the Power Analysis (Python) tool
Developed by Jazz Mack Smith
Imperial College London
2020
"""
import pa
import streamlit as st
import numpy as np
import pandas as pd

st.title("Power Analysis Web Interface")

@st.cache
def load_data(data_file):
    data = pd.read_csv(data_file, header=None)
    return data

st.subheader("Enter parameter values on the left and click Submit")
instructions_3 = '0:100:500 (default value) means the range of sample sizes from 0 to 500 (not inclusive) with interval of 100 \n'
instructions_4 = '0.05:0.05:0.7 (default value) means the range of effect sizes from 0.05 to 0.7 (not inclusive) with interval of 0.05\n'

csv_data = st.sidebar.file_uploader('Data', type='csv', encoding='auto')
v_range = st.sidebar.text_input('Variable range', '9-12')
sample_range = st.sidebar.text_input('Range of sample sizes', '0:100:500')
effect_range = st.sidebar.text_input('Range of effect sizes', '0.05:0.05:0.7')
num_repeats = st.sidebar.text_input('Number of repeats', '10')
analysis = st.sidebar.text_input('0 = classification; 1 = regression; 2 = both', '4')
num_cpus = st.sidebar.text_input('Number of cpus', '1')

submit = st.button('Submit')

try:
    if submit:
        if csv_data is not None:
            data = load_data(csv_data)
            st.write(data)
            pa.main_ui(data, v_range, sample_range, effect_range, num_repeats, analysis, num_cpus)
        else:
            raise ValueError("No input file supplied")
except Exception as e:
    st.error(e)