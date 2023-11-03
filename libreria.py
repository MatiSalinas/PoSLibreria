import libreriaClases
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow,QTableWidgetItem
from PyQt6.QtCore import QTime,QTimer
Caja01= libreriaClases.Caja(1,'Matias')
inventario = libreriaClases.Inventario()

inventario.agregar_inventario(libreriaClases.libro)
inventario.agregar_inventario(libreriaClases.libro2)
inventario.agregar_inventario(libreriaClases.libro3)
inventario.agregar_inventario(libreriaClases.libro4)
inventario.agregar_inventario(libreriaClases.libro5)
inventario.agregar_inventario(libreriaClases.libro6)

class Mi_Ventana(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ventanaPrincipal.ui',self)
        
        self.tableWidget.setColumnWidth(0, 156)
        self.tableWidget.setColumnWidth(1, 356)
        self.tableWidget.setColumnWidth(2, 200)
        self.tableWidget.setColumnWidth(3, 95)
        self.tableWidget.setColumnWidth(4, 95)
        
        Caja01.crear_venta()
        self.codigo_barras.returnPressed.connect(self.agregar_producto_codigo)
        self.lcdNumber.setDigitCount(8)  # Para mostrar una hora en formato HH:MM:SS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_hora)
        self.timer.start(1000)  # Actualizar cada segundo (1000 ms)

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
                self.tableWidget.setItem(fila, 4, QTableWidgetItem(str(unidades*producto.precio)))
                total =Caja01.ventas[indice].calcular_total()
                self.total.setText(str(total))
            except AttributeError:
                print("No existe un producto con ese codigo")

        

app = QApplication([])

ventana = Mi_Ventana()
ventana.show()

app.exec()