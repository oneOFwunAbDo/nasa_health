"""
Entry point: run this file.  Login comes first, then the homepage.

Run:  python main.py
"""

from homepage_mock import HomepageMock
from login_page import LoginApp

if __name__ == "__main__":
    login = LoginApp()
    login.mainloop()

    if login.result:  # set only after a successful log in or sign up
        HomepageMock(login.result).mainloop()
