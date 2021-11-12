#!/usr/local/bin/python3

from cgitb import enable
enable()

from os import environ
from shelve import open
from http.cookies import SimpleCookie

print('Content-Type: text/html')
print()

result = '<p>You are already logged out</p>'
try:
    cookie = SimpleCookie()
    http_cookie_header = environ.get('HTTP_COOKIE')
    if http_cookie_header:
        cookie.load(http_cookie_header)
        if 'sid' in cookie:
            sid = cookie['sid'].value
            session_store = open('sess_' + sid, writeback=True)
            session_store['authenticated'] = False
            session_store.close()
            # add success message to output
            result = """
                <p>You are now logged out. Thanks for using our reservation system.</p>
                <p>You can log in again: <a href="login.py">Login.</a></p>"""

except IOError:
    result = '<p>Sorry! We are experiencing problems at the moment. Please call back later.</p>'

print("""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8" />
            <title>Reservation System &#124; Logged Out</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            <header>
                <h1>Reservation System</h1>
            </header>
            <main>
            <h1>Logged out.</h1>
            %s
            </main>
            <footer>
                <small>&copy; Group 3 CS3500 2021 </small>
            </footer>
        </body>
    </html>""" % (result))
