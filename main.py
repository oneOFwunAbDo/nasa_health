"""
Entry point: run this file.  Login comes first, then the homepage.

Run:  python main.py
"""

import sys

import user_store as store
from homepage_mock import HomepageMock
from login_page import LoginApp

# DEVELOPER SHORTCUT: `python main.py --admin` skips the login page and opens
# the admin account below, loaded from users.json (saved station, language and tasks apply).
# Remove this block before the app is given to real users.
ADMIN_USERNAME = "oneofwunabdo"

if __name__ == "__main__":
    if "--admin" in sys.argv:
        user = store.get_user(ADMIN_USERNAME)
        if user is None:
            sys.exit(f"Admin account '{ADMIN_USERNAME}' not found in users.json. Sign up with that username first.")
        HomepageMock({
            "username": user["username"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "station": user["station"],
            "language": user["language"],
            "tasks": user.get("tasks", {}),
        }).mainloop()
    else:
        login = LoginApp()
        login.mainloop()

        if login.result:  # set only after a successful log in or sign up
            HomepageMock(login.result).mainloop()