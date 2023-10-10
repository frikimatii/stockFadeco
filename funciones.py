import tkinter as tk
from tkinter import ttk
import sqlite3

piezas_predefinidas = ["Base", "Motor", "Teletubi", "Cuchilla", "Vela",
                       "CubreCuchilla", "Cabezal", "Planchada", "Brazo", "Tapa_afilador", "Afilador", "Patas"]

order_ascendente = True

# Variables Globales para rastrear las maquinas ensambladas

maquinas_mes = 0

# Función para mostrar los datos de la base de dat
def mostrar_datos():
    conn = sqlite3.connect("Stock_Fadeco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Pieza, Cantidad FROM piezas_de_330")
    stock = cursor.fetchall()
    conn.close()

    # ordena los datos segun la direcciom del ordenamiento
    stock.sort(key=lambda x: x[1], reverse=not order_ascendente)

    # Borra el contenido actual de la lista
    for item in piezas_listbox.get_children():
        piezas_listbox.delete(item)

    # Agrega los datos a la lista
    for pieza, cantidad in stock:
        piezas_listbox.insert("", "end", values=(pieza, cantidad))

# Función para calcular cuántas máquinas se pueden armar

def calcular_maquinas_posibles():

    conn = sqlite3.connect("Stock_Fadeco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Pieza, Cantidad FROM piezas_de_330")
    stock = dict(cursor.fetchall())
    conn.close()

    # Define las cantidades requeridas para una máquina
    cantidades_requeridas = {
        "Base": 1,
        "Motor": 1,
        "Teletubi": 1,
        "Cuchilla": 1,
        "Vela": 1,
        "CubreCuchilla": 1,
        "Cabezal": 1,
        "Planchada": 1,
        "Brazo": 1,
        "Tapa_afilador": 1,
        "Afilador": 1,
        "Patas": 4  # Agregamos la cantidad de patas necesarias
    }

    # Obtener el número deseado de máquinas desde la entrada del usuario
    try:
        cantidad_deseada = int(cantidad_entry.get())
    except ValueError:
        resultado_label.config(text="Ingrese un número válido.")
        return

    # Encuentra el número máximo de máquinas que se pueden armar
    # Inicialmente, asume que puedes armar infinitas máquinas
    maquinas_posibles = float("inf")

    for pieza, cantidad in cantidades_requeridas.items():
        if pieza in stock:
            cantidad_disponible = stock[pieza]
            cantidad_requerida = cantidades_requeridas[pieza]
            maquinas_posibles = min(
                maquinas_posibles, cantidad_disponible // cantidad_requerida)

    if cantidad_deseada <= maquinas_posibles:
        resultado_label.config(
            text=f"Es posible armar {cantidad_deseada} máquinas.")
    else:
        resultado_label.config(
            text=f"No es posible armar {cantidad_deseada} máquinas.")
        print("No es Posible armar maquinas")
        piezas_faltantes = {}
        for pieza, cantidad in cantidades_requeridas.items():
            cantidad_disponible = stock.get(pieza, 0)
            cantidad_requerida = cantidad * cantidad_deseada
            if cantidad_requerida > cantidad_disponible:
                piezas_faltantes[pieza] = cantidad_requerida - cantidad_disponible
        resultado_label.config(text=f"Piezas faltantes: {piezas_faltantes}")

# Funciopn para actualizar la cantida de piezas
def actualizar_cantidad_piezas():
    pieza_actualizar = pieza_combobox.get()
    cantidad_actualizar = cantidad_nueva_entry.get()

    # Validar que la cantidad ingresada sea un número válido
    try:
        cantidad_actualizar = int(cantidad_actualizar)
        if cantidad_actualizar < 0:
            raise ValueError("La Cantidad no puede ser Negativa")
    except ValueError as e:
        resultado_label.config(text=str(e))
        return

    # Conectar a la base de datos y actualizar la cantidad de piezas
    conn = sqlite3.connect("Stock_Fadeco.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Cantidad FROM piezas_de_330 WHERE Pieza=?", (pieza_actualizar,))
    cantidad_actual = cursor.fetchone()

    if cantidad_actual is not None:
        cantidad_actual = cantidad_actual[0]  # Extraer el valor de la tupla
        nueva_cantidad = cantidad_actual + cantidad_actualizar
        cursor.execute("UPDATE piezas_de_330 SET Cantidad=? WHERE Pieza=?",
                       (nueva_cantidad, pieza_actualizar))
    else:
        resultado_label.config(
            text=f"La pieza {pieza_actualizar} no se puede modificar.")

    conn.commit()
    conn.close()
    mostrar_datos()

#funcion para eliminar Piezas
def eliminar_pieza():
    pieza_eliminar = pieza_eliminar_combobox.get()
    cantidad_eliminar = cantidad_eliminar_entry.get()

    # Validar que la cantidad ingresada sea un número válido
    try:
        cantidad_eliminar = int(cantidad_eliminar)
        if cantidad_eliminar < 0:
            raise ValueError("La Cantidad no puede ser Negativa")
    except ValueError as e:
        resultado_label.config(text=str(e))
        return

    # Conectar a la base de datos y eliminar la pieza
    conn = sqlite3.connect("Stock_Fadeco.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT cantidad FROM piezas_de_330 WHERE Pieza = ?", (pieza_eliminar,))
    cantidad_actual = cursor.fetchone()

    if cantidad_actual is not None:
        cantidad_actual = cantidad_actual[0]  # extrate el valor de la tupla
        if cantidad_eliminar <= cantidad_actual:
            nueva_cantidad = cantidad_actual - cantidad_eliminar
            if nueva_cantidad >= 0:
                cursor.execute(
                    "UPDATE piezas_de_330 SET Cantidad = ? WHERE Pieza=?", (nueva_cantidad, pieza_eliminar))
            else:
                resultado_label.config(
                    text=f"No se puede eliminar la pieza {pieza_eliminar}.")
        else:
            resultado_label.config(
                text=f"No hay suficientes {pieza_eliminar} en el stock.")
    else:
        resultado_label.config(
            text=f"La pieza {pieza_eliminar} no se puede eliminar.")

    conn.commit()
    conn.close()
    mostrar_datos()

#funcion para cambiar el ordenb de mayor a menor y visecersas 
def cambiar_orden():
    global order_ascendente
    order_ascendente = not order_ascendente
    mostrar_datos()

#funcion para resetar el mes 
def resetear_mes():
    global maquinas_mes
    maquinas_mes = 0
    maquinas_mes_label.config(text=f"Maquinas Terminadas en el mes: {maquinas_mes} ")

# Funcion de maquinas terminadas 
def ensamblar_maquinas():
    global maquinas_dia, maquinas_mes
    cantidad_ensamblada = cantidad_ensamblar_entry.get()

    # Validamos que la cantidad ingresada sea un número válido
    try:
        cantidad_ensamblada = int(cantidad_ensamblada)
    except ValueError:
        resultado_label.config(text="Ingrese una Cantidad Válida")
        return

    conn = sqlite3.connect("Stock_Fadeco.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Pieza, Cantidad FROM piezas_de_330")
    stock = cursor.fetchall()

    cantidades_requeridas = {
        "Base": 1,
        "Motor": 1,
        "Teletubi": 1,
        "Cuchilla": 1,
        "Vela": 1,
        "CubreCuchilla": 1,
        "Cabezal": 1,
        "Planchada": 1,
        "Brazo": 1,
        "Tapa_afilador": 1,
        "Afilador": 1,
        "Patas": 4
    }

    for pieza, cantidad in stock:
        if pieza in cantidades_requeridas:
            cantidades_requerida = cantidades_requeridas[pieza] * cantidad_ensamblada
            if cantidad < cantidades_requerida:
                resultado_label.config(text=f"No hay suficientes {pieza} en el stock para ensamblar {cantidad_ensamblada} máquinas.")
                conn.close()
                return

    # Si hay suficientes piezas, ensamblar las máquinas y actualizar las cantidades en la base de datos
    for pieza, cantidad in stock:
        if pieza in cantidades_requeridas:
            cantidad_requerida = cantidades_requeridas[pieza] * cantidad_ensamblada
            nueva_cantidad = cantidad - cantidad_requerida
            cursor.execute("UPDATE piezas_de_330 SET Cantidad=? WHERE Pieza=?", (nueva_cantidad, pieza))

    # Actualizar el contador de máquinas ensambladas

    maquinas_mes += cantidad_ensamblada

    # Crear una etiqueta para mostrar la cantidad total de máquinas ensambladas en el mes
    maquinas_mes_label.config(text=f"Maquinas Terminadas en el mes: {maquinas_mes}")

    # Mostrar la cantidad total de máquinas ensambladas
    resultado_label.config(text=f"Se Armaron {cantidad_ensamblada} máquinas \h Total del mes: {maquinas_mes}")

    conn.commit()
    conn.close()
    mostrar_datos()



# Crear la ventana principal
root = tk.Tk()
root.title("Gestión de Stock") 

# Crear un ComboBox para seleccionar la pieza a actualizar


#--------------------------------------------------------------
frame1 = ttk.Frame(root)
frame1.grid(row=0, column=0, padx=0, pady=0, sticky="w")
#-------------------------------------------------------------

# BOTON mostrar Datos
mostrar_button = ttk.Button(frame1, text="Mostrar Datos", command=mostrar_datos)
mostrar_button.grid(row=0, column=0, padx=5, pady=5)

# Botton Cambio de lista de Orden
orden_boton = ttk.Button(frame1, text="Ordenar Cantidad", command=cambiar_orden)
orden_boton.grid(row=0, column=1, padx=5, pady=5)

#Crear una lista de Piezas usando ttk.treeview (arbol)
piezas_listbox = ttk.Treeview(root, columns=("Pieza", "Cantidad"))
piezas_listbox.heading("Pieza", text="Pieza")
piezas_listbox.heading("Cantidad", text="Cantidad")

piezas_listbox.config(height=15)

piezas_listbox.grid(row=1, column=0, padx=5, pady=5)

#aniadir las columnas de la vista arbol
piezas_listbox.column("#0", width=0, stretch=tk.NO)
piezas_listbox.column("Pieza", anchor=tk.W, width=170)
piezas_listbox.column("Cantidad", anchor=tk.W, width=90)
 

#-------------------------------------------------------
frame2 = ttk.Frame(root)
frame2.grid(row=2, column=0, padx=5, pady=5, sticky="w")
#-----------------------------------------------------


# Crear un botón para calcular máquinas posibles
calcular_button = ttk.Button(
    frame2, text="Calcular Máquinas Deseadas", command=calcular_maquinas_posibles)
calcular_button.grid(row=2, column=1, padx=1, pady=1)


# Crear una entrada para ingresar la cantidad deseada de máquinas
cantidad_label = ttk.Label(frame2, text="Cantidad Deseadas:")
cantidad_label.grid(row=0, column=0, padx=1, pady=1, )
cantidad_entry = ttk.Entry(frame2)
cantidad_entry.grid(row=0, column=1, padx=1, pady=1)

frame2.grid_rowconfigure(0, weight=2)
frame2.grid_columnconfigure(0, weight=2)
#---------------------------------------------------
frame3 = ttk.Frame(root)
frame3.grid(row=1, column=1, padx=0, pady=0, sticky="w")
#------------------------------------------------------


piezas_disponibles = []  # Lista para almacenar las piezas disponibles

conn = sqlite3.connect("Stock_Fadeco.db")
cursor = conn.cursor()
cursor.execute("SELECT Pieza FROM piezas_de_330")
for row in cursor.fetchall():
    piezas_disponibles.append(row[0])
conn.close()
 

# Crear una etiqueta y entrada para actualizar piezas
actualizar_label = ttk.Label(frame3, text="Agregar Pieza:")
actualizar_label.grid(row=0, column=0, padx=2, pady=2)

pieza_combobox = ttk.Combobox(frame3, values=piezas_predefinidas, state="readonly")
pieza_combobox.grid(row=0, column=1, padx=2, pady=2)

cantidad_nueva_entry = ttk.Entry(frame3)
cantidad_nueva_entry.grid(row=1, column=1, padx=2, pady=2)

cantidad_nueva_label = ttk.Label(frame3, text="Cantidad:")
cantidad_nueva_label.grid(row=1, column=0, padx=2, pady=2)

actualizar_button = ttk.Button(
    frame3, text="Actualizar Cantidad", command=actualizar_cantidad_piezas)
actualizar_button.grid(row=2, column=1, padx=5, pady=5)

#--------------------------------------------------------------------------------------
separator1 = ttk.Separator(frame3, orient="horizontal")
separator1.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
#--------------------------------------------------------------------------------------

# Crear una etiqueta y ComboBox para eliminar piezas
eliminar_label = ttk.Label(frame3, text="Eliminar Piezas:")
eliminar_label.grid(row=4, column=0, padx=2, pady=2)

pieza_eliminar_combobox = ttk.Combobox(frame3, values=piezas_predefinidas, state="readonly")
pieza_eliminar_combobox.grid(row=4, column=1, padx=2, pady=2)

cantidad_eliminar_label = ttk.Label(frame3, text="Cantidad")
cantidad_eliminar_label.grid(row=5, column=0, padx=2, pady=2)
cantidad_eliminar_entry = ttk.Entry(frame3)
cantidad_eliminar_entry.grid(row=5, column=1, padx=2, pady=2)

eliminar_button = ttk.Button(
    frame3, text="Eliminar Pieza", command=eliminar_pieza)
eliminar_button.grid(row=6, column=1, padx=0, pady=5)

#--------------------------------------------------------------------------------------
separator1 = ttk.Separator(frame3, orient="horizontal")
separator1.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
#--------------------------------------------------------------------------------------


# Crear una entrada para ensamblar máquinas
ensamblar_label = ttk.Label(frame3, text="Maquinas del dia: ", anchor="center")
ensamblar_label.grid(row=8, column=0, columnspan=2, padx=0, pady=(0,5))

cantidad_ensamblar_label = ttk.Label(frame3, text="Cantidad Terminadas:")
cantidad_ensamblar_label.grid(row=9, column=0, padx=1, pady=1, sticky="e")

cantidad_ensamblar_entry = ttk.Entry(frame3)
cantidad_ensamblar_entry.grid(row=9, column=1, padx=1, pady=1)

ensamblar_boton = ttk.Button(frame3, text="Confirmar", command=ensamblar_maquinas)
ensamblar_boton.grid(row=10, column=1, padx=4, pady=4)

#--------------------------------------------------------------------------------------
separator1 = ttk.Separator(frame3, orient="horizontal")
separator1.grid(row=11, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
#--------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------
frame4 = ttk.Frame(root)
frame4.grid(row=2, column=1, padx=0, pady=0, sticky="nsew")
#-----------------------------------------------------------------------------

# Crear una etiqueta para mostrar la cantidad total de máquinas ensambladas en el mes
maquinas_mes_label = ttk.Label(frame4, text=f"Maquinas Terminadas en el mes: {maquinas_mes}")
maquinas_mes_label.grid(row=0, column=0, padx=0, pady=0)

resetear_mes_button = ttk.Button(frame4, text="Resetear Mes", command=resetear_mes)
resetear_mes_button.grid(row=1, column=0, padx=0, pady=4)

frame4.grid_rowconfigure(0, weight=1)
frame4.grid_columnconfigure(0, weight=1)
#-----------------------------------------------------------------------------

# Crear una etiqueta para mostrar el resultado
resultado_label = ttk.Label(root, text="")
resultado_label.grid(row=6, column=0, padx=5, pady=5)


root.mainloop()
