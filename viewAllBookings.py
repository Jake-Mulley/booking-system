#!/usr/local/bin/python3

from cgitb import enable

enable()

from os import environ
from shelve import open
from http.cookies import SimpleCookie
import pymysql as db

print('Content-Type: text/html')
print()

result = """

        <h1>Please log in or register to view all bookings.</h1>
       <p>You do not have permission to access this page.</p>
       <ul>
           <li><a href="register.py">Register</a></li>
           <li><a href="login.py">Login</a></li>
       </ul>
   """
table = ''

try:
    cookie = SimpleCookie()
    # get the http cookie
    http_cookie_header = environ.get('HTTP_COOKIE')
    if http_cookie_header:
        # cookie exists, load http cookie to cookie
        cookie.load(http_cookie_header)
        if 'sid' in cookie:
            sid = cookie['sid'].value
            session_store = open('sess_' + sid, writeback=False)
            username = session_store['username']

            if session_store.get('authenticated'):
                # connect to the database
                connection = db.connect('localhost', '', '', '')
                cursor = connection.cursor(db.cursors.DictCursor)

                # is the user a staff member

                cursor.execute('SELECT * FROM users WHERE username = %s', (username))

                # use fetchone() not fetchall, no need for a loop here
                userDetails = cursor.fetchone()
                if userDetails['accountType'] == 'waitstaff' or userDetails['accountType'] == 'manager':

                    # the user is a staff member, can view all bookings
                    cursor.execute('SELECT * FROM bookings')
                    table = '<h1>View Bookings</h1><table><tr><th>Booking ID</th><th>Table</th><th>Time</th></tr>'
                    counter = 0
                    for row in cursor.fetchall():
                        table += '<tr><th>%s</th><td>%s</td><td>%s</td></tr>' % (
                            row['BookingID'], row['TableID'], row['BookingTime'])
                    table += '</table>'
                    cursor.close()
                    connection.close()
                    if userDetails['accountType'] == 'manager':
                        # if it is a manager they have the option to cancel any booking, so output the form to do so
                        result = """
                                    <h1>Make a cancellation</h1>
                                    <form action="cancelBooking.py" method="post">
                                        <label for="bookingID">Booking ID to cancel: </label>
                                        <input type="text" name="bookingID" id="bookingID"/>
                                        <input type="submit" value="Cancel Booking" />
                                    </form>
                                """
                    else:
                        result = ''

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
            <nav>
                <a href="viewBookings.py">View own Bookings</a>
                <a href="book.py">Make Booking For Self</a>
                <a href="viewAllBookings.py">View All Bookings</a>
                <a href="bookOther.py">Make Booking For Someone else</a>
                <a href="modifyAccount.py">Modify Account</a>
                <a href="logout.py">Log Out</a>
            </nav>
            <main>
                %s
                %s
            </main>
            
            <aside></aside>
            <footer>
                <small>&copy; Group 3 CS3500 2021</small>
	        </footer>
        </body>
    </html>""" % (table, result))
