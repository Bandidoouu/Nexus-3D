import sqlite3
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_name="inventario_materiales.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._migrate_db()

    def _create_tables(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS materiales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                categoria TEXT,
                stock REAL DEFAULT 0,
                precio_unitario REAL
            );
            CREATE TABLE IF NOT EXISTS historial_movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER,
                tipo_accion TEXT,
                cantidad REAL,
                fecha_hora TEXT,
                comentarios TEXT,
                FOREIGN KEY (material_id) REFERENCES materiales (id)
            );
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT,
                fecha TEXT,
                total REAL,
                estado TEXT DEFAULT 'Guardada'
            );
            CREATE TABLE IF NOT EXISTS cotizacion_detalles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cotizacion_id INTEGER,
                material_id INTEGER,
                cantidad REAL,
                precio_unitario REAL,
                costo_total REAL,
                FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones (id),
                FOREIGN KEY (material_id) REFERENCES materiales (id)
            );
            CREATE TABLE IF NOT EXISTS productos_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_producto TEXT,
                categoria TEXT,
                fecha TEXT,
                total_costo REAL
            );
            CREATE TABLE IF NOT EXISTS producto_stock_detalles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                material_id INTEGER,
                cantidad REAL,
                costo_total REAL,
                FOREIGN KEY (producto_id) REFERENCES productos_stock (id),
                FOREIGN KEY (material_id) REFERENCES materiales (id)
            );
        ''')
        self.conn.commit()

    def _migrate_db(self):
        for stmt in [
            "ALTER TABLE cotizaciones ADD COLUMN estado TEXT DEFAULT 'Guardada'",
        ]:
            try:
                self.cursor.execute(stmt)
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def registrar_movimiento(self, m_id, tipo, cant, nota=""):
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            'INSERT INTO historial_movimientos '
            '(material_id, tipo_accion, cantidad, fecha_hora, comentarios) VALUES (?, ?, ?, ?, ?)',
            (m_id, tipo, cant, ahora, nota)
        )
        self.conn.commit()

    def reset_database(self):
        for t in ['materiales', 'historial_movimientos', 'cotizaciones',
                  'cotizacion_detalles', 'productos_stock', 'producto_stock_detalles']:
            self.cursor.execute(f"DELETE FROM {t}")
        self.cursor.execute("DELETE FROM sqlite_sequence")
        self.conn.commit()

    def get_materiales(self):
        return self.cursor.execute(
            "SELECT id, nombre, categoria FROM materiales"
        ).fetchall()

    def get_material_by_id(self, m_id):
        return self.cursor.execute(
            "SELECT nombre, categoria, precio_unitario, descripcion FROM materiales WHERE id=?",
            (m_id,)
        ).fetchone()

    def get_stock(self, m_id):
        row = self.cursor.execute(
            "SELECT stock FROM materiales WHERE id=?", (m_id,)
        ).fetchone()
        return row[0] if row else 0

    def update_stock(self, m_id, delta):
        self.cursor.execute(
            "UPDATE materiales SET stock = stock + ? WHERE id = ?", (delta, m_id)
        )
        self.conn.commit()
