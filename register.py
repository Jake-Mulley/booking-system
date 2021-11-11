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
    # get data from the form
    username = escape(form_data.getfirst('username', '').strip())
    password1 = escape(form_data.getfirst('password1', '').strip())
    password2 = escape(form_data.getfirst('password2', '').strip())
    fname = escape(form_data.getfirst('fname', '').strip())
    lname = escape(form_data.getfirst('lname', '').strip())
    if not username or not password1 or not password2:
        result = '<p>User name and password are required</p>'
    elif password1 != password2:
        result = '<p>Passwords must be equal</p>'
    else:
        try:
            connection = db.connect('localhost', '', '', '')
            cursor = connection.cursor(db.cursors.DictCursor)
            cursor.execute("""SELECT * FROM users 
                              WHERE username = %s""", (username))
            if cursor.rowcount > 0:
                result = '<p>That user name has already taken</p>'
            else:
                sha256_password = sha256(password1.encode()).hexdigest()
                account_type = "customer"
                # insert new users into the database
                cursor.execute("""INSERT INTO users (username, password, accountType, fname, lname) 
                                  VALUES (%s, %s, %s, %s, %s)""", (username, sha256_password, account_type, fname, lname))
                connection.commit()
                cursor.close()
                connection.close()
                # create session
                cookie = SimpleCookie()
                sid = sha256(repr(time()).encode()).hexdigest()
                cookie['sid'] = sid
                session_store = open('sess_' + sid, writeback=True)
                session_store['authenticated'] = True
                session_store['username'] = username
                session_store.close()
                result = """
                   <p>Successfully registered.</p>
                   <p>Thanks for registering.</p>
                   <ul>
                       <li><a href="viewBookings.py">View own bookings</a></li> 
                       <li><a href="logout.py">Logout</a></li>
                   </ul>"""
                print(cookie)
        except (db.Error, IOError):
            # nts, improve output here
            result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

print('Content-Type: text/html')
print()
print("""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title>Reservation System &#124; register</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <header>
                <h1>Reservation System</h1>
            </header>
            
            <main>
                <h1>Register:</h1>
                <form action="register.py" method="post">
                    <label for="username">User name: </label>
                    <input type="text" name="username" id="username" value="%s" />
                    <label for="password1">Password: </label>
                    <input type="password" name="password1" id="password1" />
                    <label for="passwords2">Re-enter password: </label>
                    <input type="password" name="password2" id="password2" />
                    <label for="fname">First Name: </label>
                    <input type="text" name="fname" id="fname" />
                    <label for="lname">Last Name: </label>
                    <input type="text" name="lname" id="lname" />
                    <input type="submit" value="Register" />
                </form>
                <p>Use the above boxes to enter a unique username, a password and re-enter the password in order to register.</p>
                <p><a href="login.py"> Log in</a></p>
                %s
            </main>
            <footer>
                <small>&copy; Group 3 3500 2021</small>
            </footer>
        </body>
    </html>""" % (username, result))
