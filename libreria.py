import libreriaClases
from PyQt6 import uic, QtGui, QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow,QTableWidgetItem, QAbstractItemView 
from PyQt6.QtCore import QTime,QTimer



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
        self.tableWidget.setColumnWidth(0, int(tabla_ancho*(1/4)))
        self.tableWidget.setColumnWidth(1, int(tabla_ancho*(2/5)))
        self.tableWidget.setColumnWidth(2, int(tabla_ancho*(1.85/17)))
        self.tableWidget.setColumnWidth(3, int(tabla_ancho*(2/17)))
        self.tableWidget.setColumnWidth(4, int(tabla_ancho*(2/16)))
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)#Desabilita la edicion de las tablas

        Caja01.crear_venta()#Provisorio para generar la venta actual
        self.cargar_inventarioL()#Cargamos el inventario
        self.cargar_inventarioP()

        self.codigo_barras.returnPressed.connect(self.agregar_producto_codigo)
        self.botonFinalizarVenta.clicked.connect(self.finalizar_venta)


        self.botonCierreCaja.clicked.connect(self.cierre_caja)
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
    def cierre_caja(self):
        self.ventanaCierre.show()

    def buscar_producto(self):
        texto = self.nombre_producto.text()
        self.ventanaBusqueda.show()
        self.ventanaBusqueda.buscar.setText(texto)
    def actualizar_hora(self):
        # Obtener la hora actual
        hora_actual = QTime.currentTime()

        # Mostrar la hora actual en el QLCDNumber
        self.lcdNumber.display(hora_actual.toString("hh:mm:ss"))
    
    def agregar_producto_codigo(self):
        indice = Caja01.num_ventas
        unidades = self.spinBox.value()
        codigo = int(self.codigo_barras.text())
        if unidades > 0:
            try:
                producto = Caja01.ventas[indice].agregar_venta(unidades,codigo,inventario)
                fila = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(fila + 1)
                self.tableWidget.setItem(fila, 0, QTableWidgetItem(str(producto.codigo)))
                self.tableWidget.setItem(fila, 1, QTableWidgetItem(producto.nombre))
                self.tableWidget.setItem(fila, 2, QTableWidgetItem(str(producto.precio)))
                self.tableWidget.setItem(fila, 3, QTableWidgetItem(str(unidades)))
                self.tableWidget.setItem(fila, 4, QTableWidgetItem(str(unidades*producto.precio)))
                total =Caja01.ventas[indice].calcular_total()
                self.total.setText(str(total))
            except AttributeError:
                print("No existe un producto con ese codigoaca")
    def finalizar_venta(self):
        indice = Caja01.num_ventas
        venta = Caja01.ventas[indice]
        venta.turno_asociado = Caja01.turno
        venta.insertar_venta()
        Caja01.vender(venta)
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




app = QApplication([])

ventana = Mi_Ventana()
ventana.show()

app.exec()