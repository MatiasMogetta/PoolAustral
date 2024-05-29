import streamlit as st
import psycopg2

def get_db_connection():
    user = 'postgres.qaqarqxmcujaagjnhysc'
    password = 'AustralCarPool.'
    host = 'aws-0-sa-east-1.pooler.supabase.com'
    port = '5432'
    dbname = 'postgres'
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return conn

def authenticate_user(email, password):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT idUser FROM AustralPool.Usuarios
            WHERE email = %s AND contraseña = %s
            """
            cur.execute(query, (email, password))
            result = cur.fetchone()
            if result:
                return result[0]  # Return the user ID if authentication is successful
            else:
                return None
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al autenticar el usuario: {e}")
        return None
    finally:
        conn.close()

st.set_page_config(page_title='Austral Pool', page_icon='logoCarPool.jpg', layout="centered", initial_sidebar_state="auto", menu_items=None)

if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'
    st.session_state['user_id'] = None  # Almacenar el ID del usuario autenticado

st.write(st.session_state['estado'])

st.title("Iniciar Sesión")

email = st.text_input("Correo electrónico")
password = st.text_input("Contraseña", type="password")

if st.button("Iniciar Sesión"):
    user_id = authenticate_user(email, password)
    if user_id:
        st.success("Inicio de sesión exitoso")
        st.session_state['estado'] = 'Autorizado'
        st.session_state['user_id'] = user_id  # Almacenar el ID del usuario autenticado
    else:
        st.error("Correo electrónico o contraseña incorrectos")

# Mostrar contenido solo si el usuario está autorizado
if st.session_state['estado'] == 'Autorizado':
    st.write("¡Bienvenido! Ahora puedes acceder a las otras páginas.")
    # Aquí puedes agregar enlaces o botones para navegar a otras páginas
    if st.button("Ir a AltaConductor"):
        st.switch_page("pages/3Alta Conductor.py")
    if st.button("Ir a Viajes"):
        st.switch_page("pages/4Viajes.py")
else:
    st.warning("Por favor, inicie sesión para acceder a las otras páginas.")

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