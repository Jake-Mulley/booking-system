#!/usr/local/bin/python3

from cgitb import enable

enable()

from cgi import FieldStorage
from html import escape
from os import environ
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
                bookingID = 0
                if len(form_data) != 0:
                    bookingID = escape(form_data.getfirst('bookingID', '').strip())

                    if not bookingID:
                        # User did not put in required information
                        result = '<p>Booking ID is required</p>'

                    else:
                        try:
                            # connect to the database
                            connection = db.connect('localhost', '', '', '')
                            cursor = connection.cursor(db.cursors.DictCursor)
                            cursor.execute('SELECT * FROM users WHERE username = %s', username)
                            user = cursor.fetchone()
                            user_type = user['accountType']

                            cursor.execute("""SELECT * FROM bookings 
                                              WHERE BookingID = %s """, (bookingID))

                            if cursor.rowcount == 0:
                                result = '<p>There does not exist a booking with that ID</p>'
                            else:
                                # booking does exist, verify it should be deleted (correct RBAC)
                                row = cursor.fetchone()
                                if username == row['Person'] or user_type == 'manager' or user_type == 'admin':
                                    cursor.execute("""DELETE FROM bookings WHERE BookingID = %s
                                                    """, (bookingID))
                                    result = '<p>Cancellation successful</p>'
                                else:
                                    result = '<p>You do not have permission to cancel this booking</p>'

                                connection.commit()
                                cursor.close()
                                connection.close()

                        except (db.Error, IOError):
                            result = '<p>Sorry! We are experiencing problems at the moment. Please call back later. </p>'

except IOError:
    result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

print("""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title>Reservation System &#124; Cancel Booking</title>
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
                <h1> Cancelling Booking </h1>
                %s
            </main>
            <footer>
                <small>&copy; Group 3 3500 2021</small>
            </footer>
        </body>
    </html>""" % (result))
