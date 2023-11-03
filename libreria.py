#Grupo 19 libreria


#TO DO
#interfaz grafica para el programa
#vincular con base de datos 

class Producto:
    def __init__(self,nombre,codigo,precio,cantidad):
        self.nombre = nombre
        self.codigo = codigo
        self.precio = precio
        self.cantidad = cantidad

class Libro(Producto):
    def __init__(self,nombre,codigo,precio,cantidad,autor,genero,anio,num_paginas):
        super().__init__(nombre,codigo,precio,cantidad)
        self.autor = autor
        self.genero = genero
        self.anio = anio
        self.num_paginas = num_paginas

    def __str__(self):
        return f"{self.nombre} {self.precio}"

class Inventario:
    def __init__(self):
        self.lista_inventario= []

    def agregar_inventario(self,producto):
        self.lista_inventario.append(producto)
class Venta:
    def __init__(self):
        self.articulos = []
        self.total = 0
    
    def agregar_venta(self,codigo,inventario):
        for producto in inventario:
            if producto.codigo == codigo:
                self.articulos.append(producto)
                producto.cantidad -=1

    def remover(self,art):
        self.articulos.remove(art)
        self.total -= art.precio
        art.cantidad += 1
    
    def __str__(self):
        nombres = ""
        for libros in self.articulos:
            nombres += libros.nombre + ", "
        return f"Articulos : {nombres} total: {self.total}"



class Caja:
    def __init__(self,turno,vendedor):
        self.turno =  turno
        self.vendedor =  vendedor
        self.num_ventas = 0
        self.ventas =  []
        self.caja =  0

    def vender(self,venta):
        self.num_ventas += 1
        self.caja += venta.total
        self.ventas.append(venta)

    def reporte(self):
        for venta in self.ventas:
            print(venta)



libro = Libro('Harry potter 1',83123213,2,100,'jk','ficcion',2020,200)

libro2 = Libro('Harry potter 2',83123213,2,100,'jk','ficcion',2020,200)

libro3 = Libro('Harry potter 3',83123213,2,100,'jk','ficcion',2020,200)

libro4 = Libro('Harry potter 4',83123213,2,100,'jk','ficcion',2020,200)

libro5 = Libro('Harry potter 5',83123213,2,100,'jk','ficcion',2020,200)

libro6 = Libro('Morro',83123213,2,100,'el mismo morro','comedia',2020,200)

caja = Caja(0, "matias")


print(venta1)
print(venta2)
