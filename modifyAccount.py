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
        <h1>Please log in as an administrator to modify accounts.</h1>
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
            username = session_store['username']

            if session_store.get('authenticated'):
                connection = db.connect('localhost', '', '', '')
                cursor = connection.cursor(db.cursors.DictCursor)

                form_data = FieldStorage()

                # SQL query to find user details in users table

                cursor.execute('SELECT * FROM users WHERE username = %s', (username))
                updateMsg = ''
                row = cursor.fetchone()
                # is the user an admin,
                if row['accountType'] == 'admin':
                    # user is an admin, can modify accounts
                    if len(form_data) != 0:
                        # given input, escape and save as variables
                        usernameMod = escape(form_data.getfirst('usernameMod', '').strip())
                        accounttype = escape(form_data.getfirst('accounttype', '').strip())

                        cursor.execute('UPDATE users SET accountType = %s WHERE username = %s', (accounttype, usernameMod))
                        connection.commit()
                        updateMsg = '<p>Updated %s to %s successfully</p>' % (usernameMod, accounttype)

                    # close database connection
                    cursor.close()
                    connection.close()
                    result = """
                            <main>
                                    <h1>Modify Account</h1>
                                    <form action="modifyAccount.py" method="post">
                                        <label for="usernameMod">Username: </label>
                                        <input type="text" name="usernameMod" id="usernameMod"/>
                                        <label for="accounttype">Account Type: </label>
                                          <select id="accounttype" name="accounttype">
                                            <option value="customer">customer</option>
                                            <option value="waitstaff">waitstaff</option>
                                            <option value="manager">manager</option>
                                            <option value="admin">admin</option>
                                          </select>
                                        <input type="submit" value="Modify Account Booking" />

                                    </form>
                                    %s

                                    <p></p>
                            </main>
                            """ % (updateMsg)
            else:
                result = '<p>You do not have access to modify accounts</p>'

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
                %s
                <aside></aside>
                <footer>
                    <small>&copy; Group 3 CS3500 2021</small>
    	        </footer>
            </body>
        </html>""" % (result))
