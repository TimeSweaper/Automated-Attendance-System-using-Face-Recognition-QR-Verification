# Database/DB_Conn.py
# Simple DB connection helper. Edit values or use environment variables.

import os

dbHost = os.getenv('DB_HOST', 'localhost')
dbPort = int(os.getenv('DB_PORT', '3306'))
dbUser = os.getenv('DB_USER', 'root')
dbPass = os.getenv('DB_PASS', 'Makub123')
dbName = os.getenv('DB_NAME', 'attendance_db')
