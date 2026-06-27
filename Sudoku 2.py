#Constantes e imports
import tkinter as tk
from tkinter import messagebox

import random

import json
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from collections import deque

#imports del programa 3
import pickle
import hashlib
from tkinter import simpledialog


ARCHIVO_CONFIG = "sudoku2026configuracion.json" 
ARCHIVO_BITACORA = "sudoku2026_bitacora_jugadas.json" 
ARCHIVO_JUEGO = "sudoku2026juegoactual.json" 
ARCHIVO_PARTIDAS = "sudoku2026partidas.json" #Ya no se usa en el programa 3

NIVELES=["facil", "intermedio", "dificil", "multinivel"]
NUMEROS=[1,2,3,4,5,6,7,8,9]
LETRAS=["A","B","C","D","E","F","G","H","I"]

CONFIG_DEFAULT={"nivel":"facil", "reloj":"cronometro", "timer":{"horas": 0, "minutos": 0, "segundos": 0},
                "top_x": 1, "elementos": "numeros", "elementos_personalizados": ""}

#Programa 3
#Clases del Programa 3
class Partida:
    def __init__(self,jugador, nivel, tiempo, fecha_hora):
        self.jugador = jugador
        self.nivel = nivel
        self.tiempo = tiempo
        self.fecha_hora = fecha_hora
        
    def get_partida(self):
        horas = self.tiempo // 3600
        minutos = (self.tiempo % 3600) // 60
        segs = self.tiempo % 60
        
        return f"{self.jugador} | {self.nivel} | {horas}:{minutos:02d}:{segs:02d} | {self.fecha_hora}"
    
class NodoABB:
    def __init__(self, partida):
        self.partida = partida 
        self.izquierdo = None 
        self.derecho = None

class ABB:
    def __init__(self):
        self.raiz = None

    def insertar_nodo(self, partida):
        nuevo_nodo = NodoABB(partida)

        if self.raiz is None:
            self.raiz = nuevo_nodo
        else:
            self.insertar_recursivo(self.raiz, nuevo_nodo)
            
    def insertar_recursivo(self, nodo_actual, nuevo_nodo):
        if nuevo_nodo.partida.tiempo<nodo_actual.partida.tiempo:
            if nodo_actual.izquierdo == None:
                nodo_actual.izquierdo = nuevo_nodo
                    
            else:
                self.insertar_recursivo(nodo_actual.izquierdo, nuevo_nodo)
                    
        else:
            if nodo_actual.derecho == None:
                nodo_actual.derecho = nuevo_nodo
                    
            else:
                self.insertar_recursivo(nodo_actual.derecho, nuevo_nodo)

    def recorrer_arbol(self):
        resultado = []
        self.recorrer_recursivo(self.raiz, resultado)
        return resultado
    
    def recorrer_recursivo(self, nodo_actual, resultado):
        if nodo_actual is not None:
            self.recorrer_recursivo(nodo_actual.izquierdo, resultado)
            resultado.append(nodo_actual.partida.get_partida())
            self.recorrer_recursivo(nodo_actual.derecho, resultado)


#Constantes del Programa 3
abb_facil = ABB()
abb_intermedio = ABB()
abb_dificil = ABB()

ARCHIVO_BITACORA_PKL = "sudoku2026_bitacora_jugadas.pkl"
ARCHIVO_USUARIOS = "usuarios.json"


#Seccion de funciones
#Funciones principales
def salir():
    ventana.destroy()
    
