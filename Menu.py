#=============================================
# (C) 2023 Universidad de Guadalajara. Cutonala.
#Equipo 2. Llaves primarias y foraneas.
# Villalpando Rivera Ismael.
# Anguiano Serrano Marco Antonio.
# Ramírez Pichardo Oscar Daniel.
# Jaramillo López Juan Luis.
#=============================================

from Tabla_PK_FK import Table

tabla = None
nomb_tabla = None

def abrir_tabla(nombre_tabla):
    try:
        global tabla, nomb_tabla 
        tabla = Table(nombre_tabla+".txt")
        nomb_tabla = nombre_tabla
        return tabla
    except:
        print("ocurrio un error")

def crear_tabla():
    global tabla, nomb_tabla 
    try:
        nombre_tabla = input("Introduce el nombre de la tabla: ")
        diccionario = {"usr_columns": [],
                        "PK_Column": "" , 
                        "FK_Columns": []
                    }
        numero_columnas = int(input("Introduce el numero de columnas: "))
    
        
        for i in range(numero_columnas):
            datos_columnas= {"tipo": "", "label": "", "size": 0}
            nombre_col = input(f"introduce el nombre de la columna {i}: ")
            tipo_col = input(f"introduce el tipo de la columna (NUM o TEXT) {i}: ")
            datos_columnas["label"] = nombre_col
            datos_columnas["tipo"] = tipo_col
            datos_columnas["size"] = 10
            diccionario["usr_columns"].append(datos_columnas)

        diccionario["PK_Column"] = diccionario["usr_columns"][0]["label"]

        pregunta_fk = input("¿Quieres introducir llave foranea? 'y' o 'n' : ")
        if(pregunta_fk == 'y'):
            fk= input("¿Que columna va ser tu llave forane? : ")
            diccionario["FK_Columns"].append(fk)
        
        newTsv = Table(nombre_tabla+".txt", diccionario)
        tabla = newTsv
        nomb_tabla = nombre_tabla
        print("Tabla creada con exito")
    except:
        print("ocurrio un error")
 

    

def insertar_registro(n_tabla):
    try:
        if (n_tabla == None):
            n_tabla = input("introduce el nombre de la tabla: ") 
        tabla= abrir_tabla(n_tabla)
        n_registro = ()
        for i in range(int(tabla.props["C"])):
            registro = int(input(f"introduce el dato {i}: "))
            y = list(n_registro)
            y.append(registro)
            n_registro = tuple(y)
        tabla.insert_record(n_registro)
        print(n_registro)
        print("datos ingresados con exito")
    except:
        print("ocurrio un error")

def buscar_registro_pk(n_tabla):
    try:
        if (n_tabla == None):
            n_tabla = input("introduce el nombre de la tabla: ") 
        tabla= abrir_tabla(n_tabla)
        i_pk = int(input("introduce la llave primaria: "))
        print(tabla.read_pk(i_pk))
    except:
        print("ocurrio un error")

def buscar_registro_indice(n_tabla):
    try:
        if (n_tabla == None):
            n_tabla = input("introduce el nombre de la tabla: ") 
        tabla= abrir_tabla(n_tabla)
        indice = int(input("ingresa el indice: "))
        print(tabla.read_record(indice))
    except:
        print("ocurrio un error")

flag = True
if __name__ == "__main__":
    try:
        while(flag):
            print("==============Bienvenido=============")
            opc = input("1-Crear tabla\n2-Introducir Registro\n3-Buscar Registro por llave primaria\n4-Buscar Registro por indice\n5-Salir\nIngrese una opcion: ")
            if(opc =="1"):
                crear_tabla()
            elif(opc =="2"):
                insertar_registro(nomb_tabla)
            elif(opc =="3"):
                buscar_registro_pk(nomb_tabla)
            elif(opc =="4"):
            
                buscar_registro_indice(nomb_tabla)
            else:
                flag = False
    except:
        print("ocurrio un error")