import streamlit as st
import numpy as np
import fireo
# Write a title and a bit of a blurb
st.title('COVIBOT :pill:')

st.write('COVIBOT está buscando ayuda relacionada a COVID en twitter')
# Make some choices for a user to select
keys = ['Normal','Uniform']
dist_key = st.selectbox('Which Distribution do you want to plot?',keys)
# Logic of our program
if dist_key == 'Normal':
    nums = np.random.randn(1000)
elif dist_key == 'Uniform':
    nums = np.array([np.random.randint(100) for i in range(1000)])
# Display User
st.line_chart(nums)