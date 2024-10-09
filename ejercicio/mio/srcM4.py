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

    boton_listar = Button(raiz, text="Listar Jornadas", command=listar_partidos_jornada)
    boton_listar.pack(pady=0)

    boton_buscar_jornada = Button(raiz, text="Buscar Jornada", command=buscar_jornada)
    boton_buscar_jornada.pack(pady=0)

    boton_estadisticas = Button(raiz, text="Estadísticas Jornada", command=burcar_estadisticas_jornada)
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
            
            print(f"{numero_jornada} - Link: {link} |{equipo_local} vs {equipo_visitante}| Goles: {resultado_local}-{resultado_visitante}")
            
            conn.execute("""INSERT INTO RESULTADOS (JORNADA, LINK, EQUIPO1, EQUIPO2, RESULTADO1, RESULTADO2) VALUES (?,?,?,?,?,?)""",
                     (numero_jornada, link, equipo_local, equipo_visitante, resultado_local, resultado_visitante))
    
    conn.commit()

    cursor = conn.execute("SELECT COUNT(*) FROM RESULTADOS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()
   
   
def listar_partidos_jornada():
            conn = sqlite3.connect('resultados.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT JORNADA, LINK, EQUIPO1, EQUIPO2, RESULTADO1, RESULTADO2 FROM RESULTADOS")
            conn.close
            formato_partidos(cursor)


def formato_partidos(cursor): 
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    jornada = 0
    for row in cursor:
        if row[0] != jornada:
            jornada = row[0]
            lb.insert(END, "\n\n")
            s = row[0].upper()
            lb.insert(END, s)
            lb.insert(END, "------------------------------------------------------------------------")
        l = str(row[2]) + " " + str(row[4]) + "-" + str(row[5]) + " " + row[3]
        lb.insert(END, l)
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)
    
    
def buscar_jornada():

    def lista(event):
            conn = sqlite3.connect('resultados.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT JORNADA, LINK, EQUIPO1, EQUIPO2, RESULTADO1, RESULTADO2 FROM RESULTADOS WHERE JORNADA = '" + sb.get() + "'")
            conn.close
            formato_partidos(cursor)
    
    conn = sqlite3.connect('resultados.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT JORNADA FROM RESULTADOS")
    
    jornadas = [i[0] for i in cursor]
        
    v = Toplevel()
    lb = Label(v, text="Seleccione la jornada: ")
    lb.pack(side = LEFT)  
    sb = Spinbox(v, values=jornadas)
    sb.bind("<Return>", lista)
    sb.pack()
    
    conn.close()

    
def burcar_estadisticas_jornada():

    def estadisticas(event):
            conn = sqlite3.connect('resultados.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT SUM(RESULTADO1)+SUM(RESULTADO2) FROM RESULTADOS WHERE JORNADA = '" + sb.get() + "'")
            goles = cursor.fetchone()[0]
            cursor = conn.execute("SELECT RESULTADO1,RESULTADO2 FROM RESULTADOS WHERE JORNADA = '" + sb.get() + "'")
            empates = 0
            local = 0
            visitante = 0
            for row in cursor:
                if row[0] == row[1]:
                    empates += 1
                elif row[0] > row[1]:
                    local += 1
                else:
                    visitante += 1
            conn.close
            formato_estadisticas(goles,local,visitante,empates)
    
    conn = sqlite3.connect('resultados.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT DISTINCT JORNADA FROM RESULTADOS")
    
    jornadas = [i[0] for i in cursor]
        
    v = Toplevel()
    lb = Label(v, text="Seleccione la jornada: ")
    lb.pack(side = LEFT)  
    sb = Spinbox(v, values=jornadas)
    sb.bind("<Return>", estadisticas)
    sb.pack()
    
    conn.close()
    
def formato_estadisticas(goles,local,visitante,empates): 

    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    lb.insert(END, "TOTAL GOLES JORNADA : " + str(goles))
    lb.insert(END, "\n\n")
    lb.insert(END, "EMPATES : " + str(empates))
    lb.insert(END, "VICTORIAS LOCALES : " + str(local))
    lb.insert(END, "VICTORIAS VISITANTES : " + str(visitante))
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


if __name__ == '__main__':
    ventana_principal()
    
