#Grupo 19 libreria

import sqlite3
#TO DO
#interfaz grafica para el programa

class Producto:
    def __init__(self,nombre,codigo,precio,cantidad):
        self.nombre = nombre
        self.codigo = codigo
        self.precio = precio
        self.cantidad = cantidad
        self.conn = sqlite3.connect('libreria.db')
        self.cursor = self.conn.cursor()
    def editar(self,nombre,codigo,precio,cantidad):
        self.nombre = nombre
        self.codigo = codigo
        self.precio = precio
        self.cantidad = cantidad
    def editar_tabla(self, nombre, precio, cantidad):
        
        self.cursor.execute('''
            UPDATE Libro
            SET nombre = ?, precio = ?, cantidad = ?
            WHERE codigo = ?
        ''', (nombre, precio, cantidad, self.codigo))
        self.conn.commit()
    
    def insertar_producto(self):
        self.cursor.execute('''
        INSERT INTO Producto (nombre, codigo, precio, cantidad)
        VALUES (?, ?, ?, ?)''', (self.nombre, self.codigo, self.precio, self.cantidad))
        self.conn.commit()

class Libro(Producto):
    def __init__(self,nombre,codigo,precio,cantidad,autor,genero,anio,num_paginas):
        super().__init__(nombre,codigo,precio,cantidad)
        self.autor = autor
        self.genero = genero
        self.anio = anio
        self.num_paginas = num_paginas
        self.conn = sqlite3.connect('libreria.db')
        self.cursor = self.conn.cursor()

    def editar(self,nombre,codigo,precio,cantidad,autor,genero,anio,num_paginas):
        self.nombre = nombre
        self.codigo = codigo
        self.precio = precio
        self.cantidad = cantidad
        self.autor = autor
        self.genero = genero
        self.anio = anio
        self.num_paginas = num_paginas
    
    def editar_tabla(self, nombre, precio, cantidad, autor, genero, anio, num_paginas):
        
        self.cursor.execute('''
            UPDATE Libro
            SET nombre = ?, precio = ?, cantidad = ?, autor = ?, genero = ?, anio = ?, num_paginas = ?
            WHERE codigo = ?
        ''', (nombre, precio, cantidad, autor, genero, anio, num_paginas, self.codigo))
        self.conn.commit()

    def __str__(self):
        return f"{self.nombre} {self.precio}"
    def insertar_libro(self):
        self.cursor.execute('''
        INSERT INTO Libro (nombre, codigo, precio,cantidad, autor, genero, anio, num_paginas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (self.nombre, self.codigo, self.precio,self.cantidad, self.autor, self.genero, self.anio, self.num_paginas))
        self.conn.commit()
        print('completado')

class Inventario:
    def __init__(self):
        self.lista_inventario= []
        self.conn = sqlite3.connect('libreria.db')
        self.cursor = self.conn.cursor()

    def agregar_inventario(self,producto):
        for producto_existente in self.lista_inventario:
            if producto.codigo == producto_existente.codigo:
                print('Ya existe un producto con ese nombre')
                return 0
        self.lista_inventario.append(producto)

    
    def cargar_inventario_desde_bd(self):
        # Recupera los productos de la tabla Producto
        self.cursor.execute('SELECT nombre, codigo, precio, cantidad FROM Producto')
        productos = self.cursor.fetchall()
        
        # Recupera los libros de la tabla Libro
        self.cursor.execute('SELECT nombre, codigo, precio,cantidad, autor, genero, anio, num_paginas FROM Libro')
        libros = self.cursor.fetchall()
        
        # Crea objetos de productos y libros y los agrega al inventario
        for producto_data in productos:
            nombre, codigo, precio, cantidad = producto_data
            producto = Producto(nombre, int(codigo), precio, cantidad)
            self.lista_inventario.append(producto)

        
        for libro_data in libros:
            nombre, codigo, precio,cantidad, autor, genero, anio, num_paginas = libro_data
            libro = Libro(nombre, int(codigo), precio, int(cantidad), autor, genero, anio, num_paginas) 
            self.lista_inventario.append(libro)

    def __str__(self):
        for libro in self.lista_inventario:
            print(libro.codigo)
            print(type(libro.codigo))

    def eliminar_libro(self, codigo):
        self.cursor.execute('DELETE FROM Libro WHERE codigo = ?', (codigo,))
        self.conn.commit()
    
    def eliminar_producto(self, codigo):
        self.cursor.execute('DELETE FROM Producto WHERE codigo = ?', (codigo,))
        self.conn.commit()

class Venta:
    def __init__(self):
        self.articulos = []
        self.total = 0
        self.turno_asociado = 0
        self.conn = sqlite3.connect('libreria.db')
        self.cursor = self.conn.cursor()
    
    def agregar_venta(self,cantidad,codigo,inventario):
        for producto in inventario.lista_inventario:
            if producto.codigo == codigo:
                for i in range(cantidad):
                    print('agregado')
                    self.articulos.append(producto)
                    producto.cantidad -=1
                return producto
        

    def remover(self,art,unidades):
        for i in range(unidades):
            self.articulos.remove(art)
            art.cantidad += 1

    def calcular_total(self):
        self.total = 0
        for elemento in self.articulos:
            self.total += elemento.precio
        return self.total
    def __str__(self):
        nombres = ""
        for libros in self.articulos:
            nombres += libros.nombre + ", "
        return f"Articulos : {nombres} total: {self.total}"

    def insertar_venta(self):
        print(self.articulos)
        for articulo in self.articulos:
            self.cursor.execute('''
            INSERT INTO Ventas (codigo, nombre, turno_id)
            VALUES (?, ?, ?)''', (articulo.codigo, articulo.nombre, self.turno_asociado))
            self.conn.commit()



class Caja:
    def __init__(self,turno,vendedor):
        self.turno =  turno
        self.vendedor =  vendedor
        self.num_ventas = 0
        self.ventas =  []
        self.caja =  0
        self.conn = sqlite3.connect('libreria.db')
        self.cursor = self.conn.cursor()
        self.estado = False

    def crear_venta(self):
        venta = Venta()
        self.ventas.append(venta)
    def vender(self,venta):
        self.num_ventas += 1
        self.caja += venta.total
        self.ventas.append(venta)
        ventaNueva = Venta()
        self.ventas.append(ventaNueva)

    def reporte(self):
        for venta in self.ventas:
            print(venta)
    def abrir_caja(self,vendedor):
        self.estado = True
        self.turno +=1
        self.caja = 0
        self.vendedor = vendedor
        self.num_ventas =0
        self.ventas.clear()
    
    def cerrar_caja(self):
        self.estado = False

    
    def insertar_caja(self):
        self.cursor.execute('''
        INSERT INTO Caja (turno, vendedor, num_ventas, caja)
        VALUES (?, ?, ?, ?)''', (self.turno, self.vendedor, self.num_ventas, self.caja))
        self.conn.commit()





caja = Caja(0, "matias")


