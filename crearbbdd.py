import sqlite3

# Conectar a la base de datos (creará el archivo de base de datos si no existe)
conn = sqlite3.connect('libreria.db')
cursor = conn.cursor()

# Crear la tabla Producto si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Producto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT UNIQUE NOT NULL,
        precio REAL NOT NULL,
        cantidad INTEGER NOT NULL
    )
''')

# Crear la tabla Libro si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Libro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT UNIQUE NOT NULL,
        precio REAL NOT NULL,
        cantidad INTEGER NOT NULL,
        autor TEXT NOT NULL,
        genero TEXT NOT NULL,
        anio INTEGER NOT NULL,
        num_paginas INTEGER NOT NULL
    )
''')

# Crear la tabla Ventas si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_articulo TEXT,
        nombre_articulo TEXT,
        precio_unitario REAL,
        cantidad_vendida INTEGER,
        total REAL NOT NULL,
        turno_id INTEGER NOT NULL
    )
''')

# Crear la tabla Caja si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Caja (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turno INTEGER NOT NULL,
        vendedor TEXT NOT NULL,
        num_ventas INTEGER NOT NULL,
        sobrante INTEGER NOT NULL,
        caja REAL NOT NULL,
        estado BIT DEFAULT 0
    )
''')

# Confirmar los cambios y cerrar la conexión
conn.commit()
conn.close()