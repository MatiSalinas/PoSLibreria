import libreriaClases
from PyQt6 import uic, QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow,QTableWidgetItem, QAbstractItemView , QDialog
from PyQt6.QtCore import QTime,QTimer
import sys


#Todo, crear ventana que inicialice la caja y el inventario
Caja01= libreriaClases.Caja(1,'Matias')
inventario = libreriaClases.Inventario()
inventario.cargar_inventario_desde_bd()

class Mi_Ventana(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ventanaPrincipal.ui',self)
        
        #Acomodamos las columnas de la tabla para que esten bien espaciadas
        tabla_ancho = self.tableWidget.width()
        print(tabla_ancho)
        self.tableWidget.setColumnWidth(0, int(tabla_ancho*(1/2)))
        self.tableWidget.setColumnWidth(1, int(tabla_ancho*(1/2)))
        self.tableWidget.setColumnWidth(2, int(tabla_ancho*(1/4)))
        self.tableWidget.setColumnWidth(3, int(tabla_ancho*(1/5)))
        self.tableWidget.setColumnWidth(4, int(tabla_ancho*(1/5)))
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)#Desabilita la edicion de las tablas

        self.cargar_inventarioL()#Cargamos el inventario
        self.cargar_inventarioP()

        #seniales para la venta
        self.codigo_barras.returnPressed.connect(self.agregar_producto_codigo)
        self.botonFinalizarVenta.clicked.connect(self.finalizar_venta)
        self.botonAnular.clicked.connect(self.anular_venta)
        self.botonEliminarArticulo.clicked.connect(self.remover_articulo)

        self.botonCierreCaja.triggered.connect(self.cierre_caja)
        #ponemos la imagen de lupa como el icono del boton
        self.lupa.setIcon(QtGui.QIcon('lupo.png'))
        self.lupa.setIconSize(QtCore.QSize(self.lupa.width(),self.lupa.height()))


        ##ventana buscar conectada a el input de nombre
        self.ventanaBusqueda = VentanaBuscar(self)
        self.nombre_producto.returnPressed.connect(self.buscar_producto)
        self.lupa.clicked.connect(self.buscar_producto)

        self.ventanaCierre = CierreCaja()

        #RELOJ
        self.lcdNumber.setDigitCount(8)  # Para mostrar una hora en formato HH:MM:SS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_hora)
        self.timer.start(1000)  # Actualizar cada segundo (1000 ms)


        #Compras
        self.rb_crearLibro.toggled.connect(self.ComprasRadio)
        self.rb_CrearProducto.toggled.connect(self.ComprasRadio)
        self.rb_entradaLibro.toggled.connect(self.ComprasRadio)
        self.rb_entradaProducto.toggled.connect(self.ComprasRadio)
        self.ingreso_codigo.returnPressed.connect(self.cargar_compras_codigo)
        self.botonGuardarCompras.clicked.connect(self.guardar_compra)

        #Inventario
        self.InventarioLBorrar.clicked.connect(self.BorrarLInventario)
        self.InventarioPBorrar.clicked.connect(self.BorrarPInventario)
        self.InventarioLEditar.clicked.connect(self.EditarLInventario)
        self.InventarioPEditar.clicked.connect(self.EditarPInventario)

    def BorrarLInventario(self):
        fila = self.tablaLibros.currentRow()
        codigo = self.tablaLibros.item(fila,0).text()
        inventario.eliminar_libro(codigo)
        self.cargar_inventarioL()
    
    def EditarLInventario(self):
        try:
            fila = self.tablaLibros.currentRow()
            codigo = self.tablaLibros.item(fila,0).text()
            nombre = self.tablaLibros.item(fila,1).text()
            precio = self.tablaLibros.item(fila,2).text()
            cantidad = self.tablaLibros.item(fila,3).text()
            autor = self.tablaLibros.item(fila,4).text()
            genero = self.tablaLibros.item(fila,5).text()
            anio = self.tablaLibros.item(fila,6).text()
            num = self.tablaLibros.item(fila,7).text()
        except AttributeError:
            print("selecciona un libro primero")

        dialogo = DialogEditarLibro(codigo,nombre,precio,cantidad,autor,genero,anio,num)
        with open('stylesheet.qss','r') as file:
            dialogo.setStyleSheet(file.read())
        if(dialogo.exec()):
            nuevos_datos= dialogo.get_datos()
            codigo = int(nuevos_datos[0])
            nombre = nuevos_datos[1]
            precio = float(nuevos_datos[2])
            cantidad = int(nuevos_datos[3])
            autor = nuevos_datos[4]
            genero = nuevos_datos[5]
            anio = int(nuevos_datos[6])
            num = int(nuevos_datos[7])
            for productos_existentes in inventario.lista_inventario:
                if str(productos_existentes.codigo) == str(codigo):

                    productos_existentes.editar(nombre,precio,cantidad,autor,genero,anio,num)
                    productos_existentes.editar_tabla(nombre,precio,cantidad,autor,genero,anio,num)
                    self.cargar_inventarioL()

    def EditarPInventario(self):
        try:
            fila = self.tablaProductos.currentRow()
            codigo = self.tablaProductos.item(fila,0).text()
            nombre = self.tablaProductos.item(fila,1).text()
            precio = self.tablaProductos.item(fila,2).text()
            cantidad = self.tablaProductos.item(fila,3).text()

        except AttributeError:
            print("selecciona un Producto primero")

        dialogo = DialogEditarProducto(codigo,nombre,precio,cantidad)
        with open('stylesheet.qss','r') as file:
            dialogo.setStyleSheet(file.read())
        if(dialogo.exec()):
            nuevos_datos= dialogo.get_datos()
            codigo = int(nuevos_datos[0])
            nombre = nuevos_datos[1]
            precio = float(nuevos_datos[2])
            cantidad = int(nuevos_datos[3])

            for productos_existentes in inventario.lista_inventario:
                if str(productos_existentes.codigo) == str(codigo):

                    productos_existentes.editar(nombre,precio,cantidad)
                    productos_existentes.editar_tabla(nombre,precio,cantidad)
                    self.cargar_inventarioP()

    def BorrarPInventario(self):
        fila = self.tablaProductos.currentRow()
        codigo = self.tablaProductos.item(fila,0).text()
        inventario.eliminar_producto(codigo)
        self.cargar_inventarioP()
    def ComprasRadio(self):
        #Desactivamos o activamos los campos necesarios para cada opcion
        if self.rb_crearLibro.isChecked():
            self.ingreso_nombre.setEnabled(True)
            self.ingreso_precio.setEnabled(True)
            self.ingreso_cantidad.setEnabled(True)
            self.ingreso_genero.setEnabled(True)
            self.ingreso_paginas.setEnabled(True)
            self.ingreso_anio.setEnabled(True)
            self.ingreso_autor.setEnabled(True)
            
        if self.rb_CrearProducto.isChecked():
            self.ingreso_nombre.setEnabled(True)
            self.ingreso_precio.setEnabled(True)
            self.ingreso_cantidad.setEnabled(True)
            self.ingreso_genero.setEnabled(False)
            self.ingreso_paginas.setEnabled(False)
            self.ingreso_anio.setEnabled(False)
            self.ingreso_autor.setEnabled(False)
        if self.rb_entradaLibro.isChecked():
            self.ingreso_nombre.setEnabled(False)
            self.ingreso_precio.setEnabled(False)
            self.ingreso_cantidad.setEnabled(True)
            self.ingreso_genero.setEnabled(False)
            self.ingreso_paginas.setEnabled(False)
            self.ingreso_anio.setEnabled(False)
            self.ingreso_autor.setEnabled(False)
        if self.rb_entradaProducto.isChecked():
            self.ingreso_nombre.setEnabled(False)
            self.ingreso_precio.setEnabled(False)
            self.ingreso_cantidad.setEnabled(True)
            self.ingreso_genero.setEnabled(False)
            self.ingreso_paginas.setEnabled(False)
            self.ingreso_anio.setEnabled(False)
            self.ingreso_autor.setEnabled(False)

    def cargar_compras_codigo(self):
        codigo = self.ingreso_codigo.text()
        if self.rb_crearLibro.isChecked():
            pass
            
        if self.rb_CrearProducto.isChecked():
            pass
        if self.rb_entradaLibro.isChecked():
            for producto_existente in inventario.lista_inventario:

                if codigo == str(producto_existente.codigo) and type(producto_existente)==libreriaClases.Libro:
                    self.ingreso_nombre.setText(producto_existente.nombre)
                    self.ingreso_precio.setText(str(producto_existente.precio))
                    self.ingreso_genero.setText(producto_existente.genero)
                    self.ingreso_paginas.setText(str(producto_existente.num_paginas))
                    self.ingreso_anio.setText(str(producto_existente.anio))
                    self.ingreso_autor.setText(producto_existente.autor)
        if self.rb_entradaProducto.isChecked():
            for producto_existente in inventario.lista_inventario:
                if codigo == str(producto_existente.codigo) and type(producto_existente)==libreriaClases.Producto:
                    self.ingreso_nombre.setText(producto_existente.nombre)
                    self.ingreso_precio.setText(str(producto_existente.precio))
    
    def guardar_compra(self):
        def limpiar():
            self.ingreso_codigo.setText('')
            self.ingreso_nombre.setText('')
            self.ingreso_precio.setText('')
            self.ingreso_cantidad.setText('')
            self.ingreso_genero.setText('')
            self.ingreso_paginas.setText('')
            self.ingreso_anio.setText('')
            self.ingreso_autor.setText('')
        if self.rb_crearLibro.isChecked():
            codigo =int(self.ingreso_codigo.text())
            nombre = self.ingreso_nombre.text()
            precio = float(self.ingreso_precio.text())
            cantidad = int(self.ingreso_cantidad.text())
            genero = self.ingreso_genero.text()
            paginas =self.ingreso_paginas.text()
            anio =self.ingreso_anio.text()
            autor =self.ingreso_autor.text()
            libroNuevo = libreriaClases.Libro(nombre,codigo,precio,cantidad,autor,genero,anio,paginas)
            inventario.lista_inventario.append(libroNuevo)
            libroNuevo.insertar_libro()
            self.cargar_inventarioL()
            limpiar()
            
        if self.rb_CrearProducto.isChecked():
            codigo =int(self.ingreso_codigo.text())
            nombre = self.ingreso_nombre.text()
            precio = float(self.ingreso_precio.text())
            cantidad = int(self.ingreso_cantidad.text())
            productoNuevo = libreriaClases.Producto(nombre,codigo,precio,cantidad)
            inventario.lista_inventario.append(productoNuevo)
            productoNuevo.insertar_producto()
            self.cargar_inventarioP()
            limpiar()
        if self.rb_entradaLibro.isChecked():
            codigo =int(self.ingreso_codigo.text())
            for producto_existente in inventario.lista_inventario:
                if str(codigo) == str(producto_existente.codigo) and type(producto_existente)==libreriaClases.Libro:
                    cantidad = int(self.ingreso_cantidad.text()) + producto_existente.cantidad
                    producto_existente.cantidad += int(self.ingreso_cantidad.text())
                    producto_existente.editar_tabla(producto_existente.nombre,producto_existente.precio,cantidad,producto_existente.autor,producto_existente.genero,producto_existente.anio,producto_existente.num_paginas)
                    limpiar()
                    self.cargar_inventarioL()
        if self.rb_entradaProducto.isChecked():
            codigo =int(self.ingreso_codigo.text())
            for producto_existente in inventario.lista_inventario:
                if str(codigo) == str(producto_existente.codigo) and type(producto_existente)==libreriaClases.Producto:
                    cantidad = int(self.ingreso_cantidad.text()) + producto_existente.cantidad
                    producto_existente.cantidad += int(self.ingreso_cantidad.text())
                    producto_existente.editar_tabla(producto_existente.nombre,producto_existente.precio,cantidad)
                    limpiar()
                    self.cargar_inventarioP()


    def cierre_caja(self):
        self.ventanaCierre.show()

    def buscar_producto(self):
        with open('stylesheet.qss','r') as file:
            ventana.ventanaBusqueda.setStyleSheet(file.read())

        texto = self.nombre_producto.text()
        self.ventanaBusqueda.show()
        self.ventanaBusqueda.buscar.setText(texto)
    def actualizar_hora(self):
        # Obtener la hora actual
        hora_actual = QTime.currentTime()

        # Mostrar la hora actual en el QLCDNumber
        self.lcdNumber.display(hora_actual.toString("hh:mm:ss"))
    
    def agregar_producto_codigo(self):
        
        unidades = self.spinBox.value()
        codigo = int(self.codigo_barras.text())
        if unidades > 0:
            try:
                for producto_existente in inventario.lista_inventario:
                    if codigo == producto_existente.codigo:
                        fila = self.tableWidget.rowCount()
                        self.tableWidget.setRowCount(fila + 1)
                        self.tableWidget.setItem(fila, 0, QTableWidgetItem(str(producto_existente.codigo)))
                        self.tableWidget.setItem(fila, 1, QTableWidgetItem(producto_existente.nombre))
                        self.tableWidget.setItem(fila, 2, QTableWidgetItem(str(producto_existente.precio)))
                        self.tableWidget.setItem(fila, 3, QTableWidgetItem(str(unidades)))
                        self.tableWidget.setItem(fila, 4, QTableWidgetItem(str(unidades*producto_existente.precio)))
                        total =producto_existente.precio* unidades + float(self.total.text())
                        self.total.setText(str(total))

                        #Limpiamos los Qlineedit y spinbox
                        self.codigo_barras.setText('')
                        self.spinBox.setValue(1)
                        return 0
                print("No existe un producto con ese codigo")
            except AttributeError:
                print("No existe un producto con ese codigo")
    def remover_articulo(self):
        item = self.tableWidget.currentItem()
        if (item == None):
            return
        fila = item.row()
        self.tableWidget.removeRow(fila)

    def anular_venta(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.total.setText('0')
    def finalizar_venta(self):
        #Creamos un objeto venta al final de la lista ventas de caja
        if self.tableWidget.rowCount() == 0:
            return
        
        print(Caja01.ventas)
        Caja01.crear_venta()
        print(Caja01.ventas)
        print(self.tableWidget.rowCount(),'porongaaaa')
        for fila in range(self.tableWidget.rowCount()):
            print('poronguita')
            codigo = self.tableWidget.item(fila,0).text()
            nombre = self.tableWidget.item(fila,1).text()
            precio = float(self.tableWidget.item(fila,2).text())
            cantidad = int(self.tableWidget.item(fila,3).text())
            Caja01.ventas[-1].agregar_venta(codigo,nombre,precio,cantidad)#accedemos a la ultima venta de la caja y agregamos los productos a la venta
        
        Caja01.ventas[-1].insertar_venta()
        total = float(self.total.text())
        Caja01.vender(total)
        Caja01.crear_venta()
        print(Caja01.ventas)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.total.setText('0')

    def cargar_inventarioL(self):
        #Todo 
        #re size las columnas asi ocupan toda la tabla
        fila = 0
        self.tablaLibros.setRowCount(fila)
        for item in inventario.lista_inventario:
            if type(item) == libreriaClases.Libro:
                fila = self.tablaLibros.rowCount()
                self.tablaLibros.setRowCount(fila + 1)
                self.tablaLibros.setItem(fila, 0, QTableWidgetItem(str(item.codigo)))
                self.tablaLibros.setItem(fila, 1, QTableWidgetItem(item.nombre))
                self.tablaLibros.setItem(fila, 2, QTableWidgetItem(str(item.precio)))
                self.tablaLibros.setItem(fila, 3, QTableWidgetItem(str(item.cantidad)))
                self.tablaLibros.setItem(fila, 4, QTableWidgetItem(str(item.autor)))
                self.tablaLibros.setItem(fila, 5, QTableWidgetItem(str(item.genero)))
                self.tablaLibros.setItem(fila, 6, QTableWidgetItem(str(item.anio)))
                self.tablaLibros.setItem(fila, 7, QTableWidgetItem(str(item.num_paginas)))
    def cargar_inventarioP(self):
        #Todo
        #re size las columnas asi ocupan toda la tabla
        fila = 0
        self.tablaProductos.setRowCount(fila)
        for item in inventario.lista_inventario:
            if type(item) == libreriaClases.Producto:
                fila = self.tablaProductos.rowCount()
                self.tablaProductos.setRowCount(fila + 1)
                self.tablaProductos.setItem(fila, 0, QTableWidgetItem(str(item.codigo)))
                self.tablaProductos.setItem(fila, 1, QTableWidgetItem(item.nombre))
                self.tablaProductos.setItem(fila, 2, QTableWidgetItem(str(item.precio)))
                self.tablaProductos.setItem(fila, 3, QTableWidgetItem(str(item.cantidad)))
class VentanaBuscar(QMainWindow):
    def __init__(self,padre):
        super().__init__()
        uic.loadUi('ventanabuscar.ui',self)
        self.padre = padre
        self.lista_aux = []
        self.tablaBuscar.setColumnWidth(0, 156)
        self.tablaBuscar.setColumnWidth(1, 500)
        self.tablaBuscar.setColumnWidth(2, 156)
        self.tablaBuscar.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)#Desabilita la edicion de las tablas
        self.buscar.textChanged.connect(self.filtrar)
        self.tablaBuscar.itemActivated.connect(self.elegir_producto)


    def elegir_producto(self):
        fila = self.tablaBuscar.currentRow()
        codigo = self.tablaBuscar.item(fila,0).text()
        self.padre.ventanaBusqueda.close()
        self.padre.codigo_barras.setText(codigo)
        self.padre.agregar_producto_codigo()
    def filtrar(self):
        self.tablaBuscar.clearContents()
        fila = 0
        self.tablaBuscar.setRowCount(fila)
        for item in inventario.lista_inventario:
            if self.buscar.text().lower() in item.nombre.lower():
                fila = self.tablaBuscar.rowCount()
                self.tablaBuscar.setRowCount(fila + 1)
                self.tablaBuscar.setItem(fila, 0, QTableWidgetItem(str(item.codigo)))
                self.tablaBuscar.setItem(fila, 1, QTableWidgetItem(item.nombre))
                self.tablaBuscar.setItem(fila, 2, QTableWidgetItem(str(item.precio)))



