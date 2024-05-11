import datetime
current_date = datetime.date.today()
print(current_date)

from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import pyodbc
import datetime

import os
os.urandom(24)


app = Flask(__name__)
app.secret_key = os.urandom(24)


# Configure database connection
server = 'DESKTOP-PIKNNDF\SQLEXPRESS01'
database = 'todos'

driver = '{ODBC Driver 17 for SQL Server}'
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()


cursor.execute("SELECT * FROM task ORDER BY CASE priority WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 WHEN 'High' THEN 3 ELSE 4 END;")

tasks = cursor.fetchall()
sub = []
print(tasks)
