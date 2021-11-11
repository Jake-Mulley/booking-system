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
                # connect to database
                connection = db.connect('localhost', '', '', '')

                cursor = connection.cursor(db.cursors.DictCursor)

                # username of user logged in
                username = session_store['username']
                cursor.execute('SELECT * FROM users WHERE username = %s', (username))

                form_data = FieldStorage()
                table = ''
                time = ''
                row = cursor.fetchone()
                # is the user a staff member,
                if row['accountType'] == 'manager' or row['accountType'] == 'waitstaff':
                    result = """    <form action="bookOther.py" method="post">
                                        <label for="usernameBook">Username: </label>
                                        <input type="text" name="usernameBook" id="usernameBook" value="" />
                                        <label for="table">Table Number: </label>
                                        <input type="text" name="table" id="table" value="" />
                                        <label for="time">Time (format: YYYY-MM-DD hh:mm:ss): </label>
                                        <input type="text" name="time" id="time" />
                    
                                        <input type="submit" value="Book" />
                                    </form>
                                    <p>Use the above boxes to enter a username of the person to book for,  
                                    valid table number and the time with which you wish to book</p>"""

                    if len(form_data) != 0:
                        table = escape(form_data.getfirst('table', '').strip())
                        time = escape(form_data.getfirst('time', '').strip())
                        usernameBook = escape(form_data.getfirst('usernameBook', '').strip())

                        if not table or not time:
                            # User did not put in required information
                            result += '<p>Username, Table Number and time are required</p>'

                        else:
                            try:
                                cursor.execute("""SELECT * FROM bookings 
                                                  WHERE TableID = %s AND BookingTime = %s""", (table, time))
                                if cursor.rowcount > 0:
                                    result += '<p>That table has already taken for that time</p>'
                                else:
                                    # create booking

                                    cursor.execute("""INSERT INTO bookings (Person, BookingTime, TableID)
                                                      VALUES (%s, %s, %s)""", (usernameBook, time, table))
                                    result += '<p>Booking at table %s at %s was successful for %s</p>' % (table, time, usernameBook)
                                    connection.commit()

                            except (db.Error, IOError):
                                result += '<p>Sorry! We are experiencing problems at the moment. Please call back later. </p>'
                else:
                    result = '<p>You must be logged in as a staff member to book for someone else.</p>'

                # close DB connection
                cursor.close()
                connection.close()



except IOError:
    result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

print("""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title>Reservation System &#124; Make Booking</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <header>
                <h1>Reservation System</h1>
            </header>
            <nav>
                <a href="viewBookings.py">View own Bookings</a>
                <a href="book.py">Make Booking For Self</a>
                <a href="viewAllBookings.py">View All Bookings</a>
                <a href="bookOther.py">Make Booking For Someone else</a>
                <a href="modifyAccount.py">Modify Account</a>
                <a href="logout.py">Log Out</a>
            </nav>
            <main>
                <h1>Make Booking for someone:</h1>


                %s
            </main>
            <footer>
                <small>&copy; Group 3 3500 2021</small>
            </footer>
        </body>
    </html>""" % (result))