class CierreCaja(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('cierre_caja.ui',self)

class DialogEditarLibro(QDialog):
    def __init__(self,codigoActual,nombreActual,precioActual,cantidadActual,autorActual,generoActual,anioActual,numActual):
        super().__init__()
        uic.loadUi('QdialogLibro.ui',self)
        self.CodigoInput.setText(codigoActual)
        self.NombreInput.setText(nombreActual)
        self.PrecioInput.setText(precioActual)
        self.CantidadInput.setText(cantidadActual)
        self.AutorInput.setText(autorActual)
        self.GeneroInput.setText(generoActual)
        self.AnioInput.setText(anioActual)
        self.NumInput.setText(numActual)
        



    def get_datos(self):
        codigo = self.CodigoInput.text()
        Nombre = self.NombreInput.text()
        Precio = self.PrecioInput.text()
        Cantidad = self.CantidadInput.text()
        Autor = self.AutorInput.text()
        Genero = self.GeneroInput.text()
        Anio = self.AnioInput.text()
        Num = self.NumInput.text()

        return codigo,Nombre,Precio,Cantidad,Autor,Genero,Anio,Num

class DialogEditarProducto(QDialog):
    def __init__(self,codigoActual,nombreActual,precioActual,cantidadActual):
        super().__init__()
        uic.loadUi('QdialogProducto.ui',self)
        self.CodigoInput.setText(codigoActual)
        self.NombreInput.setText(nombreActual)
        self.PrecioInput.setText(precioActual)
        self.CantidadInput.setText(cantidadActual)




    def get_datos(self):
        codigo = self.CodigoInput.text()
        Nombre = self.NombreInput.text()
        Precio = self.PrecioInput.text()
        Cantidad = self.CantidadInput.text()

        return codigo,Nombre,Precio,Cantidad




app = QApplication([])

ventana = Mi_Ventana()
with open('stylesheet.qss','r') as file:
    ventana.setStyleSheet(file.read())
    ventana.ventanaBusqueda.setStyleSheet(file.read())
ventana.show()

app.exec()