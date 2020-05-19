# -*- coding: utf-8 -*-
"""
Created on Fri May 15 10:21:36 2020

@author: ThinkPad
"""


from psycopg2 import (
        connect
        )
from werkzeug.security import check_password_hash, generate_password_hash


cleanup = (
        'DROP TABLE IF EXISTS users CASCADE',
        'DROP TABLE IF EXISTS data',
        'DROP TABLE IF EXISTS post'
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
                species VARCHAR(255) NOT NULL,
                dieback VARCHAR(255) NOT NULL,
                diameter VARCHAR(255) NOT NULL,
                height VARCHAR(255) NOT NULL,
                latitude VARCHAR(255) NOT NULL,
                longitude VARCHAR(255) NOT NULL,
                FOREIGN KEY (author_id)
                    REFERENCES data (data_id)
        )
        """,
        """ 
        CREATE TABLE post (
                post_id SERIAL PRIMARY KEY,
                author_id INTEGER NOT NULL,
                created TIMESTAMP DEFAULT NOW(),
                title VARCHAR(350) NOT NULL,
                body VARCHAR(500) NOT NULL,
                FOREIGN KEY (author_id)
                    REFERENCES users (user_id)
        )
        """)
        
sqlCommands = (
        'INSERT INTO users (user_name, user_password) VALUES (%s, %s) RETURNING user_id',
        'INSERT INTO data (species, dieback, diameter, height, latitude, longitude, author_id) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        )


conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
cur = conn.cursor()
for command in cleanup :
    cur.execute(command)

for command in commands :
    cur.execute(command)
    
cur.execute(sqlCommands[0], ('Admin', generate_password_hash('password')))
userId = cur.fetchone()[0]
cur.execute(sqlCommands[1], ('Acero', '5','25','100','41.04557','-86.5984', userId))
cur.execute(sqlCommands[1], ('Quercia', '0','35','120','41.0485','-86.5983', userId))
cur.execute(sqlCommands[1], ('Salice', '10','20','90','41.0477','-86.5984', userId))

cur.close()
conn.commit()
conn.close()

