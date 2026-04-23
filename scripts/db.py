import sqlite3, os
from scripts import utils

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def _get_connection(self): # 
        # Establish connection. Reusing a single connection per thread
        # is recommended for performance [13].
        return sqlite3.connect(self.db_path)

    def execute_query(self, query, params=()):
        """Execute INSERT/UPDATE/DELETE queries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def fetch_all(self, query, params=()):
        """Fetch all results for a SELECT query."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def create_table(self, table_name, schema): # schema should be a string like "id INTEGER PRIMARY KEY, name TEXT"
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema});"
        self.execute_query(query)

local_path = str(os.getenv('APPDATA') or os.path.expanduser('~'))
install_path = os.path.join(local_path, "ProjectObsidian")
db_path = os.path.join(install_path, "connections.db")
db = DatabaseManager(db_path)

# =====================================================
# Utility Functions
# =====================================================
def convert_to_dict(row):
    if row is None:
        return None
    columns = ['key', 'name', 'path', 'timestamp', 'pid', 'local_port', 'remote_ip', 'remote_port', 'status', 'blacklisted', 'whitelisted']
    return {columns[i]: row[i] for i in range(len(columns))}

# =====================================================
# Database Functions
# =====================================================
def create_database(db_path):
    try:
        if not os.path.exists(db_path):
            db.create_table('connections', '''
                key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                pid INTEGER,
                local_port INTEGER NOT NULL,
                remote_ip TEXT NOT NULL,
                remote_port INTEGER NOT NULL,
                status TEXT NOT NULL,
                blacklisted INTEGER DEFAULT 0,
                whitelisted INTEGER DEFAULT 0
            ''')
            db._get_connection().execute('PRAGMA journal_mode=WAL;')
            journal_mode = db._get_connection().execute('PRAGMA journal_mode').fetchone()[0]
            utils.log_debug(f"Journal mode set to: {journal_mode}")
            return f"Database created at: {db_path}", True
        else:
            return f"Database already exists at: {db_path}", True
    except Exception as e:
        return f"Error creating database: {str(e)}", False

def delete_database(db_path):
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            return f"Database deleted at: {db_path}", True
        else:
            return f"No database found at: {db_path}", False
    except Exception as e:
        return f"Error deleting database: {str(e)}", False

def clear_zero_pid_connections():
    try:
        db.execute_query('DELETE FROM connections WHERE pid = 0')
        return "Zero PID connections cleared.", True
    except Exception as e:
        return f"Error clearing zero PID connections: {str(e)}", False

# =====================================================
# Functions for single connection operations
# =====================================================
def insert_connection(key, name, path, timestamp, pid, local_port, remote_ip, remote_port, status, blacklisted=0, whitelisted=0):
    db.execute_query('''
        INSERT INTO connections (key, name, path, timestamp, pid, local_port, remote_ip, remote_port, status, blacklisted, whitelisted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (key, name, path, timestamp, pid, local_port, remote_ip, remote_port, status, blacklisted, whitelisted))

def update_connection(key, **kwargs):
    if connection_exists(key):
        fields = []
        values = []
        for k, value in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(value)
        values.append(key)
        db.execute_query(f"UPDATE connections SET {', '.join(fields)} WHERE key = ?", values)
    else:
        insert_connection(
            key,
            kwargs.get('name', ''),
            kwargs.get('path', ''),
            kwargs.get('timestamp', ''),
            kwargs.get('pid', 0),
            kwargs.get('local_port', 0),
            kwargs.get('remote_ip', ''),
            kwargs.get('remote_port', 0),
            kwargs.get('status', ''),
            kwargs.get('blacklisted', 0),
            kwargs.get('whitelisted', 0)
        )


def connection_exists(key):
    return bool(db.fetch_all('SELECT 1 FROM connections WHERE key = ?', (key,)))

def remove_connection(key):
    db.execute_query('DELETE FROM connections WHERE key = ?', (key,))

def get_connection(key):
    result = db.fetch_all('SELECT * FROM connections WHERE key = ?', (key,))
    return result[0] if result else None

# =====================================================
# Functions for fetching many connections
# =====================================================
def fetch_connections():
    return db.fetch_all('SELECT * FROM connections')

def fetch_blacklisted_connections():
    return db.fetch_all('SELECT * FROM connections WHERE blacklisted = 1')

def fetch_whitelisted_connections():
    return db.fetch_all('SELECT * FROM connections WHERE whitelisted = 1')

def fetch_suspicious_connections():
    return db.fetch_all('SELECT * FROM connections WHERE blacklisted = 0 AND whitelisted = 0')

def fetch_recent_connections(limit=10):
    return db.fetch_all('SELECT * FROM connections ORDER BY timestamp DESC LIMIT ?', (limit,))

# =====================================================
# Additional utility functions
# =====================================================
def count_connections():
    return db.fetch_all('SELECT COUNT(*) FROM connections')[0][0]

def count_blacklisted_connections():
    return db.fetch_all('SELECT COUNT(*) FROM connections WHERE blacklisted = 1')[0][0]

def count_whitelisted_connections():
    return db.fetch_all('SELECT COUNT(*) FROM connections WHERE whitelisted = 1')[0][0]

def count_suspicious_connections():
    return db.fetch_all('SELECT COUNT(*) FROM connections WHERE blacklisted = 0 AND whitelisted = 0')[0][0]

# ====================================================
# Functions for importing/exporting connections
# ====================================================
def export_connections_to_csv(path):
    import csv
    csv_path = os.path.join(path, f"connections_export_{utils.get_date()}.csv")
    connections = fetch_connections()
    with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Key", "Name", "Path", "Remote IP", "Remote Port", "Local Port", "PID", "Status", "Blacklisted", "Whitelisted", "Timestamp"])
            for conn in connections:
                conn_dict = convert_to_dict(conn)
                if conn_dict:
                    writer.writerow([
                        conn_dict["key"],
                        conn_dict["name"],
                        conn_dict["path"],
                        conn_dict["remote_ip"],
                        conn_dict["remote_port"],
                        conn_dict["local_port"],
                        conn_dict["pid"],
                        conn_dict["status"],
                        conn_dict["blacklisted"],
                        conn_dict["whitelisted"],
                        conn_dict["timestamp"]
                    ])
            
def import_connections_from_csv(csv_path):
    import csv
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            update_connection(
                key=row['Path'] + str(row['Remote IP']) + str(row['Remote Port']),   
                name=row['Name'],
                path=row['Path'],
                timestamp=row['Timestamp'], 
                pid=int(row['PID']), 
                local_port=int(row['Local Port']), 
                remote_ip=row['Remote IP'], 
                remote_port=int(row['Remote Port']), 
                status=row['Status'], 
                blacklisted=int(row['Blacklisted']), 
                whitelisted=int(row['Whitelisted'])
            )