import streamlit as st
import psycopg2
import pandas as pd
import time

if 'estado' not in st.session_state or st.session_state['estado'] != 'Autorizado':
    st.warning("No autorizado. Por favor, inicie sesión.")
    st.stop()

def get_db_connection():
    user='postgres.qaqarqxmcujaagjnhysc'
    password='AustralCarPool.' 
    host='aws-0-sa-east-1.pooler.supabase.com'
    port='5432' 
    dbname='postgres'
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return conn

#Función para insertar al conductor en la base de datos
def insert_conductor(dni, plazas, fechaInicio, fechaFin, horarioIdaLunes, horarioVueltaLunes, horarioIdaMartes, horarioVueltaMartes, horarioIdaMiércoles, horarioVueltaMiércoles, horarioIdaJueves, horarioVueltaJueves, horarioIdaViernes, horarioVueltaViernes):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "INSERT INTO Australpool.Conductor (iduser, plazas, fecha_inicio, fecha_fin, lunes_ida, lunes_vuelta, martes_ida, martes_vuelta, miercoles_ida, miercoles_vuelta, jueves_ida, jueves_vuelta, viernes_ida, viernes_vuelta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(query, (dni, plazas, fechaInicio, fechaFin, horarioIdaLunes, horarioVueltaLunes, horarioIdaMartes, horarioVueltaMartes, horarioIdaMiércoles, horarioVueltaMiércoles, horarioIdaJueves, horarioVueltaJueves, horarioIdaViernes, horarioVueltaViernes))
            conn.commit()
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al guardar el usuario: {e}")
    finally:
        conn.close()

st.set_page_config(page_title='Austral Pool', page_icon='logoCarPool.jpg', layout="centered", initial_sidebar_state="auto", menu_items=None)

#Le pido los datos necesarios al usuario para que sea un conductor
st.title('Alta Conductor')
st.write('Acá podrás darte de alta como conductor, donde podrás ofrecerle ayuda a compañeros que necesiten ir los mismos días y horarios que vos.')
dni = st.text_input('DNI')
plazas = st.text_input('¿Cuántas personas estás dispuestas a llevar en tu auto? Sin contarte a vos.')
fechaInicio = st.date_input("Fecha donde planeás empezar a ofrecerte como conductor", value=None)
fechaFin = st.date_input("Fecha donde planeás dejar de ofrecerte como conductor", value=None)

#Se podría hacer con un for usando una lista con los días. El problema serían los nombres de las variables. SOLUCIONAR
st.write('Seleccione los días en los que va a la facultad y los horarios: Mañana (M), Tarde (T), Noche (N)')
df = pd.DataFrame({'first column': ['M', 'T', 'N']})
if st.checkbox('Lunes'):
    horarioIdaLunes = st.selectbox('Horario ida lunes', df['first column'])
    horarioVueltaLunes = st.selectbox('Horario vuelta lunes', df['first column'])
else:
    horarioIdaLunes = None
    horarioVueltaLunes = None

if st.checkbox('Martes'):
    horarioIdaMartes = st.selectbox('Horario ida martes', df['first column'])
    horarioVueltaMartes = st.selectbox('Horario vuelta martes', df['first column'])
else:
    horarioIdaMartes = None
    horarioVueltaMartes = None

if st.checkbox('Miércoles'):
    horarioIdaMiércoles = st.selectbox('Horario ida Miércoles', df['first column'])
    horarioVueltaMiércoles = st.selectbox('Horario vuelta Miércoles', df['first column'])
else:
    horarioIdaMiércoles = None
    horarioVueltaMiércoles = None

if st.checkbox('Jueves'):
    horarioIdaJueves = st.selectbox('Horario ida Jueves', df['first column'])
    horarioVueltaJueves = st.selectbox('Horario vuelta Jueves', df['first column'])
else:
    horarioIdaJueves = None
    horarioVueltaJueves = None

if st.checkbox('Viernes'):
    horarioIdaViernes = st.selectbox('Horario ida Viernes', df['first column'])
    horarioVueltaViernes = st.selectbox('Horario vuelta Viernes', df['first column'])
else:
    horarioIdaViernes = None
    horarioVueltaViernes = None

if st.button("Dar de alta"):
    insert_conductor(dni, plazas, fechaInicio, fechaFin, horarioIdaLunes, horarioVueltaLunes, horarioIdaMartes, horarioVueltaMartes, horarioIdaMiércoles, horarioVueltaMiércoles, horarioIdaJueves, horarioVueltaJueves, horarioIdaViernes, horarioVueltaViernes)
    progress_text = "Operation in progress. Please wait."
    my_bar = st.progress(0, text=progress_text)

    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()

#fondo de la app
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://i.postimg.cc/4xgNnkfX/Untitled-design.png");
background-size: cover;
background-position: center center;
background-repeat: no-repeat;
background-attachment: local;
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
