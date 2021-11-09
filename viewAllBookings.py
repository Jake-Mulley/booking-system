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
        <h1>Please log in or register to view your bookings.</h1>
       <p>You do not have permission to access this page.</p>
       <ul>
           <li><a href="register.py">Register</a></li>
           <li><a href="login.py">Login</a></li>
           <a href="logout.py">Log Out </a>
           
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
            username = session_store['username']

            if session_store.get('authenticated'):
                connection = db.connect('localhost', '', '', '')
                cursor = connection.cursor(db.cursors.DictCursor)

                # is the user a staff member

                cursor.execute('SELECT * FROM users WHERE username = %s', (username))

                # use fetchone() not fetchall, no need for a loop here
                for row in cursor.fetchall():
                    if row['accountType'] == 'waitstaff' or row['accountType'] == 'manager' or row['accountType'] == 'admin':
                        cursor.execute('SELECT * FROM bookings')
                        table = '<table><tr><th>Booking ID</th><th>Table</th><th>Time</th></tr>'
                        counter = 0
                        for row in cursor.fetchall():
                            table += '<tr><th>%s</th><td>%s</td><td>%s</td></tr>' % (
                                row['BookingID'], row['TableID'], row['BookingTime'])
                        table += '</table>'
                        cursor.close()
                        connection.close()
                        result = """
                            <nav>
                                    <a href=""> </a>
                                    <a href=""> </a>
                                    <a href=""> </a>
                                    <a href="logout.py">Log Out </a>
                            </nav>
                            <main>
                                    <h1>Cancel Booking</h1>
                                    <form action="cancelBooking.py" method="post">
                                        <label for="bookingID">Booking ID to cancel: </label>
                                        <input type="text" name="bookingID" id="bookingID"/>
                                        <input type="submit" value="Cancel Booking" />
                                    </form>
                                    <p></p>
                                    %s
                            </main>
                            """ % (table)
            else:
                result = '<p>You do not have access to viewing all bookings</p>'
            session_store.close()
except IOError:
    result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

print("""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title>Reservation System &#124; View Bookings</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <header>
                <h1>Reservation System</h1>
            </header>

            %s
            <aside></aside>
            <footer>
                <small>&copy; Group 3 CS3500 2021</small>
                <a href="#header">Back To The Top</a>
	        </footer>
        </body>
    </html>""" % (result))
