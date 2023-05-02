#=============================================
# (C) 2023 Universidad de Guadalajara. Cutonala.
#Equipo 2. Llaves primarias y foraneas.
# Villalpando Rivera Ismael.
# Anguiano Serrano Marco Antonio.
# Ramírez Pichardo Oscar Daniel.
# Jaramillo López Juan Luis.
#=============================================

from TSFile import TSFile
import nacl.encoding
import nacl.hash

class Table (TSFile):
    def __init__(self, filename, dicProps = { "reopen" : True }):
        self.filename = filename
        #If reopen toma propiedades del archivo, else archivo de nueva creacion
        if ("reopen" in dicProps.keys()): #El archivo ya existe, lee las propiedades.
            self.file = open(filename, 'rt')
            self.__read_header()
        else: #El archivo aun no existe, crealo con propiedades dadas por el usuario
            self.file = open(filename, 'wt')
            self.__write_header(dicProps)
        self.file.close()

    def __write_header(self, dicProps):
            lines = []
            ln_cnt = 7  #Basic 7-line header ...
            col_cnt = 0
            lines.append("\tMETADATA_BEGIN\t..........")
            lines.append("\tN\tM\tC\tK")
            lines.append("\t" +  self.__marsh_num(0))
            #add primary key--------------------------- 
            #Esto solo fue una prueba, no es viable agregar la pk como meta-registro
            # lines.append("\tPK_"+dicProps["PK_Column"])
            # ln_cnt +=1 
            # -----------------------------------------
            #... or maybe more, for specialized files
            if ("extra_lines" in dicProps.keys()):
                for ln in dicProps["extra_lines"]:
                    lines.append(ln) #Add as is... no ENTER at the end
                    ln_cnt += 1
            lines[2] += "\t" +  self.__marsh_num(ln_cnt)
            lines.append("")
            lines.append("")
            lines.append("_ID") # quite \t, da problemas en la funcion __process_hdr_cols 

            #add primary key and foreign keys-------------------
            lines[-1]+="\t_PK_"+dicProps["PK_Column"]
            pk_fk_cnt = 1 #numero de llaves primarias y foraneas
            if ("FK_Columns" in dicProps.keys() and len(dicProps["FK_Columns"])>0 ):
                #lines[-3] += "\tFK" fue una prueba, da problemas en la funcion __process_hdr_cols 
                #lines[-2] += "\t" +  fue una prueba, da problemas en la funcion __process_hdr_cols 
                for fk in dicProps["FK_Columns"]:
                    lines[-1] +="\t_"+fk
                    pk_fk_cnt += 1
            #--------------------------------------

            for col in dicProps["usr_columns"]:
                if (col["tipo"] in ("NUM", "TEXT", "LABEL", "BINARY")):
                    lines[-3] += "\t" + col["tipo"]  
                    lines[-2] += "\t" +  self.__marsh_num(col["size"]) 
                    lines[-1] += "\t" + col["label"] 
                    col_cnt += 1
                else:
                    pass # error
            lines[2] += "\t" + self.__marsh_num(col_cnt)
            lines[2] += "\t" +  self.__marsh_num(1+pk_fk_cnt) # Modificado, numero de metacolumnas
                    
            lines.append("\tMETADATA_END\t..........")
            hdr_sz = 0
            hdr_txt = ""
            for i in range(len(lines)):
                lines[i] += "\t\n"
                hdr_sz += len(lines[i])+1  #+1 porque se agrega un \r al ENTER
                hdr_txt += lines[i]
            self.file.write(hdr_txt.replace("..........",
                                             self.__marsh_num(hdr_sz)))
    #Funcion no modificada, no es necesario
    def __read_header(self):
        self.props = { "HDR_SZ" : 0}
        lines = []
        self.file.seek(0)
        lines.append(self.file.readline())
        sz = len(lines[0])+1  # +1 porque readline borra el \r del ENTER
        if (lines[0].startswith("\tMETADATA_BEGIN\t") and lines[0].endswith("\t\n")):
            #Lee todas las lineas del encabezado
            i = 1
            while (not lines[-1].startswith("\tMETADATA_END\t")):
                L = self.file.readline()
                if (L.startswith("\t") or L.startswith("_ID\t")):
                    if (L.endswith("\t\n")):
                        lines.append(L)
                        sz += len(L)+1 # +1 porque readline borra el \r del ENTER
                        i += 1
                    else:
                        print("bad line end") #format error
                else:
                    print("bad line start") #format error
            else: #processa...
                if (i < 7):
                    pass # Encabezado incompleto. Throw error
                #BEGIN y END
                self.__process_hdr_begin(sz, lines[0].split("\t"),
                                         lines[-1].split("\t"))
                #CONFIG VALs
                self.__process_hdr_props(lines[1].split("\t"),
                                         lines[2].split("\t"))
                #COLUMN HEADERS
                self.__process_hdr_cols (lines[-2].split("\t"),
                                         lines[-3].split("\t"),
                                         lines[-4].split("\t"))
        else: #not TSV file. throw error?
            pass
    #Funcion no modificada, no es necesario
    def __process_hdr_begin(self, hdr_sz, ln_begin, ln_end):
        if (ln_begin[2] == ln_end[2]):
            if (ln_begin[2].isnumeric()):
                if (hdr_sz == int(ln_begin[2])):
                    self.props["HDR_SZ"] = hdr_sz
                else:
                    print("error")
                    print(hdr_sz)
                    print(int(ln_begin[2]))
                    #pass # error de formato
            else:
                pass # error de formato
        else:
            pass #error de formato
    #Funcion no modificada, no es necesario
    def __process_hdr_props(self, ln_key, ln_val):
        #en las propiedades debe existir una etiqueta por valor
        if (len(ln_key) != len(ln_val)):
            pass #format error
        #index 0 e index -1 son vacios
        for i in range(1, len(ln_key)-1):
            #las etiquetas son siempre alfanumericas
            if (not ln_key[i].isalpha()):
                pass # No es una etiqueta, error
            etq = ln_key[i].upper()
            if (etq in ("N", "M", "C", "K")): #dimensiones tabulares
                self.props[etq] = int(ln_val[i])                
            elif (etq in ("CRYP_KEY", "CRYP_NONCE")): #elementos criptograficos
                self.props[etq] = b64_decode(ln_val[i])                
            else: #Etiqueta desconocida, pasala como va
                self.props[etq] = ln_val[i]
    #Funcion modificada
    def __process_hdr_cols(self, ln_head, ln_size, ln_type):
        #3 filas pq cada columna necesita una 3-tupla, todas del mismo tamaño
        if (ln_head[0] == "_ID"):
            self.col_hdr = { "_ID": (10, "NUM")}
        else:
            pass #Error de formato
        #quitar llaves foraneas y primarias del arreglo ln_head y agregar llaves a self.col_hdr =====
        self.pk_fk_num = 0
        ln_head_copy = ln_head.copy()
        for x in ln_head_copy:
            if(x.startswith("_") and x != "_ID"):
                if(x.startswith("_PK")):
                    ln_head.remove(x)
                    self.col_hdr[x] = (64,"PK")
                    self.pk_fk_num +=1  
                else:                    
                    ln_head.remove(x)
                    self.col_hdr[x] = (64,"FK")
                    self.pk_fk_num +=1
        #=======================================
        if (len(ln_head) != len(ln_size) or
            len(ln_head) != len(ln_type)):
            pass #format error
        #index 0 es caso expecial, index -1 es vacio

        for i in range(1, len(ln_head)-1):
            #los titulos de columna son siempre alfabeticas (con guion bajo para metacolumnas)
            if (not ln_head[i].lstrip("_").isalpha()):
                pass # No es un encabezado de columna, error
            etq = ln_head[i].upper()
            tipo = ln_type[i].upper()
            #modificado ===================
            # devolvia un error cuando convertia '', por el \t del _ID 
            # if(ln_size[i].strip() != ''):
            #     tamano = int(ln_size[i].strip())
            # else:
            #     tamano = 0
            tamano = int(ln_size[i].strip())
            #modificado ======================
            #Los titulos de la columna son definidos por el usuario,
            #pero solo existen 4 tipos validos
            if (tipo in ("NUM", "TEXT", "LABEL", "BINARY")): #tipos validos
                self.col_hdr[etq] = (tamano, tipo)
            else: 
                pass #tipo desconocido, error
            #print(etq)
        #print(self.col_hdr)
            
    #---------------------------
    # INSERT RECORD
    #---------------------------
    #funcion modificada
    def insert_record(self, tupla):
        #construye la linea, escribela
        self.file = open(self.filename, 'at')     #append, record siempre al final
        ln  = self.__marsh_num(self.props["N"])
        ln += "\t"  #Inserta al final, _IDX es el valor de N
        #insertar pk y fk==========================
        i=0
        if(self.pk_fk_num>0):
            for x in tupla:
                if(i<self.pk_fk_num ):
                    ln += self.hash_txt(str(x)).decode()+"\t"
                i+=1
        #=================================
        ln += self.__marshall(tupla)
        self.file.write(ln)
        self.file.close()
        #insertar pk ===============================
        # tener la pk como un meta registro da mas problemas que beneficios, por lo que sera meta-columna
        # self.file = open(self.filename, 'rt')
        # self.file.seek(0)
        # pk_pos = len (self.file.readline())+1 #METADATA_BEGIN
        # pk_pos += len (self.file.readline())+1 #PARAMETER TITLES
        # pk_pos += len (self.file.readline())+1 #CONFIG VALs
        # ln_pk = self.file.readline().split("\t")
        # self.file.close()

        # self.file = open(self.filename, 'r+t')
        # self.file.seek(pk_pos)
        # print(self.file.readline())
        # print(ln_pk)
        # id_hash = self.hash_txt(str(tupla[0])).decode()
        # self.file.write('\t'+id_hash+'\t\n')
        # self.file.close()
        # #=================================
        #modifica parametro N, tambien en disco
        self.props["N"] += 1
        self.file = open(self.filename, 'rt') #Abre para leer la posicion correcta
        self.file.seek(0)
        foo = len (self.file.readline())+1 #METADATA_BEGIN
        print(foo)
        foo += len(self.file.readline())+1 #PARAMETER TITLES
        print(foo)
        for idx in self.props: #numero de columna del parametro N
            if (idx != "N"):
                while(self.file.read(1) != '\t'): # avanza hasta el tabulador
                    foo+=1
                    print(foo)
            else:
                foo+=1
                self.file.close()
                break
        self.file = open(self.filename, 'r+t') # Abre para sobreescribir
        self.file.seek(foo)
        Nval = str(self.props["N"])
        print(Nval)
        print(Nval.rjust(10, "0"))
        self.file.write(Nval.rjust(10, "0"))
        self.file.close()

    #---------------------------
    # READ RECORD
    #---------------------------
    #funcion modificada
    def read_record(self, rec_num):
        self.file = open(self.filename, 'rt')

        #desplaza el apuntador hasta el registro correcto
        print(len(self.col_hdr))
        rec_sz = len(self.col_hdr) +2  #1 TAB por columna + \r\n
        for tup in self.col_hdr.values(): 
            rec_sz += tup[0]  #suma los tamaños de cada columna
            print(tup[0])
        self.file.seek(self.props["HDR_SZ"] + (rec_sz*rec_num))
        # self.file.seek(819)
        print(rec_sz*rec_num)
        line = self.file.readline()
        # print(line)
        self.file.close()
        # return self.__unmarshall(line) no funciona
        return line
    #Funcion no modificada, no es necesario
    def __marsh_num (self, num): #De momento, solo enteros
        strNum = ""
        if (type(num) == int):
            if (num < 0):
                strNum = "-" + str(num).rjust(9, "0")
            else:
                strNum = str(num).rjust(10, "0")
        else:
            pass
        return strNum
    #Funcion no modificada, no es necesario
    def __unmarsh_num (self, strNum): #De momento, solo enteros
        num = float("nan")
        if (strNum.isnumeric() or (strNum.startswith("-") and
            strNum.lstrip("-").isnumeric())):
            num = int(strNum)
        #elif (float???
        else:
            pass #Not really a number
        return num

    # Funcion creada, convierte texto plano a hash
    def hash_txt(self,txt): 
        HASHER = nacl.hash.sha256
        msg = txt.encode()
        digest = HASHER(msg, encoder=nacl.encoding.HexEncoder)
        return digest
    #Funcion no modificada, no es necesario
    def __marshall(self, tupla):
        if (len(tupla) != self.props["C"]):
            pass # Invalid argument error

        i = 0
        ln = ""
        for keyz in self.col_hdr.keys():
        #    print(keyz)
        #    print( L[i])
            if (keyz.startswith("_")):
                pass  #meta-column, not part of the user data
            else:
                tup = self.col_hdr[keyz]
                if (tup[1] == "NUM"):
                    ln += self.__marsh_num(tupla[i]) + "\t"
                #Los otros casos no funcionan aun...
                elif (tup[1] == "TEXT"):
                    pass
                elif (tup[1] == "LABEL"):
                    pass
                elif (tup[1] ==  "BINARY"):
                    pass 
                i += 1
        return ln+"\n"
    #Funcion no modificada, no funciona correctamente
    def __unmarshall (self, line):
        #print(line)
        L = line.split("\t")
        #for i in range(len(L)):
        #    print("{a} {b}".format(a = i, b =L[i]))
        if (L[-1] == "\n"):
            L.pop()
        else:
            pass #Bad format, error

        i = len(L)
        for keyz in reversed (self.col_hdr.keys()):
            i = i-1
        #    print(keyz)
        #    print( L[i])
            if (keyz.startswith("_")):
                L.pop(i)  #meta-column, not part of the user data
            else:
                tup = self.col_hdr[keyz]
                if (tup[1] == "NUM"):
                    L[i] = self.__unmarsh_num(L[i])
                #Los otros casos no funcionan aun...
                elif (tup[1] == "TEXT"):
                    pass
                elif (tup[1] == "LABEL"):
                    pass
                elif (tup[1] ==  "BINARY"):
                    pass 
        return L

#---- class end ----


#=====================================

#crear tabla
# diccionario = {"usr_columns": [
#                    {"tipo": "NUM", "label": "UNO", "size": 10},
#                    {"tipo": "NUM", "label": "DOS", "size": 10},
#                    {"tipo": "NUM", "label": "TRES", "size": 10}],
#                 "PK_Column": "UNO" , 
#                 "FK_Columns": ["DOS","TRES"]               
#               }
# newTsv = Table("tablepk.txt", diccionario)

#Insertar registro
# tsv = Table("tablepk.txt")
# bla = (4, 5, 6)
# tsv.insert_record(bla)

#Leer registro
# tsv = Table("tablepk.txt")
# print(tsv.read_record(1))
