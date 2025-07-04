import sqlite3

class DBManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        query_ip = '''
        CREATE TABLE IF NOT EXISTS ip_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            version INTEGER NOT NULL,
            path TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            UNIQUE(ip, path, line_number)
        );
        '''
        self.conn.execute(query_ip)
        
        # Create the hashes table for hash extraction results
        query_hash = '''
        CREATE TABLE IF NOT EXISTS hashes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_value TEXT NOT NULL,
            hash_type TEXT NOT NULL,
            path TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            UNIQUE(hash_value, path, line_number)
        );
        '''
        self.conn.execute(query_hash)
        self.conn.commit()

    def save_ip(self, ip_info):
        query = '''
        INSERT OR IGNORE INTO ip_addresses (ip, version, path, line_number)
        VALUES (?, ?, ?, ?)
        '''
        try:
            self.conn.execute(query, (
                ip_info['ip'],
                ip_info['version'],
                ip_info['path'],
                ip_info['line_number']
            ))
            self.conn.commit()
        except Exception:
            pass

    def save_hash(self, hash_info):
        query = '''
        INSERT OR IGNORE INTO hashes (hash_value, hash_type, path, line_number)
        VALUES (?, ?, ?, ?)
        '''
        try:
            self.conn.execute(query, (
                hash_info['hash_value'],
                hash_info['hash_type'],
                hash_info['path'],
                hash_info['line_number']
            ))
            self.conn.commit()
        except Exception:
            pass

    def fetch_all_ips(self):
        query = 'SELECT ip, version, path, line_number FROM ip_addresses ORDER BY path, line_number;'
        cursor = self.conn.execute(query)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()

    def clear_ips(self):
        """Delete all records from the ip_addresses table."""
        self.conn.execute('DELETE FROM ip_addresses;')
        self.conn.commit()

    def clear_hashes(self):
        """Delete all records from the hashes table."""
        self.conn.execute('DELETE FROM hashes;')
        self.conn.commit() 