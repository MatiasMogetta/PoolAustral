import streamlit as st
import pandas as pd
import time
import psycopg2
from datetime import datetime

#Función para conectarme a la base de datos
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

#Función para chequear si el mail ingresa existe o no en la BBDD
def email_exists(email):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM Australpool.Usuarios WHERE email = %s"
            cur.execute(query, (email,))
            result = cur.fetchone()
            return result is not None
    finally:
        conn.close()

#Función para insertar al usuario en la base de datos
def insert_user(iduser, nombreYApellido, codigoPostal, contactoTelefono, email, genero, fechaDeNacimiento, contraseña):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "INSERT INTO Australpool.Usuarios (iduser, nombre_apellido, codigo_postal, telefono_celular, email, genero, fecha_nacimiento, contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(query, (iduser, nombreYApellido, codigoPostal, contactoTelefono, email, genero, fechaDeNacimiento, contraseña))
            conn.commit()
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al guardar el usuario: {e}")
    finally:
        conn.close()

#Sección donde se piden los datos de registro de usuario
st.set_page_config(page_title='Austral Pool', page_icon='logoCarPool.jpg', layout="centered", initial_sidebar_state="auto", menu_items=None)

st.title('✅ Registrar Usuario')

email = st.text_input("Email")
password = st.text_input("Contraseña") 
confirm_password = st.text_input("Confirmar contraseña")
if confirm_password == password:
    st.write("Contraseña verificada")
st.title('Llenar datos')
st.write('Para poder proveerte de la mejor experiencia necesitamos que llenes los siguientes datos por única vez. Es obligatorio para poder registrarte como usuario.')
dni = st.text_input("DNI")
nombreYApellido = st.text_input("Nombre y Apellido")
codigoPostal = st.text_input("Código postal")
contactoTelefono = st.text_input("Número de celular")
df = pd.DataFrame({'first column': ['F', 'M']})
genero = st.selectbox(
    'Género',
     df['first column'])
fechaDeNacimiento =  st.date_input("Fecha de Nacimiento", max_value=datetime.today())

#Botón de registrar usuario, acá se chequea que estén todos los datos correspondientes
#Si están todos los datos, se inserta al usuario en la BBDD, sino se piden los datos
if st.button("Registrar Usuario"):
    if not dni or not nombreYApellido or not codigoPostal or not contactoTelefono or not email or not genero or not fechaDeNacimiento:
        st.error("Por favor, completa todos los campos.")
    elif fechaDeNacimiento >= datetime.today().date():
        st.error("La fecha de nacimiento debe ser anterior a la fecha actual.")
    elif email_exists(email):
        st.error("El email ya está registrado. Por favor, utiliza otro email.")
    else:
        insert_user(dni, nombreYApellido, codigoPostal, contactoTelefono, email, genero, fechaDeNacimiento, password)
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
