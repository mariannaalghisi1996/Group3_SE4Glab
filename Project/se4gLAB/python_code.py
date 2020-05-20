# -*- coding: utf-8 -*-
"""
Created on Mon May 18 10:57:38 2020

@author: maria
"""

from flask import (
    Flask, render_template, request, redirect, flash, url_for, session, g
)

from werkzeug.security import check_password_hash, generate_password_hash

from werkzeug.exceptions import abort

from psycopg2 import (
        connect
)

import static_analysis
import bokeh_yourdata

app = Flask(__name__, template_folder="templates")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else :
            
            conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
            cur = conn.cursor()
            cur.execute(
            'SELECT user_id FROM users WHERE user_name = %s', (username,))
            if cur.fetchone() is not None:
                error = 'User {} is already registered.'.format(username)
                cur.close()
                conn.close()

        if error is None:
            cur.execute(
                'INSERT INTO users (user_name, user_password) VALUES (%s, %s)',
                (username, generate_password_hash(password))
            )
            cur.close()
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

        flash(error)

    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
        cur = conn.cursor()
        error = None
        cur.execute(
            'SELECT * FROM users WHERE user_name = %s', (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#@app.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        
        conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM users WHERE user_id = %s', (user_id,)
        )
        g.user = cur.fetchone()
        cur.close()
        conn.commit()
        conn.close()
    if g.user is None:
        return False
    else: 
        return True
    
@app.route('/')
@app.route('/index')
def index():
    load_logged_in_user()
    return render_template('index.html')
    
    
@app.route('/visualization')
def visualization():
    load_logged_in_user()
    return render_template('trees_map.html')
  
    
@app.route('/blog')
def blog():
    
    conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
    cur = conn.cursor()
    cur.execute(
            """SELECT users.user_name, post.post_id, post.created, post.title, post.body 
               FROM users, post WHERE  
                    users.user_id = post.author_id"""
                    )
    posts = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    load_logged_in_user()
    return render_template('blog/index.html', posts=posts)



@app.route('/create', methods=('GET', 'POST'))
def create():
    if load_logged_in_user():
        if request.method == 'POST' :
            title = request.form['title']
            body = request.form['body']
            error = None
            
            if not title :
                error = 'Title is required!'
            if error is not None :
                flash(error)
                return redirect(url_for('blog'))
            else : 
                    
                    conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
                    cur = conn.cursor()
                    cur.execute('INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s)', 
                               (title, body, g.user[0])
                               )
                    cur.close()
                    conn.commit()
                    conn.close()
                    return redirect(url_for('blog'))
        else :
            return render_template('blog/create.html')
    else :
        error = 'Only loggedin users can insert posts!'
        flash(error)
        return redirect(url_for('blog/login'))
    
def get_post(id):
    
    conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
    cur = conn.cursor()
    cur.execute(
        """SELECT *
           FROM post
           WHERE post.post_id = %s""",
        (id,)
    )
    post = cur.fetchone()
    cur.close()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if post[1] != g.user[0]:
        abort(403)

    return post
    
@app.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    if load_logged_in_user():
        post = get_post(id)
        if request.method == 'POST' :
            title = request.form['title']
            body = request.form['body']
            error = None
            
            if not title :
                error = 'Title is required!'
            if error is not None :
                flash(error)
                return redirect(url_for('blog'))
            else : 
                
                conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
                cur = conn.cursor()
                cur.execute('UPDATE post SET title = %s, body = %s'
                               'WHERE post_id = %s', 
                               (title, body, id)
                               )
                cur.close()
                conn.commit()
                return redirect(url_for('blog'))
        else :
            return render_template('blog/update.html', post=post)
    else :
        error = 'Only loggedin users can insert posts!'
        flash(error)
        return redirect(url_for('login'))
    
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    
    conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
    cur = conn.cursor()
    cur.execute('DELETE FROM post WHERE post_id = %s', (id,))
    conn.commit()
    return redirect(url_for('blog'))    


@app.route('/insert_data', methods=('GET', 'POST'))
def insert_data():
    if load_logged_in_user():
        if request.method == 'POST':
            
            species = request.form['species']
            dieback = request.form['dieback']
            diameter = request.form['diameter']
            height = request.form['height']
            lat = request.form['latitude']
            lon = request.form['longitude']
            error = None
            
            if not species:
                error = 'Name of the species is required!'
            elif (int(dieback)<0 or int(dieback)>100):
                error = 'Please insert a valid value for dieback percentage!'
            elif (float(diameter)<0 or float(diameter) >50):
                error = 'Please insert a valid value for diameter!'
            elif (float(height)<3 or float(height)>150):
                error = 'Please insert a valid value for height!'
            elif (float(lat)<41.0080 or float(lat)>42.0000):
                error = 'Sorry but the value of the latitude inserted does not belong to our domain!'
            #elif (float(lon)>-86.62 or float(lon)<-86.70000):
            #    error = 'Sorry but the value of the longitude inserted does not belong to our domain!'
            if error is not None :
                flash(error)
                return redirect(url_for('insert_data'))
            else : 
                
                conn = connect("dbname=prova user=postgres password=postgres sslmode=disable")
                cur = conn.cursor()
                cur.execute('INSERT INTO data (species, dieback, diameter, height, latitude, longitude, author_id) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                            (species, dieback, diameter, height, lat, lon, g.user[0],)
                            )
                cur.close()
                conn.commit()
                return redirect(url_for('index'))
        else :
            return render_template('insert_data.html')
    else :
        error = 'Only logged in users can insert data!'
        flash(error)
        return render_template('login.html')
    
@app.route('/statistics')
def statistics():
    if load_logged_in_user():
        #static_analysis.f_static()
        return render_template('statistic.html')
    else:
        error = 'Only logged in users can get statistical information!'
        flash(error)
        return render_template('login.html')
    
@app.route('/DB_visualization')
def visualize_your_data():
    if load_logged_in_user():
        x = bokeh_yourdata.funct_DB_visua()
        if x == None:
            return render_template('yourData_map.html')
        else:
            error = 'Something went wrong!"
            flash(error)
            return render_template('index.html')
    else:
        error = 'Only logged in users can visualize this map!'
        flash(error)
        return render_template('login.html')
    
@app.route('/pie_chart')
def pie_chart():
    if load_logged_in_user():
        return render_template('pie.html')
    else:
        error = 'Only logged in users can visualize this page!'
        flash(error)
        return render_template('login.html')

if __name__ == '__main__':
    app.run()
