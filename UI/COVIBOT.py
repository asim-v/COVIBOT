import streamlit as st
import numpy as np
import pandas as pd
import fireo
from fireo.models import Model,TextField,NumberField

fireo.connection(from_file="keyfile.json")
class Post(Model):
    content = TextField()
    urgency = NumberField()
    category = TextField()

data = [[x.urgency,x.content,x.category] for x in Post.collection.fetch()]
df = pd.DataFrame(data,columns=(['Urgencia','Contenido','Categoria']))


st.title(':pill: COVIBOT ')
st.write('COVIBOT está buscando ayuda relacionada a COVID en twitter')
st.write('{} tweets hasta ahora'.format(len(data)))

cols = ["Urgencia", "Contenido", "Categoria"]
st_ms = st.multiselect("Columns", df.columns.tolist(), default=cols)
	
def ColorPill(val):
	if val == 'Salud':
		return 'background-color:red'
	if val == 'Información Oficial':
		return 'background-color:green'
	if val == 'Ocio':
		return 'background-color:yellow'
	if val == 'Laborales':
		return 'background-color:blue'
	if val == 'Educación':
		return 'background-color:orange'

st.dataframe(df.style.applymap(ColorPill))

# if dist_key == 'Normal':
#     nums = np.random.randn(1000)
# elif dist_key == 'Uniform':
#     nums = np.array([np.random.randint(100) for i in range(1000)])