#!/usr/local/bin/python3
from cgitb import enable

enable()

from cgi import FieldStorage
from html import escape
from hashlib import sha256
from os import environ
from time import time
from shelve import open
from http.cookies import SimpleCookie
import pymysql as db

print('Content-Type: text/html')
print()

result = """
    <main>
        <h1>Please log in or register to make a booking.</h1>
       <p>You do not have permission to access this page.</p>
       <ul>
           <li><a href="register.py">Register</a></li>
           <li><a href="login.py">Login</a></li>
       </ul>
   </main>"""

try:
    cookie = SimpleCookie()
    http_cookie_header = environ.get('HTTP_COOKIE')
    if http_cookie_header:
        cookie.load(http_cookie_header)
        if 'sid' in cookie:
            sid = cookie['sid'].value
            session_store = open('sess_' + sid, writeback=False)
            if session_store.get('authenticated'):
                username = session_store['username']

                form_data = FieldStorage()
                table = ''
                time = ''
                if len(form_data) != 0:
                    table = escape(form_data.getfirst('table', '').strip())
                    time = escape(form_data.getfirst('time', '').strip())

                    if not table or not time:
                        # User did not put in required information
                        result = '<p>Table Number and time are required</p>'

                    else:
                        try:
                            connection = db.connect('localhost', 'jm72', 'phoht', 'cs6503_cs1106_jm72')
                            cursor = connection.cursor(db.cursors.DictCursor)
                            cursor.execute("""SELECT * FROM bookings 
                                              WHERE TableID = %s AND BookingTime = %s""", (table, time))
                            if cursor.rowcount > 0:
                                result = '<p>That table has already taken for that time</p>'
                            else:
                                # create booking

                                cursor.execute("""INSERT INTO bookings (Person, BookingTime, TableID)
                                                  VALUES (%s, %s, %s)""", (username, time, table))
                                connection.commit()
                                cursor.close()
                                connection.close()

                        except (db.Error, IOError):
                            # nts, improve output here
                            result = '<p>Sorry! We are experiencing problems at the moment. Please call back later. </p>'

except IOError:
    result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

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
                <form action="test.py" method="post">
                    <label for="table">Table Number: </label>
                    <input type="text" name="table" id="table" value="%s" />
                    <label for="time">Time (format: YYYY-MM-DD hh:mm:ss): </label>
                    <input type="text" name="time" id="time" />

                    <input type="submit" value="Book" />
                </form>
                <p>Use the above boxes to enter a valid table number and the time with which you wish to book</p>
                <p><a href="login.py"> Log in</a></p>

                %s
            </main>
            <footer>
                <small>&copy; Group 3 3500 2021</small>
                <a href="#header">Back To The Top</a>
            </footer>
        </body>
    </html>""" % (table, result))
