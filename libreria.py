import libreriaClases
from PyQt6 import uic, QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow,QTableWidgetItem, QAbstractItemView , QDialog, QMessageBox
from PyQt6.QtCore import QTime,QTimer
import sqlite3
import csv

#Todo, crear ventana que inicialice la caja y el inventario

inventario = libreriaClases.Inventario()

inventario.cargar_inventario_desde_bd()
inventario.cargar_cajas_desde_bd()

class Mi_Ventana(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ventanaPrincipal.ui',self)
        
        #Acomodamos las columnas de la tabla para que esten bien espaciadas
        tabla_ancho = self.tableWidget.width()
        self.tableWidget.setColumnWidth(0, int(tabla_ancho*(1/2)))
        self.tableWidget.setColumnWidth(1, int(tabla_ancho*(1/2)))
        self.tableWidget.setColumnWidth(2, int(tabla_ancho*(1/4)))
        self.tableWidget.setColumnWidth(3, int(tabla_ancho*(1/5)))
        self.tableWidget.setColumnWidth(4, int(tabla_ancho*(1/5)))
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)#Desabilita la edicion de las tablas

        self.cargar_inventarioL()#Cargamos el inventario en las tablas de inventario
        self.cargar_inventarioP()
        self.des_habilitar_ventas()

        #seniales para la venta
        self.codigo_barras.returnPressed.connect(self.agregar_producto_codigo)
        self.botonFinalizarVenta.clicked.connect(self.finalizar_venta)
        self.botonAnular.clicked.connect(self.anular_venta)
        self.botonEliminarArticulo.clicked.connect(self.remover_articulo)

        #seniales en los botones de menu
        self.abrirTurno.triggered.connect(self.abrir_caja)
        self.botonCierreCaja.triggered.connect(self.cierre_caja)
        self.botonRendicionCaja.triggered.connect(self.rendicion_caja)
        self.reporte_Ventas.triggered.connect(self.reporte_ventas)
        #ponemos la imagen de lupa como el icono del boton
        self.lupa.setIcon(QtGui.QIcon('lupo.png'))
        self.lupa.setIconSize(QtCore.QSize(self.lupa.width(),self.lupa.height()))


        #ventana buscar conectada a el input de nombre
        self.ventanaBusqueda = VentanaBuscar(self)
        self.nombre_producto.returnPressed.connect(self.buscar_producto)
        self.lupa.clicked.connect(self.buscar_producto)

        self.ventanaCierre = VentanaCierre()
        self.ventanaReporte = VentanaReportVentas()

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

        if inventario.lista_cajas[-1].estado:
            titulo = 'Recordatorio'
            cuerpo = 'Recuerde abrir una caja para proceder con las ventas'
            mensaje(titulo,cuerpo)

    def des_habilitar_ventas(self):
        if inventario.lista_cajas[-1].estado:
            self.principal.setTabEnabled(0,False) #deshabilita el tab con indice 0 
        else:
            self.principal.setTabEnabled(0,True)

    def BorrarLInventario(self):
        try:
            fila = self.tablaLibros.currentRow()
            codigo = self.tablaLibros.item(fila,0).text()
            inventario.eliminar_libro(codigo)
            self.cargar_inventarioL()
        except AttributeError:
                    titulo = 'Error'
                    cuerpo = 'Seleccione un Libro primero'
                    mensaje(titulo,cuerpo)
    
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
        except AttributeError:
            titulo = 'Error'
            cuerpo = 'Seleccione un libro primero'
            mensaje(titulo,cuerpo)

    def EditarPInventario(self):
        try:
            fila = self.tablaProductos.currentRow()
            codigo = self.tablaProductos.item(fila,0).text()
            nombre = self.tablaProductos.item(fila,1).text()
            precio = self.tablaProductos.item(fila,2).text()
            cantidad = self.tablaProductos.item(fila,3).text()

        

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
        except AttributeError:
                    titulo = 'Error'
                    cuerpo = 'Seleccione un Producto primero'
                    mensaje(titulo,cuerpo)
    def BorrarPInventario(self):
        try:
            fila = self.tablaProductos.currentRow()
            codigo = self.tablaProductos.item(fila,0).text()
            inventario.eliminar_producto(codigo)
            self.cargar_inventarioP()
        except AttributeError:
                    titulo = 'Error'
                    cuerpo = 'Seleccione un Producto primero'
                    mensaje(titulo,cuerpo)
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
            for producto_existente in inventario.lista_inventario:
                if codigo == producto_existente.codigo: 
                    mensaje('error','ese codigo ya existe')
                    self.ingreso_codigo.setText('')
                    return
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
            for producto_existente in inventario.lista_inventario:
                if codigo == producto_existente.codigo: 
                    mensaje('error','ese codigo ya existe')
                    self.ingreso_codigo.setText('')
                    return 
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
                        
    def abrir_caja(self):
        if inventario.lista_cajas[-1].estado:
            dialogo = DialogAperturaCaja()
            with open('stylesheet.qss','r') as file:
                dialogo.setStyleSheet(file.read())
            if(dialogo.exec()):
                datos= dialogo.get_datos()
                inventario.abrir_caja(int(datos[0]),datos[1])
                inventario.lista_cajas[-1].insertar_caja()
            
            self.des_habilitar_ventas()
        else:
            titulo = 'Error'
            cuerpo = 'Ya hay una caja abierta'
            mensaje(titulo,cuerpo)
    def cierre_caja(self):
        if inventario.lista_cajas[-1].estado:
            titulo = 'Error'
            cuerpo = 'La caja ya esta cerrada!'
            mensaje(titulo,cuerpo)
        else:
            inventario.lista_cajas[-1].estado = True
            titulo = 'Cierre'
            cuerpo = 'Caja cerrada!'
            mensaje(titulo,cuerpo)
            self.des_habilitar_ventas()
    def rendicion_caja(self):
        if inventario.lista_cajas[-1].estado:
            self.ventanaCierre.show()
            ingresos = str(inventario.lista_cajas[-1].calcular_ingresos())
            turno = str(inventario.lista_cajas[-1].turno)
            self.ventanaCierre.ingresosInput.setText(ingresos)
            self.ventanaCierre.numeroTurno.setText(turno)
        else:
            titulo = 'Error'
            cuerpo = 'Primero cierre la caja.'
            mensaje(titulo,cuerpo)
        

    def reporte_ventas(self):
        self.ventanaReporte.show()
        self.ventanaReporte.cargar_comboBox()

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
                titulo = 'Error'
                cuerpo = 'No existe un producto con ese codigo!'
                mensaje(titulo,cuerpo)
            except AttributeError:
                titulo = 'Error'
                cuerpo = 'No existe un producto con ese codigo!'
                mensaje(titulo,cuerpo)
    def remover_articulo(self):
        item = self.tableWidget.currentItem()
        if (item == None):
            return # no hacer nada si no hay un elemento seleccionado
        fila = item.row()
        totalArticulo = float(self.tableWidget.item(fila,4).text())
        total = float(self.total.text())
        total -= totalArticulo
        self.total.setText(str(total))
        self.tableWidget.removeRow(fila)


    def anular_venta(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.total.setText('0')


    def finalizar_venta(self):
        #Creamos un objeto venta al final de la lista ventas de caja
        if self.tableWidget.rowCount() == 0:
            return #el boton no hara nada si no hay ningun producto en la tabla
        
        inventario.lista_cajas[-1].crear_venta()
        for fila in range(self.tableWidget.rowCount()):
            codigo = self.tableWidget.item(fila,0).text()
            nombre = self.tableWidget.item(fila,1).text()
            precio = float(self.tableWidget.item(fila,2).text())
            cantidad = int(self.tableWidget.item(fila,3).text())
            inventario.lista_cajas[-1].ventas[-1].agregar_venta(codigo,nombre,precio,cantidad)#accedemos a la ultima venta de la caja y agregamos los productos a la venta
            inventario.actualizar_inventario_post_venta(codigo,cantidad)
        inventario.lista_cajas[-1].ventas[-1].insertar_venta()#guardamos la venta en la tabla ventas de la base de datos
        total = float(self.total.text())
        inventario.lista_cajas[-1].vender(total)#sumamos el total de la venta a la caja 
        inventario.lista_cajas[-1].Actualizar_Caja()#Guardamos los datos de la caja en caso de que el programa se cierre, asi mantendremos los datos
        self.cargar_inventarioL()#volvemos a cargar el inventario asi se ve reflejado en la tabla de inventario
        self.cargar_inventarioP()

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

class DialogAperturaCaja(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('aperturaCaja.ui',self)
        turno = inventario.lista_cajas[-1].turno
        turno +=1
        self.TurnoLabel.setText(str(turno))

    def get_datos(self):
        turno = self.TurnoLabel.text()
        cajero = self.CajeroInput.text()
        return turno,cajero

class VentanaCierre(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('cierre_caja.ui',self)
        validador = QtGui.QIntValidator(0, 10000000)
        self.dosmil.setValidator(validador)
        self.mil.setValidator(validador)
        self.quinientos.setValidator(validador)
        self.doscientos.setValidator(validador)
        self.cien.setValidator(validador)

        self.tarjetaInput.setValidator(validador)
        self.tranferenciasInput.setValidator(validador)
        self.retiroInput.setValidator(validador)
        self.egresosInput.setValidator(validador)

        self.dosmil.editingFinished.connect(self.efectivo)
        self.mil.editingFinished.connect(self.efectivo)
        self.quinientos.editingFinished.connect(self.efectivo)
        self.doscientos.editingFinished.connect(self.efectivo)
        self.cien.editingFinished.connect(self.efectivo)
        self.botonFinalizar.clicked.connect(self.finalizar)

    def efectivo(self):
        dossmil=int(self.dosmil.text())
        mill=int(self.mil.text())
        quinien=int(self.quinientos.text())
        doscie=int(self.doscientos.text())
        cienpe=int(self.cien.text())
        total1=str(dossmil*2000+mill*1000+quinien*500+doscie*200+cienpe*100)
        self.efectivoRendidoLabel.setText(total1)
    
    def finalizar(self):
        total = float(self.ingresosInput.text())
        turno = inventario.lista_cajas[-1].turno
        cajero = inventario.lista_cajas[-1].vendedor
        tarjetas = int(self.tarjetaInput.text())
        transferencias = int(self.tranferenciasInput.text())
        retiros = int(self.retiroInput.text())
        egresos = int(self.egresosInput.text())
        efectivoARendir = total - tarjetas - transferencias -egresos- retiros
        efectivoRendido = int(self.efectivoRendidoLabel.text()) 
        sobrante = efectivoRendido - efectivoARendir
        inventario.lista_cajas[-1].sobranteFaltante = sobrante 

        archivo = open('Reportes.csv', 'a', newline='')
        escritor_csv = csv.writer(archivo, delimiter=',', quotechar='"')

        # Escribir los datos
        escritor_csv.writerow([turno, cajero, total,tarjetas, transferencias, retiros,egresos, efectivoARendir, efectivoRendido,sobrante])
        # Cerrar archivo
        archivo.close()

        inventario.lista_cajas[-1].Actualizar_Caja()
        titulo = 'Cierre'
        cuerpo = 'Caja guardada correctamente'
        mensaje(titulo,cuerpo)
        
        self.close()

class VentanaReportVentas(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('reportVentas.ui',self)
        self.conn = sqlite3.connect('libreria.db')
        self.cursor = self.conn.cursor()
    
        self.botonCargar.clicked.connect(self.cargar_ventas)
        
    def cargar_comboBox(self):
        self.cursor.execute("SELECT * FROM Caja")
        resultados = self.cursor.fetchall()
        for resultado in resultados:
            texto = "Turno :" + str(resultado[1]) +" "+"Cajero: " + str(resultado[2])
            self.comboBox.addItem(texto)
    def cargar_ventas(self):
        #Limpiamos la tabla en caso de que ya se haya hecho una consulta previamente
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)

        indice = self.comboBox.currentIndex()
        indice +=1
        self.cursor.execute("SELECT * FROM Ventas WHERE turno_id = ?", (indice,))
        resultados = self.cursor.fetchall()
        for resultado in resultados:
            fila = self.tableWidget.rowCount()
            self.tableWidget.setRowCount(fila + 1)
            self.tableWidget.setItem(fila, 0, QTableWidgetItem(str(resultado[1])))
            self.tableWidget.setItem(fila, 1, QTableWidgetItem(str(resultado[2])))
            self.tableWidget.setItem(fila, 2, QTableWidgetItem(str(resultado[3])))
            self.tableWidget.setItem(fila, 3, QTableWidgetItem(str(resultado[4])))
            self.tableWidget.setItem(fila, 4, QTableWidgetItem(str(resultado[5])))

def mensaje(titulo,cuerpo):
    mensaje = QMessageBox()

    mensaje.setWindowTitle(titulo)
    mensaje.setText(cuerpo)


    mensaje.setIcon(QMessageBox.Icon.NoIcon)
    mensaje.setStandardButtons(QMessageBox.StandardButton.Ok)
    resultado = mensaje.exec()
app = QApplication([])

ventana = Mi_Ventana()
with open('stylesheet.qss','r') as file:
    ventana.setStyleSheet(file.read())
    ventana.ventanaBusqueda.setStyleSheet(file.read())
ventana.show()

app.exec()