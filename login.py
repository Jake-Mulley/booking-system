#!/usr/local/bin/python3

from cgitb import enable

enable()

from cgi import FieldStorage
from html import escape
from hashlib import sha256
from time import time
from shelve import open
from http.cookies import SimpleCookie
import pymysql as db


form_data = FieldStorage()
username = ''
result = ''
if len(form_data) != 0:
    username = escape(form_data.getfirst('username', '').strip())
    password = escape(form_data.getfirst('password', '').strip())
    if not username or not password:
        result = '<p>User name and password are required</p>'
    else:
        sha256_password = sha256(password.encode()).hexdigest()
        try:
            # connect to the database
            connection = db.connect('localhost', '', '', '')
            cursor = connection.cursor(db.cursors.DictCursor)
            # Query database with the inputted username and password
            cursor.execute("""SELECT * FROM users 
                              WHERE username = %s
                              AND password = %s""", (username, sha256_password))
            if cursor.rowcount == 0:
                # no result from database, incorrect details
                result = '<p>You entered an incorrect user name or password</p>'
            else:
                # correct details, create session
                cookie = SimpleCookie()
                sid = sha256(repr(time()).encode()).hexdigest()
                cookie['sid'] = sid
                session_store = open('sess_' + sid, writeback=True)
                session_store['authenticated'] = True
                session_store['username'] = username
                session_store.close()
                # add list to navigate web application to output
                result = """
                   <p>You have logged in.</p>
                   <p>Welcome back to the reservation system.</p>
                   <ul>

                        <a href="viewBookings.py">View own Bookings</a>
                        <a href="book.py">Make Booking For Self</a>
                        <a href="viewAllBookings.py">View All Bookings</a>
                        <a href="bookOther.py">Make Booking For Someone else</a>
                        <a href="modifyAccount.py">Modify Account</a>
                        <a href="logout.py">Log Out</a>
                   </ul>"""
                print(cookie)
            cursor.close()
            connection.close()
        except (db.Error, IOError):
            result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

print('Content-Type: text/html')
print()
print("""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title>Reservation System &#124; Log in</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <header>
                <h1>Reservation System</h1>
            </header>
            <main>
                <h1>Log In:</h1>
                <form action="login.py" method="post">
                    <label for="username">User name: </label>
                    <input type="text" name="username" id="username" value="%s" />
                    <label for="password">Password: </label>
                    <input type="password" name="password" id="password" />
                    <input type="submit" value="Login" />
                </form>
                <p>Use the above boxes to type in your username and password.</p>
                <a href="register.py"> Register</a></p>

                %s
            </main>
            <footer>
                <small>&copy; Group 3 CS3500 2021</small>
            </footer>
        </body>
    </html>""" % (username, result))
