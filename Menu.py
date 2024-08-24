
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
        nombre_tabla = input("Enter the name of the table: ")
        diccionario = {"usr_columns": [],
                        "PK_Column": "" , 
                        "FK_Columns": []
                    }
        numero_columnas = int(input("Enter the number of columns: "))
    
        
        for i in range(numero_columnas):
            datos_columnas= {"type": "", "label": "", "size": 0}
            nombre_col = input(f"Enter the column name {i}: ")
            tipo_col = input(f"Enter the column type (NUM or TEXT) {i}: ")
            datos_columnas["label"] = nombre_col
            datos_columnas["tipo"] = tipo_col
            datos_columnas["size"] = 10
            diccionario["usr_columns"].append(datos_columnas)

        diccionario["PK_Column"] = diccionario["usr_columns"][0]["label"]

        pregunta_fk = input("Do you want to enter a foreign key? 'y' or 'n': ")
        if(pregunta_fk == 'y'):
            fk= input("Which column will be your foreign key? ")
            diccionario["FK_Columns"].append(fk)
        
        newTsv = Table(nombre_tabla+".txt", diccionario)
        tabla = newTsv
        nomb_tabla = nombre_tabla
        print("Table created successfully")
    except:
        print("ocurrio un error")
 

    

def insertar_registro(n_tabla):
    try:
        if (n_tabla == None):
            n_tabla = input("Enter the name of the table: ") 
        tabla= abrir_tabla(n_tabla)
        n_registro = ()
        for i in range(int(tabla.props["C"])):
            registro = int(input(f"Enter the data {i}: "))
            y = list(n_registro)
            y.append(registro)
            n_registro = tuple(y)
        tabla.insert_record(n_registro)
        print(n_registro)
        print("Data entered successfully")
    except:
        print("ocurrio un error")

def buscar_registro_pk(n_tabla):
    try:
        if (n_tabla == None):
            n_tabla = input("Enter the name of the table: ") 
        tabla= abrir_tabla(n_tabla)
        i_pk = int(input("Enter the primary key: "))
        print(tabla.read_pk(i_pk))
    except:
        print("ocurrio un error")

def buscar_registro_indice(n_tabla):
    try:
        if (n_tabla == None):
            n_tabla = input("Enter the name of the table: ") 
        tabla= abrir_tabla(n_tabla)
        indice = int(input("Enter the index: "))
        print(tabla.read_record(indice))
    except:
        print("ocurrio un error")

flag = True
if __name__ == "__main__":
    try:
        while(flag):
            print("==============Welcome=============")
            opc = input("1-Create table\n2-Insert Record\n3-Search Record by primary key\n4-Search Record by index\n5-Exit\nEnter an option: ")
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