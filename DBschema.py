# -*- coding: utf-8 -*-
"""
Created on Sun May  3 11:40:21 2020

@author: maria
"""

from psycopg2 import (
        connect
        )

cleanup = (
        'DROP TABLE IF EXISTS users CASCADE',
        'DROP TABLE IF EXISTS data'
        )

commands = (
        """
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            user_name VARCHAR(255) UNIQUE NOT NULL,
            user_password VARCHAR(255) NOT NULL
        )
        """,
        """ 
        CREATE TABLE data (
                data_id SERIAL PRIMARY KEY,
                author_id INTEGER NOT NULL,
                created TIMESTAMP DEFAULT NOW(),
                species VARCHAR(350) NOT NULL,
                dieback INTEGER NOT NULL,
                diameter INTEGER NOT NULL,
                height INTEGER NOT NULL,
                FOREIGN KEY (author_id)
                    REFERENCES data (data_id)
        )
        """)
        
sqlCommand = (
        'INSERT INTO users (user_name, user_password) VALUES (%s, %s) RETURNING user_id',
        )

myFile = open('dbConfig.txt')
connStr = myFile.readline()
conn = connect(connStr)
cur = conn.cursor()
for command in cleanup :
    cur.execute(command)

for command in commands :
    cur.execute(command)

cur.execute(sqlCommand[0], ('marianna', 'marianna'))
cur.execute(sqlCommand[0], ('martina', 'martina'))
cur.execute(sqlCommand[0], ('gabriele', 'gabriele'))
cur.execute(sqlCommand[0], ('chiara', 'chiara'))
cur.execute('SELECT * FROM users')
print(cur.fetchall())

cur.close()
conn.commit()
conn.close()


