import sqlite3
import os

# =====================================================
# Database Functions
# =====================================================
def create_database(db_path):
    try:
        if not os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE connections (
                    name TEXT PRIMARY KEY,
                    path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    local_port INTEGER NOT NULL,
                    remote_ip TEXT NOT NULL,
                    remote_port INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    blacklisted INTEGER DEFAULT 0,
                    whitelisted INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            conn.close()
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

# =====================================================
# Functions for single connection operations
# =====================================================
def insert_connection(db_path, name, path, timestamp, local_port, remote_ip, remote_port, status, blacklisted=0, whitelisted=0):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO connections (name, path, timestamp, local_port, remote_ip, remote_port, status, blacklisted, whitelisted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, path, timestamp, local_port, remote_ip, remote_port, status, blacklisted, whitelisted))
    conn.commit()
    conn.close()

def update_connection(db_path, name, **kwargs):
    if connection_exists(db_path, name):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(name)
        sql = f"UPDATE connections SET {', '.join(fields)} WHERE name = ?"
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
    else:
        insert_connection(
            db_path,
            name,
            kwargs.get('path', ''),
            kwargs.get('timestamp', ''),
            kwargs.get('local_port', 0),
            kwargs.get('remote_ip', ''),
            kwargs.get('remote_port', 0),
            kwargs.get('status', ''),
            kwargs.get('blacklisted', 0),
            kwargs.get('whitelisted', 0)
        )


def connection_exists(db_path, name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM connections WHERE name = ?', (name,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def remove_connection(db_path, name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM connections WHERE name = ?', (name,))
    conn.commit()
    conn.close()

def get_connection(db_path, name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM connections WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()
    return row

# =====================================================
# Functions for fetching many connections
# =====================================================
def fetch_connections(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM connections')
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_blacklisted_connections(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM connections WHERE blacklisted = 1')
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_whitelisted_connections(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM connections WHERE whitelisted = 1')
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_suspicious_connections(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM connections WHERE blacklisted = 0 AND whitelisted = 0')
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_recent_connections(db_path, limit=10):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM connections ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# =====================================================
# Additional utility functions
# =====================================================
def count_connections(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM connections')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_blacklisted_connections(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM connections WHERE blacklisted = 1')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_whitelisted_connections(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM connections WHERE whitelisted = 1')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_suspicious_connections(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM connections WHERE blacklisted = 0 AND whitelisted = 0')
    count = cursor.fetchone()[0]
    conn.close()
    return count

# ====================================================
# Functions for importing/exporting connections
# ====================================================
def export_connections_to_csv(db_path, csv_path):
    import csv
    connections = fetch_connections(db_path)
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Timestamp', 'Local Port', 'Remote IP', 'Remote Port', 'Status', 'Blacklisted', 'Whitelisted'])
        for conn in connections:
            writer.writerow(conn)

def import_connections_from_csv(db_path, csv_path):
    import csv
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute('''
                INSERT INTO connections (timestamp, local_port, remote_ip, remote_port, status, blacklisted, whitelisted)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['Timestamp'], 
                int(row['Local Port']), 
                row['Remote IP'], 
                int(row['Remote Port']), 
                row['Status'], 
                int(row['Blacklisted']), 
                int(row['Whitelisted'])
            ))
    conn.commit()
    conn.close()