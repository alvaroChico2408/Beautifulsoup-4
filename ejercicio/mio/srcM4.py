'''
Created on 8 oct 2024

@author: alvaro
'''

# encoding:utf-8

from tkinter import Tk, Button
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime
import re
# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def ventana_principal():
    # Crear la ventana principal
    raiz = Tk()
    raiz.title("Menú Principal")
    
    # Crear los botones
    boton_almacenar = Button(raiz, text="Almacenar Resultados", command=cargar)
    boton_almacenar.pack(pady=0)

    boton_listar = Button(raiz, text="Listar Jornadas", command=raiz.quit)
    boton_listar.pack(pady=0)

    boton_buscar_jornada = Button(raiz, text="Buscar Jornada", command=raiz.quit)
    boton_buscar_jornada.pack(pady=0)

    boton_estadisticas = Button(raiz, text="Estadísticas Jornada", command=raiz.quit)
    boton_estadisticas.pack(pady=0)

    boton_buscar_goles = Button(raiz, text="Buscar Goles", command=raiz.quit)
    boton_buscar_goles.pack(pady=0)

    # Configurar el tamaño de la ventana para que se ajuste al contenido
    raiz.geometry("200x250")
    
    raiz.mainloop()
    

def cargar():
    respuesta = messagebox.askyesno(title="Confirmar", message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_bd()
        

def almacenar_bd():

    conn = sqlite3.connect('resultados.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS RESULTADOS")
    conn.execute('''CREATE TABLE RESULTADOS
       (JORNADA    TEXT,
       LINK            TEXT NOT NULL,
        EQUIPO1    TEXT,        
        EQUIPO2    TEXT,
        RESULTADO1      INTEGER,
        RESULTADO2    INTEGER);''')
    
    f = urllib.request.urlopen("http://resultados.as.com/resultados/futbol/primera/2023_2024/calendario/")
    s = BeautifulSoup(f, "lxml")
    lista_jornadas = s.find_all("div", class_="col-md-6 col-sm-6 col-xs-12")
    
    for jornada in lista_jornadas:
        numero_jornada = jornada.find("a", title=re.compile(r"Jornada \d{1,2}")).string.strip()
        partidos = jornada.find_all("a", class_="resultado")
        for partido in partidos:
            link = str(partido).split('"')[3]
            f1 = urllib.request.urlopen(link)
            s1 = BeautifulSoup(f1, "lxml")
            equipos = s1.find_all("span", class_="name-large")
            equipo_local = equipos[0].string
            equipo_visitante = equipos[1].string
            resultados = s1.find_all("span", class_="scr-hdr__score")
            resultado_local = resultados[0].string
            resultado_visitante = resultados[1].string
            
            print(f"{numero_jornada} - Link: {link} | {equipo_local} vs {equipo_visitante} | Goles: {resultado_local}-{resultado_visitante}")
            
            conn.execute("""INSERT INTO RESULTADOS (JORNADA, LINK, EQUIPO1, EQUIPO2, RESULTADO1, RESULTADO2) VALUES (?,?,?,?,?,?)""",
                     (numero_jornada, link, equipo_local, equipo_visitante, resultado_local, resultado_visitante))
    
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM RESULTADOS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()


if __name__ == '__main__':
    ventana_principal()
    
