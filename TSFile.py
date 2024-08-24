#---------------------------------------------------------------------------------------
#   (C) 2023 Universidad de Guadalajara.
#    @author Prof. Carlos Ramon Patiño.
#---------------------------------------------------------------------------------------
import math

class TSFile:
    #----------------------------------
    # CONSTRUCTOR
    #----------------------------------
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
        lines.append("\t" + self.__marsh_num(0))
        #... or maybe more, for specialized files
        if ("extra_lines" in dicProps.keys()):
            for ln in dicProps["extra_lines"]:
                lines.append(ln) #Add as is... no ENTER at the end
                ln_cnt += 1
        lines[2] += "\t" + self.__marsh_num(ln_cnt)
        lines.append("")
        lines.append("")
        lines.append("_ID\t")
        for col in dicProps["usr_columns"]:
            if (col["tipo"] in ("NUM", "TEXT", "LABEL", "BINARY")):
                lines[-3] += "\t" + col["tipo"]  
                lines[-2] += "\t" + self.__marsh_num(col["size"]) 
                lines[-1] += "\t" + col["label"] 
                col_cnt += 1
            else:
                pass # error
        lines[2] += "\t" + self.__marsh_num(col_cnt)
        lines[2] += "\t" + self.__marsh_num(1)
                
        lines.append("\tMETADATA_END\t..........")
        hdr_sz = 0
        hdr_txt = ""
        for i in range(len(lines)):
            lines[i] += "\t\n"
            hdr_sz += len(lines[i])+1  #+1 porque se agrega un \r al ENTER
            hdr_txt += lines[i]
        self.file.write(hdr_txt.replace("..........",
                                         self.__marsh_num(hdr_sz)))
    
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

    def __process_hdr_cols(self, ln_head, ln_size, ln_type):
        #3 filas pq cada columna necesita una 3-tupla, todas del mismo tamaño
        if (len(ln_head) != len(ln_size) or
            len(ln_head) != len(ln_type)):
            pass #format error
        #index 0 es caso expecial, index -1 es vacio
        if (ln_head[0] == "_ID"):
            self.col_hdr = { "_ID": (10, "NUM")}
        else:
            pass #Error de formato
        for i in range(1, len(ln_head)-1):
            #los titulos de columna son siempre alfabeticas (con guion bajo para metacolumnas)
            if (not ln_head[i].lstrip("_").isalpha()):
                pass # No es un encabezado de columna, error
            etq = ln_head[i].upper()
            tipo = ln_type[i].upper()
            #modificado ===================
            # devolvia un error cuando convertia ''
            if(ln_size[i].strip() != ''):
                tamano = int(ln_size[i].strip())
            else:
                tamano = 0
            #modificado ======================
            #tamano = int(ln_size[i].strip())
            #Los titulos de la columna son definidos por el usuario,
            #pero solo existen 4 tipos validos
            if (tipo in ("NUM", "TEXT", "LABEL", "BINARY")): #tipos validos
                self.col_hdr[etq] = (tamano, tipo)
            else: 
                pass #tipo desconocido, error
            #print(etq)


    def b64_decode(b64_txt):
        bin_txt = b64_txt #To be done
        return bin_txt
    
    def b64_encode(bin_txt):
        b64_txt = bin_txt #To be done
        return b64_txt

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
        
    def __unmarsh_num (self, strNum): #De momento, solo enteros
        num = float("nan")
        if (strNum.isnumeric() or (strNum.startswith("-") and
            strNum.lstrip("-").isnumeric())):
            num = int(strNum)
        #elif (float???
        else:
            pass #Not really a number
        return num

    #---------------------------
    # READ RECORD
    #---------------------------
    def read_record(self, rec_num):
        self.file = open(self.filename, 'rt')

        #desplaza el apuntador hasta el registro correcto
        rec_sz = len(self.col_hdr) +2  #1 TAB por columna + \r\n
        for tup in self.col_hdr.values(): 
            rec_sz += tup[0]  #suma los tamaños de cada columna
        self.file.seek(self.props["HDR_SZ"] + (rec_sz*rec_num))
        line = self.file.readline()
        #print(line)
        self.file.close()
        # return self.__unmarshall(line) no funciona
        return line

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
        

    #---------------------------
    # INSERT RECORD
    #---------------------------
    def insert_record(self, tupla):
        #construye la linea, escribela
        self.file = open(self.filename, 'at')     #append, record siempre al final
        ln  = self.__marsh_num(self.props["N"])
        ln += "\t"  #Inserta al final, _IDX es el valor de N
        ln += self.__marshall(tupla)
        self.file.write(ln)
        self.file.close()
        
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

    #--------------------------
    # DUMP
    #--------------------------
    def dump(self):
        for attr in dir(self):
            print("obj.%s = %r" % (attr, getattr(self, attr)))


#---- class end ----

#------------------------
# Some testing code
#------------------------
# tsv = TSFile("Dumm1.txt")
# tsv.read_record(1)
# tsv.read_record(0)
# bla = tsv.read_record(3)
# bla = ("uno", "dos", "tres")
# ln = tsv.insert_record(bla)

# diccionario = {"usr_columns": [
#                    {"tipo": "NUM", "label": "UNO", "size": 10},
#                    {"tipo": "NUM", "label": "DOS", "size": 10},
#                    {"tipo": "NUM", "label": "TRES", "size": 10}]
#               }
# newTsv = TSFile("Dumm2.txt", diccionario)
# tsv = TSFile("Dumm2.txt")
# print(tsv.read_record(0))
# bla = (1,2,3)
# tsv.insert_record(bla)