import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

if 'estado' not in st.session_state or st.session_state['estado'] != 'Autorizado':
    st.warning("No autorizado. Por favor, inicie sesión.")
    st.stop()

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

def buscar_viaje(codigoPostal, dia_semana, horario, sentido, fechaDeViaje):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            dia_column_ida = f"{dia_semana.lower()}_ida"
            dia_column_vuelta = f"{dia_semana.lower()}_vuelta"
            
            if sentido == 'I':
                dia_column = dia_column_ida
            else:
                dia_column = dia_column_vuelta
            
            query = f"""
            SELECT u.iduser, u.codigo_postal, u.nombre_apellido, u.telefono_celular, u.email, c.plazas
            FROM AustralPool.Usuarios u
            JOIN AustralPool.Conductor c ON u.iduser = c.iduser
            WHERE u.codigo_postal = %s 
              AND c.{dia_column} = %s
              AND %s BETWEEN c.fecha_inicio AND c.fecha_fin
            """
            cur.execute(query, (codigoPostal, horario, fechaDeViaje))
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            return df
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al buscar el viaje: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def reservar_viaje(idConductor, idPasajero, fechaViaje, sentido, dia_semana):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Verificar plazas disponibles
            query_plazas = """
            SELECT plazas FROM AustralPool.Conductor WHERE idUser = %s
            """
            cur.execute(query_plazas, (int(idConductor),))  # Convertir a int
            plazas_disponibles = cur.fetchone()[0]

            # Verificar plazas ocupadas
            query_ocupados = """
            SELECT COUNT(*) FROM AustralPool.Viajes 
            WHERE idConductor = %s AND fechaViaje = %s AND sentido = %s AND dia_semana = %s
            """
            cur.execute(query_ocupados, (int(idConductor), fechaViaje, sentido, diaMayuscula(dia_semana)))
            result = cur.fetchone()
            plazas_ocupadas = result[0] if result else 0

            if plazas_ocupadas < plazas_disponibles:
                # Insertar nueva reserva
                query_insert = """
                INSERT INTO AustralPool.Viajes (idConductor, idPasajero, fechaViaje, sentido, dia_semana)
                VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(query_insert, (int(idConductor), int(idPasajero), fechaViaje, sentido, diaMayuscula(dia_semana)))
                conn.commit()
                return True
            else:
                st.warning(f"No hay plazas disponibles para este viaje. Plazas disponibles: {plazas_disponibles}, Plazas ocupadas: {plazas_ocupadas}")
                return False
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al reservar el viaje: {e}")
        return False
    finally:
        conn.close()

def cargar_viajes_futuros(idUser):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT v.idConductor, v.fechaViaje, v.sentido, v.dia_semana, c.nombre_apellido AS conductor
            FROM AustralPool.Viajes v
            JOIN AustralPool.Usuarios c ON v.idConductor = c.idUser
            WHERE v.idPasajero = %s AND v.fechaViaje >= CURRENT_DATE
            """
            cur.execute(query, (int(idUser),))  # Convertir a int
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            return df
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al cargar los viajes reservados: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def cargar_viajes_pasados(idUser):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT v.idConductor, v.fechaViaje, v.sentido, v.dia_semana, c.nombre_apellido AS conductor
            FROM AustralPool.Viajes v
            JOIN AustralPool.Usuarios c ON v.idConductor = c.idUser
            WHERE v.idPasajero = %s AND v.fechaViaje < CURRENT_DATE
            """
            cur.execute(query, (int(idUser),))  # Convertir a int
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            return df
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al cargar el historial de viajes: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def diaMayuscula(dia):
    if dia == 'miercoles':
        return 'X'
    else:
        return dia[0].upper()

st.set_page_config(page_title='Austral Pool', page_icon='logoCarPool.jpg', layout="centered", initial_sidebar_state="auto", menu_items=None)

st.image('Imagenderecha.jpg', 
         use_column_width=True
         )
st.title('Viajes')
st.write('Acá podés ver los viajes que ya tenés reservados y buscar nuevos viajes')

# Inicializar variables de sesión
if 'idUser' not in st.session_state:
    st.session_state['idUser'] = None

if 'confirmar_reserva' not in st.session_state:
    st.session_state['confirmar_reserva'] = False

if 'selected_index' not in st.session_state:
    st.session_state['selected_index'] = None

if 'viaje_buscado' not in st.session_state:
    st.session_state['viaje_buscado'] = False

idUser = st.text_input('Ingrese su ID de usuario')

if idUser:
    try:
        idUser = int(idUser)
        st.session_state['idUser'] = idUser
    except ValueError:
        st.error("El ID de usuario debe ser un número entero.")

if st.session_state['idUser']:
    st.title('Mis viajes')

    df_mis_viajes = cargar_viajes_futuros(st.session_state['idUser'])
    df_historial = cargar_viajes_pasados(st.session_state['idUser'])

    # Utilizando tabs para mostrar los viajes futuros y pasados
    tabs = st.tabs(["Mis viajes", "Historial"])
    
    with tabs[0]:
        st.write("Mis viajes futuros")
        st.dataframe(df_mis_viajes, hide_index=True)

    with tabs[1]:
        st.write("Historial de viajes")
        st.dataframe(df_historial, hide_index=True)

    st.title('Buscar viajes')

    codigoPostal = st.text_input('Escriba su número postal')
    fechaDeViaje = st.date_input("¿Qué día necesitás transporte para la universidad?", value=None)

    opcionesDireccion = pd.DataFrame({'first column': ['I', 'V']})
    idaOVuelta = st.selectbox('¿Querés ir hacia la universidad (IDA=I) o volver de la universidad (VUELTA=V)?', opcionesDireccion['first column'])

    opcionesHorario = pd.DataFrame({'first column': ['M', 'T', 'N']})
    if idaOVuelta == 'I':
        horario = st.selectbox('¿En qué horario querés ir a la universidad?', opcionesHorario['first column'])
    else:
        horario = st.selectbox('¿En qué horario querés volver de la universidad?', opcionesHorario['first column'])

    dias_semana_es = {
        0: 'lunes',
        1: 'martes',
        2: 'miercoles',
        3: 'jueves',
        4: 'viernes',
        5: 'sábado',
        6: 'domingo'
    }

    if st.button("Buscar viaje"):
        dia_semana = dias_semana_es[fechaDeViaje.weekday()]  # Obtener el nombre del día en español
        df_resultados = buscar_viaje(codigoPostal, dia_semana, horario, idaOVuelta, fechaDeViaje)
        
        if not df_resultados.empty:
            st.session_state['viaje_buscado'] = True
            st.session_state['df_resultados'] = df_resultados
            st.session_state['dia_semana'] = dia_semana
            st.session_state['fechaDeViaje'] = fechaDeViaje
            st.session_state['idaOVuelta'] = idaOVuelta

    if st.session_state['viaje_buscado']:
        df_resultados = st.session_state['df_resultados']
        dia_semana = st.session_state['dia_semana']
        fechaDeViaje = st.session_state['fechaDeViaje']
        idaOVuelta = st.session_state['idaOVuelta']

        st.write("Selecciona el viaje que deseas reservar:")
        selected_index = st.selectbox("Viajes disponibles:", range(len(df_resultados)), format_func=lambda x: f"ID Conductor: {df_resultados.iloc[x]['iduser']}, Nombre: {df_resultados.iloc[x]['nombre_apellido']}, Plazas: {df_resultados.iloc[x]['plazas']}")
        st.session_state['selected_index'] = selected_index
        selected_row = df_resultados.iloc[selected_index]

        st.write(f"Confirme la reserva con el conductor {selected_row['nombre_apellido']}")
        if st.button("Confirmar reserva"):
            exito = reservar_viaje(int(selected_row['iduser']), st.session_state['idUser'], fechaDeViaje, idaOVuelta, dia_semana)
            if exito:
                st.success("Reserva realizada con éxito.")
            else:
                st.error("Error en la reserva.")

# Fondo de la app
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
