from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QCheckBox, QPushButton, QLabel, QMessageBox)
from PyQt5.QtCore import Qt as QtCore, QCoreApplication
import sqlite3
import sys

class PermisosAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Administrar Permisos de Cajero")
        self.setGeometry(100, 100, 400, 500)
        
        # Widget y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Título
        titulo = QLabel("Permisos del Cajero")
        titulo.setAlignment(QtCore.AlignCenter)
        layout.addWidget(titulo)
        
        # Checkboxes para permisos
        self.permisos = {
            'ventas': QCheckBox('Acceso a Ventas'),
            'clientes': QCheckBox('Gestión de Clientes'),
            'inventario': QCheckBox('Ver Inventario'),
            'reportes': QCheckBox('Ver Reportes Básicos'),
            'ordenes': QCheckBox('Gestión de Órdenes')
        }
        
        # Agregar checkboxes al layout
        for checkbox in self.permisos.values():
            layout.addWidget(checkbox)
            
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton('Guardar Cambios')
        self.btn_cancelar = QPushButton('Cancelar')
        
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)
        
        # Conectar señales
        self.btn_guardar.clicked.connect(self.guardar_permisos)
        self.btn_cancelar.clicked.connect(self.close)
        
        # Cargar permisos actuales
        self.cargar_permisos()
        
    def cargar_permisos(self):
        try:
            conn = sqlite3.connect('lavanderia.db')
            cursor = conn.cursor()
            
            # Obtener permisos actuales de la base de datos
            cursor.execute("SELECT modulo, permitido FROM permisos_cajero")
            permisos_actuales = cursor.fetchall()
            
            # Actualizar checkboxes
            for modulo, permitido in permisos_actuales:
                if modulo in self.permisos:
                    self.permisos[modulo].setChecked(bool(permitido))
                    
            conn.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al cargar permisos: {str(e)}")
    
    def guardar_permisos(self):
        try:
            conn = sqlite3.connect('lavanderia.db')
            cursor = conn.cursor()
            
            # Actualizar permisos en la base de datos
            for modulo, checkbox in self.permisos.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO permisos_cajero (modulo, permitido)
                    VALUES (?, ?)
                """, (modulo, 1 if checkbox.isChecked() else 0))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Permisos actualizados correctamente")
            self.close()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Error al guardar permisos: {str(e)}")

if __name__ == '__main__':
    app = QCoreApplication(sys.argv)
    window = PermisosAdmin()
    window.show()
    sys.exit(app.exec_())