def jugar(): #Función base y pilar de toda la partida
    ventana_jugar = tk.Toplevel(ventana,
                                bg="LightSkyBlue1")
    ventana_jugar.title("Sudoku - Jugar")
    ventana_jugar.geometry("800x600")

    partidas = cargar_partida()
    config = cargar_configuracion()
    nivel = config["nivel"]

    frame_derecho = tk.Frame(ventana_jugar)
    frame_derecho.grid(row=0, column=1, padx=20, pady=20, sticky="n")

    name_jugador = tk.Label(frame_derecho, text="JUGADOR:")
    name_jugador.grid(row=0, column=0, pady=5)

    entry_jugador = tk.Entry(frame_derecho, width=30)
    entry_jugador.grid(row=1, column=0, pady=5)

    segundos = tk.IntVar()
    segundos.set(0)
    cronometro_activo = tk.BooleanVar()
    cronometro_activo.set(False)

    #panel para seleccionar numeros
    frame_tablero = tk.Frame(ventana_jugar)
    frame_tablero.grid(row=0, column=0, padx=20, pady=20)

    tit_panel = tk.Label(frame_derecho, text="Selecciona un número:")
    tit_panel.grid(row=2, column=0, pady=10)

    frame_numeros = tk.Frame(frame_derecho)
    frame_numeros.grid(row=3, column=0)

    numero_seleccionado = tk.StringVar()
    numero_seleccionado.set("")

    pila_realizadas = deque()
    pila_eliminadas = deque()

    tablero = [[0]*9 for _ in range(9)]

    partida_actual = [{}]

    botones_tablero = [[None]*9 for _ in range(9)]
    
    #El juego no está iniciado
    juego_iniciado = tk.BooleanVar()
    juego_iniciado.set(False)

    #Saber si juega con letras o números, la config base es con números
    if config["elementos"] == "numeros":
        elemento_panel = NUMEROS
    elif config["elementos"] == "letras":
        elemento_panel = LETRAS
    elif config["elementos"] == "personalizado":
        print("config completo:", config)
        elemento_panel = list(config["elementos_personalizados"])
        
    #Creación del panel de juego
    for indx, elem_pan_selec in enumerate(elemento_panel): #Modificada en el Programa 3
        btn_num = tk.Button(frame_numeros, text=str(elem_pan_selec), width=4, height=2)
        btn_num.configure(command=lambda n=elem_pan_selec, b=btn_num: seleccionar_numero(n, b, frame_numeros, numero_seleccionado))
        btn_num.grid(row=indx//3, column=indx%3, padx=5, pady=5)

    for i in range(9):
        for j in range(9):
            posicion = f"{i},{j}"
            valor = partidas.get(posicion, 0)
            btn = tk.Button(frame_tablero, text="", width=4, height=2, bg="gray90")
            btn.grid(row=i, column=j)

    #Caso de multinivel del Programa 3
    caso_multinivel = tk.StringVar()
    caso_multinivel.set("facil")

    #Funcionalidad propia del Programa 3
    contador_jugadas = tk.IntVar()
    contador_jugadas.set(0)
    texto_contador = tk.StringVar()
    texto_contador.set("Jugadas: 0")

    #Sección de botones 
    btn_iniciar = tk.Button(frame_derecho, text="INICIAR JUEGO", bg="red", fg="white", font=("Arial", 12, "bold"),
                            command=lambda: iniciar_juego(nivel, frame_tablero, entry_jugador, juego_iniciado, numero_seleccionado,
                                                          pila_realizadas, pila_eliminadas, tablero, partida_actual, botones_tablero,
                                                          cronometro_activo, cronometro, segundos, elemento_panel, caso_multinivel,
                                                          contador_jugadas , texto_contador))
    btn_iniciar.grid(row=5, column=0, pady=10)


    btn_deshacer = tk.Button(frame_derecho, text="DESHACER JUGADA", bg="DodgerBlue3", fg="white", font=("Arial", 12, "bold"),
                            command=lambda: deshacer_jugada(pila_realizadas, pila_eliminadas, tablero, frame_tablero, juego_iniciado, botones_tablero,
                                                            contador_jugadas, texto_contador ))
    btn_deshacer.grid(row=6, column=0, pady=10)

    
    btn_rehacer = tk.Button(frame_derecho, text="REHACER JUGADA", bg="lime green", fg="white", font=("Arial", 12, "bold"),
                            command=lambda: rehacer_jugada(pila_realizadas, pila_eliminadas, tablero, frame_tablero, juego_iniciado, botones_tablero,
                                                           contador_jugadas, texto_contador ))
    btn_rehacer.grid(row=7, column=0, pady=10)


    btn_borrar = tk.Button(frame_derecho, text="BORRAR JUEGO", bg="dark orchid", fg="white", font=("Arial", 12, "bold"),
                            command=lambda: borrar_juego(pila_realizadas, pila_eliminadas, tablero, frame_tablero,
                                                         juego_iniciado, partida_actual, botones_tablero))
    btn_borrar.grid(row=8, column=0, pady=10)


    btn_terminar = tk.Button(frame_derecho, text="TERMINAR JUEGO", bg="DarkOrange2", fg="white", font=("Arial", 12, "bold"),
                            command=lambda: terminar_juego(juego_iniciado, ventana_jugar, cronometro_activo))
    btn_terminar.grid(row=5, column=2, pady=10)


    btn_guardar = tk.Button(frame_derecho, text="GUARDAR JUEGO", bg="orchid4", fg="white", font=("Arial", 12, "bold"),
                            command=lambda: guardar_partida_actual(tablero, partida_actual, nivel, entry_jugador, juego_iniciado))
    btn_guardar.grid(row=6, column=2, pady=10)


    btn_cargar = tk.Button(frame_derecho, text="CARGAR JUEGO", bg="MediumPurple3", fg="white", font=("Arial", 12, "bold"),
                           command=lambda: cargar_partida_actual(juego_iniciado, entry_jugador, tablero, botones_tablero,
                                                                 partida_actual, nivel, frame_tablero))
    btn_cargar.grid(row=7, column=2, pady=10)


    btn_topx = tk.Button(frame_derecho, text="TOP X", bg="gold", fg="black", font=("Arial", 12, "bold"),
                         command=lambda: generar_topx())
    btn_topx.grid(row=8, column=2, pady=10)

    lbl_cronometro = tk.Label(frame_derecho, text="00:00:00", font=("Arial", 14, "bold"))
    lbl_cronometro.grid(row=4, column=0, pady=5)

    lbl_contador = tk.Label(frame_derecho, textvariable=texto_contador, font=("Arial", 12))
    lbl_contador.grid(row=10, column=0, pady=5)

    def cronometro():
        if cronometro_activo.get():
            seg = segundos.get() + 1
            segundos.set(seg)
            horas = seg // 3600
            minutos = (seg % 3600) // 60
            segs = seg % 60
            lbl_cronometro.configure(text=f"{horas:02d}:{minutos:02d}:{segs:02d}")
            ventana_jugar.after(1000, cronometro)

def configurar(): #Modificada en el Programa 3
    ventana_config = tk.Toplevel(ventana)
    ventana_config.title("Configurar")
    ventana_config.geometry("800x600")
    ventana_config.configure(bg="gray30")

    config = cargar_configuracion()

    #Configuración de dificultad
    nivel_var = tk.StringVar()
    nivel_var.set(config["nivel"])

    lbl_nivel = tk.Label(ventana_config, text="Nivel:")
    lbl_nivel.pack(pady=5)
    lbl_nivel.configure(bg="gray30", fg="white")

    for nivel in NIVELES:
        rb = tk.Radiobutton(ventana_config, text=nivel, variable=nivel_var, value=nivel)
        rb.pack()
        rb.configure(bg="ivory4", fg="white", selectcolor="green4")

    #Configuracion de cronómetro
    reloj_var = tk.StringVar()
    reloj_var.set(config["reloj"])

    lbl_reloj = tk.Label(ventana_config, text="Reloj:")
    lbl_reloj.pack(pady=5)
    lbl_reloj.configure(bg="gray30", fg="white")

    for opcion in ["cronometro", "timer", "no usar"]:
        rb = tk.Radiobutton(ventana_config, text=opcion, variable=reloj_var, value=opcion)
        rb.pack()
        rb.configure(bg="ivory4", fg="white", selectcolor="green4")

    #Configuracion de TopX
    lbl_topx = tk.Label(ventana_config, text="Cantidad de jugadas TOP X (0-10):")
    lbl_topx.pack(pady=5)
    lbl_topx.configure(bg="ivory4", fg="white")

    entry_topx = tk.Entry(ventana_config, width=5)
    entry_topx.insert(0, str(config["top_x"]))
    entry_topx.pack(pady=5)

    #Configuracion de Elementos, o sea elegir entre números o letras o personalizado
    elementos_var = tk.StringVar()
    elementos_var.set(config["elementos"])

    lbl_elementos = tk.Label(ventana_config, text="Elementos:")
    lbl_elementos.pack(pady=5)
    lbl_elementos.configure(bg="gray30", fg="white")
    
    for opcion in ["numeros", "letras", "personalizado"]:
        rb = tk.Radiobutton(ventana_config, text=opcion, variable=elementos_var, value=opcion)
        rb.pack()
        rb.configure(bg="ivory4", fg="white", selectcolor="green4")

    lbl_personalizado = tk.Label(ventana_config, text="Si elige personalizado, escriba 9 símbolos diferentes:")
    lbl_personalizado.pack(pady=5)

    entry_personalizado = tk.Entry(ventana_config, width=15)
    entry_personalizado.pack(pady=5)

    #Función creada dentro para no tener que mandarle los parametros
    def guardar_config():
        try:
            topx = int(entry_topx.get())
            if topx < 0 or topx > 10:
                messagebox.showwarning("Error", "El Top X debe estar entre 0 y 10")
                return
        except ValueError:
            messagebox.showwarning("Error", "El Top X debe ser un número entero")
            return

        if elementos_var.get() == "personalizado":
            texto_personalizado = entry_personalizado.get()
            if not validar_elementos_personalizados(texto_personalizado):
                messagebox.showwarning("Error", "Digite 9 elementos diferentes")
                return
            
        nueva_config = {
            "nivel": nivel_var.get(),
            "reloj": reloj_var.get(),
            "timer": config["timer"],
            "top_x": topx,
            "elementos": elementos_var.get(),
            "elementos_personalizados": entry_personalizado.get() if elementos_var.get() == "personalizado" else ""
            }
   
        guardar_configuracion(nueva_config)
        messagebox.showinfo("Guardado", "¡Configuración guardada!")
        ventana_config.destroy()
    
    btn_guardar = tk.Button(ventana_config, text="GUARDAR", bg="gray60", fg="gainsboro", font=("Arial", 12, "bold"),
                            command=guardar_config)
    btn_guardar.pack(pady=20)

def ayuda():
    os.startfile("manual_de_usuario_sudoku.PDF")

def acerca_de():
    ventana_acerca = tk.Toplevel(ventana)
    ventana_acerca.title("Acerca de")
    ventana_acerca.geometry("800x600")
    ventana_acerca.configure(bg="SpringGreen3")
    
    nombre = tk.Label(ventana_acerca, text="ACERCA DE", 
                  font=("Arial", 36, "bold"),
                  bg="SpringGreen3",
                  fg="white")
    nombre.pack(pady=20)
    
    app_name = tk.Label(ventana_acerca, text="Sudoking",
                        font=("Arial", 20, "bold"),
                        bg="SpringGreen3",
                        fg="white")
    app_name.pack(pady=20)

    version = tk.Label(ventana_acerca, text="Versión 1.0",
                     font=("Arial", 16, "bold"),
                     bg="SpringGreen3",
                     fg="white")
    version.pack(pady=20)
    
    fecha = tk.Label(ventana_acerca, text="Estrenado el 10/6/2026",
                     font=("Arial", 16, "bold"),
                     bg="SpringGreen3",
                     fg="white")
    fecha.pack(pady=20)

    creador = tk.Label(ventana_acerca, text="Creado por Alejandro Román Salazar",
                    font=("Arial", 16, "bold"),
                    bg="SpringGreen3",
                    fg="white")
    creador.pack(pady=20)
    


#Funciones que ayudan a las principales de antes
def iniciar_juego(nivel, frame_tablero, entry_jugador, juego_iniciado, numero_seleccionado,
                  pila_realizadas, pila_eliminadas, tablero, partida_actual, botones_tablero, cronometro_activo,
                  cronometro, segundos, elementos, caso_multinivel, contador_jugadas , texto_contador): #Modificada en Programa 3
    
    nombre = entry_jugador.get()
    
    if nombre == "":
        messagebox.showwarning("Error", "Debe ingresar un nombre de jugador")
        return

    #Caso de Multinivel
    if nivel == "multinivel":
        nivel_real = caso_multinivel.get()
    else:
        nivel_real = nivel
    
    tablero_generado = generar_tablero(elementos)
    quitar_casillas(tablero_generado, nivel_real)

    for i in range(9):
        for j in range(9):
            tablero[i][j] = tablero_generado[i][j]

    partida_actual[0] = {}
    for i in range(9):
        for j in range(9):
            if tablero[i][j] != 0:
                partida_actual[0][f"{i},{j}"] = tablero[i][j]
    
    for btn_viejos in frame_tablero.winfo_children():
        btn_viejos.destroy()

    for i in range(9):
        for j in range(9):
            posicion = f"{i},{j}"
            valor = partida_actual[0].get(posicion, 0)
            btn = tk.Button(frame_tablero, text="" if valor == 0 else str(valor),
                            width=4, height=2,
                            bg="gray70" if valor != 0 else "gray90")
            botones_tablero[i][j] = btn
            btn.configure(command=lambda f=i, c=j, b=btn: colocar_numero(f, c, b, numero_seleccionado, juego_iniciado, partida_actual, tablero,
                                                                         pila_realizadas, pila_eliminadas, botones_tablero, nombre, nivel,
                                                                         segundos, caso_multinivel, cronometro_activo, frame_tablero,
                                                                         contador_jugadas , texto_contador))
            btn.grid(row=i, column=j, padx=1, pady=1)

        
    #El juego ha iniciado
    juego_iniciado.set(True)

    #Confirmar si el usuario quiere usar el cronometro o no
    config = cargar_configuracion()
    if config["reloj"] != "no usar":
        cronometro_activo.set(True)
        cronometro()

#función para dejar el número seleccionado en verde
def seleccionar_numero(numero, btn_presionado, frame_numeros, num_selec):
    for btn in frame_numeros.winfo_children():
        btn.configure(bg="gray90")

    btn_presionado.configure(bg="lawn green")
    num_selec.set(numero)

#Como hace el programa para añadir un número a la tabla, junto a sus validaciones (funciones hechas un poco más abajo)
def colocar_numero(fila, columna, btn, numero_seleccionado, juego_iniciado, partida_actual, tablero, 
                   pila_realizadas, pila_eliminadas, botones_tablero, nombre, nivel, segundos, caso_multinivel, cronometro_activo,
                   frame_tablero, contador_jugadas, texto_contador): #Modificada en el Programa 3

    if nivel == "multinivel":
        nivel_real = caso_multinivel.get()
    else:
        nivel_real = nivel
    
    posicion = f"{fila},{columna}"
    if juego_iniciado.get() == False:
        messagebox.showwarning("Error", "Inicie el juego primero")
        return

    elif posicion in partida_actual[0]:
        messagebox.showwarning("Error", "JUGADA NO ES VÁLIDA PORQUE ESTE ES UN ELEMENTO FIJO")
        return

    elif numero_seleccionado.get() == "":
        messagebox.showwarning("Error", "Seleccione un número antes de jugar")
        return

    else:
        elemento = numero_seleccionado.get()
        if elemento.isdigit():
            elemento = int(elemento)
            
        if not validar_fila(tablero, fila, elemento):
            messagebox.showwarning("Error", "JUGADA NO ES VÁLIDA PORQUE EL ELEMENTO YA ESTÁ EN LA FILA")
            return
        elif not validar_columna(tablero, columna, elemento):
            messagebox.showwarning("Error", "JUGADA NO ES VÁLIDA PORQUE EL ELEMENTO YA ESTÁ EN LA COLUMNA")
            return
        elif not validar_subcuadricula(fila, columna, tablero, elemento):
            messagebox.showwarning("Error", "JUGADA NO ES VÁLIDA PORQUE EL ELEMENTO YA ESTÁ EN LA CUADRÍCULA")
            return
        else:
            tablero[fila][columna] = elemento
            btn.configure(text=str(elemento))
            btn.configure(text=str(elemento), bg="white")
            pila_realizadas.append((fila, columna, elemento))
            #Funcionalidad propia
            contador_jugadas.set(contador_jugadas.get() + 1)
            texto_contador.set(f"Jugadas: {contador_jugadas.get()}")

            if all(tablero[i][j] != 0 for i in range(9) for j in range(9)):
                messagebox.showinfo("¡Felicidades!", "¡EXCELENTE! JUEGO COMPLETADO")
                guardar_en_bitacora(nombre, nivel_real, segundos.get())
                cronometro_activo.set(False)
                if nivel == "multinivel":
                    nuevo_nivel = avanzar_nivel(caso_multinivel)
                    messagebox.showinfo("Multinivel", f"¡Avanzaste al nivel {nuevo_nivel.upper()}!")
                    juego_iniciado.set(False)
                    for btn_viejos in frame_tablero.winfo_children():
                        btn_viejos.destroy()
                    for i in range(9):
                        for j in range(9):
                            btn_nuevo = tk.Button(frame_tablero, text="", width=4, height=2, bg="gray90")
                            btn_nuevo.grid(row=i, column=j, padx=1, pady=1)
                            botones_tablero[i][j] = btn_nuevo
                

#Funciones de ayuda
def validar_fila(tablero, fila, elemento):
    if elemento in tablero[fila]:
        return False
    else:
        return True

def validar_columna(tablero, columna, elemento):
    for i in tablero:
        if i[columna]==elemento:
            return False
    return True

def validar_subcuadricula(fila, columna, tablero, elemento):
    inicio_fila = (fila // 3) * 3
    inicio_col = (columna // 3) * 3
    for i in range(inicio_fila, inicio_fila + 3):
        for j in range(inicio_col, inicio_col + 3):
            if tablero[i][j]==elemento:
                return False
    return True

def validar_jugada(tablero, fila, columna, elemento):
    if validar_fila(tablero, fila, elemento) and validar_columna(tablero, columna, elemento) and validar_subcuadricula(fila, columna, tablero, elemento):
        return True
    else:
        return 


#Funciones para ayudar al sudoku
def cargar_configuracion():
    if os.path.exists(ARCHIVO_CONFIG):
        with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return CONFIG_DEFAULT
    
def guardar_configuracion(config):
    with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
        
def cargar_bitacora():
    if os.path.exists(ARCHIVO_BITACORA):
        with open(ARCHIVO_BITACORA, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def guardar_bitacora(bitacora):
    with open(ARCHIVO_BITACORA, "w", encoding="utf-8") as f:
        json.dump(bitacora, f, ensure_ascii=False, indent=4)

def cargar_juego():
    if os.path.exists(ARCHIVO_JUEGO):
        with open(ARCHIVO_JUEGO, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}
    
def guardar_juego(juego):
    with open(ARCHIVO_JUEGO, "w", encoding="utf-8") as f:
        json.dump(juego, f, ensure_ascii=False, indent=4)

def guardar_partida_actual(tablero, partida_actual, nivel, entry_jugador, juego_iniciado):
    if juego_iniciado.get()==False:
        messagebox.warning("Error", "EMPIECE UNA PARTIDA PRIMERO")
        return
    
    nombre = entry_jugador.get()
    datos = cargar_juego()
    datos[nombre] = {
        "nivel": nivel,
        "tablero": tablero,
        "partida_fija": partida_actual[0]
        }
    guardar_juego(datos)
    messagebox.showinfo("Guardado", "¡Juego guardado correctamente!")

def guardar_en_bitacora(nombre, nivel, segundos_jugados): #Modificada en el Programa 3
    abb_facil, abb_intermedio, abb_dificil = cargar_bitacora_pkl()

    nueva_partida = Partida(nombre, nivel, segundos_jugados, datetime.now().strftime("%Y%m%dT%H%M%S"))

    if nivel == "facil":
        abb_facil.insertar_nodo(nueva_partida)
    elif nivel == "intermedio":
        abb_intermedio.insertar_nodo(nueva_partida)
    else:
        abb_dificil.insertar_nodo(nueva_partida)

    guardar_bitacora_pkl(abb_facil, abb_intermedio, abb_dificil)



def cargar_partida_actual(juego_iniciado, entry_jugador, tablero, botones_tablero, partida_actual, nivel, frame_tablero):
    if juego_iniciado.get()==True:
        messagebox.showwarning("Error", "DEBE TERMINAR LA PARTIDA ACTUAL PARA CARGAR OTRA")
        return

    nombre = entry_jugador.get()
    datos = cargar_juego()
        
    if nombre not in datos:
        messagebox.showwarning("Error", "NO TIENE UN JUEGO GUARDADO CON ESTA DIFICULTAD")
        return

    partida_guardada = datos[nombre]
    partida_actual[0] = partida_guardada["partida_fija"]


    for btn_viejos in frame_tablero.winfo_children():
        btn_viejos.destroy()

    for i in range(9):
        for j in range(9):
            tablero[i][j] = partida_guardada["tablero"][i][j]

    for i in range(9):
        for j in range(9):
            posicion = f"{i},{j}"
            valor = tablero[i][j]
            if posicion in partida_actual[0]:
                btn = tk.Button(frame_tablero, text=str(valor), width=4, height=2, bg="gray70")
            elif valor != 0:
                btn = tk.Button(frame_tablero, text=str(valor), width=4, height=2, bg="white")
            else:
                btn = tk.Button(frame_tablero, text="", width=4, height=2, bg="gray90")
            botones_tablero[i][j] = btn
            btn.grid(row=i, column=j, padx=1, pady=1)

    messagebox.showinfo("Cargado", "¡Juego cargado correctamente!")

def cargar_partida():
    if os.path.exists(ARCHIVO_PARTIDAS):
        with open(ARCHIVO_PARTIDAS, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def deshacer_jugada(pila_realizadas, pila_eliminadas, tablero, frame_tablero, juego_iniciado, botones_tablero, contador_jugadas, texto_contador ):
    if juego_iniciado.get() == False:
        messagebox.showwarning("Error", "EMPIECE UNA PARTIDA PRIMERO")

    elif len(pila_realizadas) == 0:        
        messagebox.showwarning("Error", "DEBE HACER UNA JUGADA PRIMERO")

    else:
        jugada = pila_realizadas.pop()
        
        fila, columna, elemento = jugada
        tablero[fila][columna] = 0
    
        #Buscar el botón en el frame y borrarle el texto
        btn = botones_tablero[fila][columna]
        btn.configure(text="", bg="gray90")
        pila_eliminadas.append(jugada)
        
        #Funcionalidad propia Programa 3
        contador_jugadas.set(contador_jugadas.get() + 1)
        texto_contador.set(f"Jugadas: {contador_jugadas.get()}")

def rehacer_jugada(pila_realizadas, pila_eliminadas, tablero, frame_tablero, juego_iniciado, botones_tablero, contador_jugadas, texto_contador ):
    if juego_iniciado.get() == False:
        messagebox.showwarning("Error", "EMPIECE UNA PARTIDA PRIMERO")

    elif len(pila_eliminadas) == 0:
        messagebox.showwarning("Error", "DEBE DESHACER UNA JUGADA PRIMERO")

    else:
        jugada = pila_eliminadas.pop()
        pila_realizadas.append(jugada)
        
        fila, columna, elemento = jugada
        tablero[fila][columna] = elemento

        #Buscar el botón en el frame y darle de nuevo el texto
        btn = botones_tablero[fila][columna]
        btn.configure(text=str(elemento), bg="white")

        #Funcionalidad propia Programa 3
        contador_jugadas.set(contador_jugadas.get() + 1)
        texto_contador.set(f"Jugadas: {contador_jugadas.get()}")


def borrar_juego(pila_realizadas, pila_eliminadas, tablero, frame_tablero, juego_iniciado, partida_actual, botones_tablero):
    if juego_iniciado.get() == False:
        messagebox.showwarning("Error", "EMPIECE UNA PARTIDA PRIMERO")

    else:
        respuesta = messagebox.askyesno("Confirmar", "¿ESTÁ SEGURO DE BORRAR EL JUEGO?")
        
        if respuesta==True:
            pila_realizadas.clear()
            pila_eliminadas.clear()
            for i in range(9):
                for j in range(9):
                    posicion = f"{i},{j}"
                    if posicion not in partida_actual[0]:
                        tablero[i][j] = 0
                        btn = botones_tablero[i][j]
                        btn.configure(text="", bg="gray90")

def terminar_juego(juego_iniciado, ventana_jugar, cronometro_activo):
    if juego_iniciado.get() == False:
        messagebox.showwarning("Error", "EMPIECE UNA PARTIDA PRIMERO")

    else:
        respuesta = messagebox.askyesno("Confirmar", "¿ESTÁ SEGURO DE TERMINAR LA PARTIDA?")

        if respuesta==True:
            cronometro_activo.set(False)
            ventana_jugar.destroy()
        else:
            pass

def generar_topx():
    abb_facil, abb_intermedio, abb_dificil = cargar_bitacora_pkl()

    c = canvas.Canvas("top_x_sudoku.pdf", pagesize=letter)
    ancho, alto = letter
    y = alto - 50

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, y, "TOP X - SUDOKU")
    y -= 40

    for nivel, abb in [("facil", abb_facil), ("intermedio", abb_intermedio), ("dificil", abb_dificil)]:
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"NIVEL {nivel.upper()}:")
        y -= 20

        partidas = abb.recorrer_arbol()
        for indice_x, partida in enumerate(partidas):
            c.setFont("Helvetica", 12)
            c.drawString(70, y, f"{indice_x+1} - {partida}")
            y -= 20
        y -= 10

    c.save()
    os.startfile("top_x_sudoku.pdf")





#PROGRAMA 3:
def cargar_bitacora_pkl():
    if os.path.exists(ARCHIVO_BITACORA_PKL):
        with open(ARCHIVO_BITACORA_PKL, "rb") as f:
            return pickle.load(f)
    else:
        return abb_facil, abb_intermedio, abb_dificil

def guardar_bitacora_pkl(abb_facil, abb_intermedio, abb_dificil):
    with open(ARCHIVO_BITACORA_PKL, "wb") as f:
        pickle.dump((abb_facil, abb_intermedio, abb_dificil), f)

#Generar el tablero sin el archivo partidassudoku2026.py usado en el anterior
def generar_tablero(elementos):
    tablero = []
    for _ in range(9):
        tablero.append([0]*9)
    llenar_tablero(tablero, elementos)
    return tablero

def llenar_tablero(tablero, elementos):
    for i in range(9):
        for j in range(9):
            if tablero[i][j] == 0:
                lista_elementos = list(elementos)
                random.shuffle(lista_elementos)
                for element in lista_elementos:
                    if validar_jugada(tablero, i, j, element): 
                        tablero[i][j] = element
                        if llenar_tablero(tablero, elementos):
                            return True
                        tablero[i][j] = 0
                return False
    return True

def quitar_casillas(tablero, nivel):
    if nivel == "facil":
        cantidad = 35
    elif nivel == "intermedio":
        cantidad = 45
    else:
        cantidad = 55
        
    contador = 0
    while contador < cantidad:
        fila = random.randint(0, 8)
        columna = random.randint(0, 8)
        if tablero[fila][columna] != 0:
            tablero[fila][columna] = 0
            contador += 1

#Creación de una cuenta de usuario
def generar_codigo():
    codigo = random.randint(100000 , 999999)
    cod_hash = encriptar_codigo(str(codigo))
    return codigo, cod_hash

def encriptar_codigo(codigo):
    cod_encriptado = hashlib.sha256(codigo.encode()).hexdigest()
    return cod_encriptado


def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []
    
def guardar_usuarios(usuarios):
    with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)

#Parte de iniciar sesión
def buscar_usuario(correo):
    usuarios = cargar_usuarios()
    
    for cuenta in usuarios:
        if cuenta["correo"] == correo:
            return cuenta
    return None

def crear_usuario(correo, nombre):
    usuarios = cargar_usuarios()
    
    if len(usuarios) == 0:
        nuevo_id = 1
    else:
        id_max = max(usuario["id"] for usuario in usuarios)
        nuevo_id = id_max+1

    codigo, cod_hash = generar_codigo()
    fecha_actual = datetime.now().strftime("%Y%m%dT%H%M%S")

    nuevo_usuario = {
        "id": nuevo_id,
        "correo": correo,
        "código_ingreso": cod_hash,
        "nombre": nombre,
        "fecha_creación": fecha_actual
        }

    usuarios.append(nuevo_usuario)
    guardar_usuarios(usuarios)

    return codigo

def generar_nuevo_codigo(correo):
    usuarios = cargar_usuarios()
    codigo, codigo_hash = generar_codigo()
    
    for usuario in usuarios:
        if usuario["correo"] == correo:
            usuario["código_ingreso"] = codigo_hash
    
    guardar_usuarios(usuarios)
    return codigo

def validar_codigo(correo, codigo_ingresado):
    usuarios = cargar_usuarios()
    codigo_hash = encriptar_codigo(codigo_ingresado)
    
    for usuario in usuarios:
        if usuario["correo"] == correo and usuario["código_ingreso"] == codigo_hash:
            return usuario
    return None

def avanzar_nivel(caso_multinivel): #Para hacer funcionar el multinivel
    nivel_actual = caso_multinivel.get()
    indice_actual = NIVELES.index(nivel_actual)
    siguiente_indice = (indice_actual + 1) % 3
    nuevo_nivel = NIVELES[siguiente_indice]
    caso_multinivel.set(nuevo_nivel)
    return nuevo_nivel
    


#Ventana de Login
def iniciar_sesion():
    raiz_oculta = tk.Tk()
    raiz_oculta.withdraw() #Evita que se cree una ventana extra
    
    ventana_login = tk.Toplevel()
    ventana_login.title("Iniciar Sesión")
    ventana_login.geometry("800x600")
    
    lbl_correo = tk.Label(ventana_login, text="Correo electrónico:")
    lbl_correo.pack(pady=10)
    
    entry_correo = tk.Entry(ventana_login, width=30)
    entry_correo.pack(pady=5)

    def mostrar_pantalla_codigo(correo):
        lbl_correo.destroy()
        entry_correo.destroy()
        btn_continue.destroy()
    
        lbl_codigo = tk.Label(ventana_login, text="Ingrese el código de 6 dígitos:")
        lbl_codigo.pack(pady=10)
    
        entry_codigo = tk.Entry(ventana_login, width=30)
        entry_codigo.pack(pady=5)

        def verificar_codigo():
            codigo_ingresado = entry_codigo.get()
            usuario = validar_codigo(correo, codigo_ingresado)
    
            if usuario is not None:
                messagebox.showinfo("Bienvenido", f"¡Bienvenido, {usuario['nombre']}!")
                ventana_login.destroy()
                abrir_menu_principal(usuario["nombre"], raiz_oculta)
            else:
                messagebox.showwarning("Error", "Código incorrecto")

        btn_ingresar = tk.Button(ventana_login, text="Ingresar", command=verificar_codigo)
        btn_ingresar.pack(pady=20)

    def verificar_correo():
        correo = entry_correo.get()
        usuario = buscar_usuario(correo)
    
        if usuario is None: #Proceso de creación de la cuenta
            respuesta = messagebox.askyesno("Cuenta no encontrada", "Este correo no existe. ¿Desea crear una cuenta nueva?")
            
            if respuesta:
                nombre = simpledialog.askstring("Nombre", "Ingrese su nombre de jugador:")
                
                if nombre:
                    codigo = crear_usuario(correo, nombre)
                    messagebox.showinfo("Código generado", f"Su código de ingreso es: {codigo}")
                    mostrar_pantalla_codigo(correo)
            else:
                return
            
        else: #Genera código nuevo para usuario existente
            codigo = generar_nuevo_codigo(correo)
            messagebox.showinfo("Código generado", f"Su código de ingreso es: {codigo}")
            mostrar_pantalla_codigo(correo)

    btn_continue = tk.Button(ventana_login, text="Continuar", #Boton para iniciar sesión
                             width=20,
                             height=2,
                             bg="azure",
                             fg="black",
                             font=("Arial", 12, "bold"),
                             command=verificar_correo)
    btn_continue.pack(pady=20)

#Valores personalizados
def validar_elementos_personalizados(texto):
    if len(texto) != 9:
        return False
    if len(set(texto)) != 9:
        return False
    return True




def abrir_menu_principal(nombre_jugador, raiz_oculta):#Creación de ventana
    global ventana
    ventana = raiz_oculta
    ventana.deiconify()
    ventana.title("Sudoku")
    ventana.configure(bg="OliveDrab4")
    ventana.geometry("800x600")
    #Titulo Sudoku
    titulo = tk.Label(ventana, text="SUDOKU", 
                      font=("Arial", 36, "bold"),
                      bg="OliveDrab4",
                      fg="white")
    titulo.pack(pady=20)

    #Botones
    btn_jugar = tk.Button(ventana, text="Jugar", 
                          width=20, 
                          height=2,
                          bg="gray60",
                          fg="black",
                          font=("Arial", 14, "bold"),
                          command=jugar)
    btn_jugar.pack(pady=10)
    btn_configurar = tk.Button(ventana, text="Configurar", 
                          width=20, 
                          height=2,
                          bg="gray55",
                          fg="black",
                          font=("Arial", 14, "bold"),
                          command=configurar)
    btn_configurar.pack(pady=10)
    btn_ayuda = tk.Button(ventana, text="Ayuda", 
                          width=20, 
                          height=2,
                          bg="gray50",
                          fg="black",
                          font=("Arial", 14, "bold"),
                          command=ayuda)
    btn_ayuda.pack(pady=10)
    btn_acerca = tk.Button(ventana, text="Acerca de", 
                          width=20, 
                          height=2,
                          bg="gray45",
                          fg="black",
                          font=("Arial", 14, "bold"),
                          command=acerca_de)
    btn_acerca.pack(pady=10)
    btn_salir = tk.Button(ventana, text="Salir", 
                          width=20, 
                          height=2,
                          bg="gray40",
                          fg="black",
                          font=("Arial", 14, "bold"),
                          command=salir)
    btn_salir.pack(pady=10)
    

    ventana.mainloop()

# iniciar_sesion()
raiz_test = tk.Tk()
abrir_menu_principal("TestUser", raiz_test)
