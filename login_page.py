"""
Login / sign-up screens for the Space Health app (tkinter + face_recognition).

Flow:
  Welcome -> Log in:  automatic face scan (shows the recognised person), or username + password
          -> Sign up: name, username, password -> face scan (5 snapshots)
                      -> choose station (ISS / Moon / Mars) and language (EN / AR)
"""

import time
import tkinter as tk

import cv2
import face_recognition
import numpy as np
from PIL import Image, ImageTk

import user_store as store
from i18n import STATIONS, tr

BG, CARD, BORDER = "#0d1117", "#161b22", "#30363d"
TEXT, MUTED, ACCENT, ERR = "#e6edf3", "#8b949e", "#39d353", "#f85149"

FACE_TOLERANCE = 0.5   # lower = stricter face matching
SAMPLES_NEEDED = 5     # face snapshots taken during sign-up
LOGIN_TIMEOUT = 20     # seconds to recognise a face before offering a retry


# ------------------------------------------------------------ camera + face helpers
class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    @property
    def ok(self):
        return self.cap.isOpened()

    def read(self):
        ok, frame = self.cap.read()
        return frame if ok else None

    def close(self):
        self.cap.release()


def _find_faces(frame):
    """Detect faces on a half-size copy (fast), return locations in full-size coordinates."""
    small = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    locations = face_recognition.face_locations(np.ascontiguousarray(small[:, :, ::-1]))
    return [(top * 2, right * 2, bottom * 2, left * 2) for top, right, bottom, left in locations]


def _encode(frame, locations):
    rgb = np.ascontiguousarray(frame[:, :, ::-1])
    return face_recognition.face_encodings(rgb, locations)[0]


def _match_face(encoding):
    """Return the username whose stored face matches, or None."""
    names, known = [], []
    for username, stored in store.all_face_encodings():
        names.append(username)
        known.append(np.array(stored))
    if not known:
        return None
    distances = face_recognition.face_distance(known, encoding)
    best = int(np.argmin(distances))
    return names[best] if distances[best] < FACE_TOLERANCE else None


def _to_photo(frame, width=420):
    rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)  # mirror, like a selfie
    height = int(rgb.shape[0] * width / rgb.shape[1])
    return ImageTk.PhotoImage(Image.fromarray(rgb).resize((width, height)))


# ----------------------------------------------------------------------- the app
class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Space Health")
        self.geometry("600x780")
        self.minsize(520, 660)
        self.configure(bg=BG)

        self.lang = "en"
        self.camera = None
        self.loop_id = None
        self.current = None
        self.pending = None      # sign-up data waiting for face scan
        self.samples = []        # face encodings captured during sign-up
        self.sel_station = "ISS"
        self.result = None       # set when the user logs in or signs up

        self.render(self.page_welcome)

    # ----- text + layout helpers
    def t(self, key, **kwargs):
        return tr(self.lang, key, **kwargs)

    def justify(self):
        return "right" if self.lang == "ar" else "left"

    def label(self, parent, text, size=12, bold=False, color=TEXT):
        return tk.Label(parent, text=text, bg=BG, fg=color, justify=self.justify(),
                        wraplength=460, font=("Segoe UI", size, "bold" if bold else "normal"))

    def button(self, parent, text, command, primary=False):
        return tk.Button(parent, text=text, command=command, bd=0, padx=20, pady=10,
                         font=("Segoe UI", 12, "bold"), cursor="hand2",
                         bg=ACCENT if primary else CARD,
                         fg="#0d1117" if primary else TEXT,
                         activebackground=BORDER, activeforeground=TEXT)

    def entry(self, parent, show=""):
        return tk.Entry(parent, font=("Segoe UI", 12), bg=CARD, fg=TEXT,
                        insertbackground=TEXT, relief="flat", justify=self.justify(), show=show)

    def set_lang(self, lang):
        self.lang = lang
        self.render(self.current)

    def render(self, builder):
        """Clear the window and build one screen. Stops the camera and any scan loop."""
        self.current = builder
        self._stop()
        for widget in self.winfo_children():
            widget.destroy()

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=12)
        other = "ar" if self.lang == "en" else "en"
        self.button(top, tr(self.lang, "toggle"), lambda: self.set_lang(other)).pack(side="right")

        page = tk.Frame(self, bg=BG)
        page.pack(fill="both", expand=True, padx=40, pady=10)
        builder(page)

    def _stop(self):
        if self.loop_id:
            self.after_cancel(self.loop_id)
            self.loop_id = None
        if self.camera:
            self.camera.close()
            self.camera = None

    def _finish(self, username):
        """Save the logged-in user and close the login window; main.py opens the homepage."""
        user = store.get_user(username)
        self._stop()
        self.result = {
            "username": user["username"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "station": user["station"],
            "language": user["language"],
            "tasks": user.get("tasks", {}),
        }
        self.destroy()

    def _show(self, frame):
        photo = _to_photo(frame)
        self.preview.config(image=photo)
        self.preview.image = photo  # keep a reference or Tk drops the image

    # ----- welcome
    def page_welcome(self, page):
        self.label(page, self.t("app"), 28, True).pack(pady=(40, 4))
        self.label(page, self.t("welcome"), 13, color=MUTED).pack(pady=(0, 40))
        self.button(page, self.t("log_in"), lambda: self.render(self.page_login),
                    primary=True).pack(fill="x", pady=6)
        self.button(page, self.t("sign_up"), lambda: self.render(self.page_signup)).pack(fill="x", pady=6)

    # ----- log in with face
    def page_login(self, page):
        self.label(page, self.t("look_camera"), 14, True).pack(pady=(10, 12))
        self.preview = tk.Label(page, bg=CARD)
        self.preview.pack()
        self.status = self.label(page, self.t("scanning"), 12, color=MUTED)
        self.status.pack(pady=12)
        self.button(page, self.t("use_password"),
                    lambda: self.render(self.page_password)).pack(fill="x", pady=(10, 6))
        self.button(page, self.t("back"), lambda: self.render(self.page_welcome)).pack(fill="x")

        self.camera = Camera()
        if not self.camera.ok:
            self.status.config(text=self.t("camera_fault"), fg=ERR)
            self._stop()
            return
        self.deadline = time.time() + LOGIN_TIMEOUT
        self._login_tick()

    def _login_tick(self):
        frame = self.camera.read()
        if frame is not None:
            self._show(frame)
            locations = _find_faces(frame)
            if len(locations) == 1:
                username = _match_face(_encode(frame, locations))
                if username:
                    self._recognised(username, frame, locations[0])
                    return

        if time.time() > self.deadline:
            self._stop()
            self.status.config(text=self.t("no_match"), fg=ERR)
            self.button(self.status.master, self.t("retry"),
                        lambda: self.render(self.page_login)).pack(pady=6)
            return

        self.loop_id = self.after(60, self._login_tick)

    def _recognised(self, username, frame, location):
        """Freeze the frame with a box around the face, then wait for the user to continue."""
        top, right, bottom, left = location
        frozen = frame.copy()
        cv2.rectangle(frozen, (left, top), (right, bottom), (57, 211, 83), 3)  # green box
        self.render(lambda page: self.page_recognised(page, username, frozen))

    def page_recognised(self, page, username, frame):
        user = store.get_user(username)
        self.label(page, self.t("matched", name=user["first_name"]), 20, True,
                   color=ACCENT).pack(pady=(10, 12))
        self.preview = tk.Label(page, bg=CARD)
        self.preview.pack()
        self._show(frame)
        self.button(page, self.t("continue"), lambda: self._finish(username),
                    primary=True).pack(fill="x", pady=(16, 0))

    # ----- log in with username + password (camera fallback)
    def page_password(self, page):
        self.label(page, self.t("log_in"), 22, True).pack(pady=(20, 20))
        self.label(page, self.t("username")).pack(fill="x")
        user_entry = self.entry(page)
        user_entry.pack(fill="x", ipady=6, pady=(0, 12))
        self.label(page, self.t("password")).pack(fill="x")
        pw_entry = self.entry(page, show="•")
        pw_entry.pack(fill="x", ipady=6, pady=(0, 12))
        self.status = self.label(page, "", color=ERR)
        self.status.pack(pady=8)

        def submit():
            username = user_entry.get().strip()
            password = pw_entry.get()
            if not username or not password:
                self.status.config(text=self.t("fill_all"))
            elif store.check_password(username, password):
                self._finish(username)
            else:
                self.status.config(text=self.t("wrong_pw"))

        self.button(page, self.t("log_in"), submit, primary=True).pack(fill="x", pady=6)
        self.button(page, self.t("back"), lambda: self.render(self.page_login)).pack(fill="x")

    # ----- sign up: details
    def page_signup(self, page):
        self.label(page, self.t("sign_up"), 22, True).pack(pady=(10, 16))
        fields = {}
        for key in ("first", "last", "username"):
            self.label(page, self.t(key)).pack(fill="x")
            fields[key] = self.entry(page)
            fields[key].pack(fill="x", ipady=6, pady=(0, 10))
        self.label(page, self.t("password")).pack(fill="x")
        fields["password"] = self.entry(page, show="•")
        fields["password"].pack(fill="x", ipady=6, pady=(0, 10))
        self.status = self.label(page, "", color=ERR)
        self.status.pack(pady=8)

        def next_step():
            values = {key: entry.get().strip() for key, entry in fields.items()}
            if not all(values.values()):
                self.status.config(text=self.t("fill_all"))
            elif store.username_taken(values["username"]):
                self.status.config(text=self.t("user_taken"))
            elif len(values["password"]) < 6:
                self.status.config(text=self.t("short_pw"))
            else:
                self.pending = values
                self.render(self.page_face_scan)

        self.button(page, self.t("continue"), next_step, primary=True).pack(fill="x", pady=6)
        self.button(page, self.t("back"), lambda: self.render(self.page_welcome)).pack(fill="x")

    # ----- sign up: face scan
    def page_face_scan(self, page):
        self.samples = []
        self.last_capture = 0.0
        self.label(page, self.t("scan_title"), 22, True).pack(pady=(10, 6))
        self.label(page, self.t("scan_hint"), 12, color=MUTED).pack(pady=(0, 10))
        self.preview = tk.Label(page, bg=CARD)
        self.preview.pack()
        self.status = self.label(page, self.t("scan_progress", n=0), 12, color=MUTED)
        self.status.pack(pady=10)
        self.button(page, self.t("back"), lambda: self.render(self.page_signup)).pack(fill="x", pady=(14, 0))

        self.camera = Camera()
        if not self.camera.ok:
            self.status.config(text=self.t("camera_fault"), fg=ERR)
            self._stop()
            return
        self._scan_tick()

    def _scan_tick(self):
        frame = self.camera.read()
        if frame is not None:
            self._show(frame)
            locations = _find_faces(frame)
            now = time.time()

            if len(locations) == 0:
                self.status.config(text=self.t("no_face"), fg=ERR)
            elif len(locations) > 1:
                self.status.config(text=self.t("many_faces"), fg=ERR)
            elif now - self.last_capture >= 0.8:  # spaced snapshots, not 5 in one second
                encoding = _encode(frame, locations)
                if _match_face(encoding):
                    self.status.config(text=self.t("scan_dup"), fg=ERR)
                    self._stop()
                    return
                self.samples.append([float(x) for x in encoding])
                self.last_capture = now
                self.status.config(text=self.t("scan_progress", n=len(self.samples)), fg=ACCENT)
                if len(self.samples) == SAMPLES_NEEDED:
                    self.render(self.page_station)
                    return

        self.loop_id = self.after(60, self._scan_tick)

    # ----- sign up: station + language
    def page_station(self, page):
        self.label(page, self.t("station_title"), 20, True).pack(pady=(20, 12))
        station_var = tk.StringVar(value=self.sel_station)

        def pick_station():
            self.sel_station = station_var.get()

        for code in STATIONS:
            tk.Radiobutton(page, text=self.t("st_" + code), variable=station_var, value=code,
                           command=pick_station, indicatoron=0, bd=0, width=30, pady=10,
                           font=("Segoe UI", 12), bg=CARD, fg=TEXT, selectcolor=ACCENT,
                           activebackground=BORDER).pack(pady=4)

        self.label(page, self.t("language_title"), 20, True).pack(pady=(28, 12))
        lang_var = tk.StringVar(value=self.lang)
        for code in ("en", "ar"):
            tk.Radiobutton(page, text=self.t("lang_" + code), variable=lang_var, value=code,
                           command=lambda: self.set_lang(lang_var.get()), indicatoron=0, bd=0,
                           width=30, pady=10, font=("Segoe UI", 12), bg=CARD, fg=TEXT,
                           selectcolor=ACCENT, activebackground=BORDER).pack(pady=4)

        def save_account():
            data = self.pending
            store.create_user(
                first_name=data["first"], last_name=data["last"],
                username=data["username"], password=data["password"],
                face_encodings=self.samples, station=self.sel_station, language=self.lang,
            )
            self._finish(data["username"])

        self.button(page, self.t("finish"), save_account, primary=True).pack(fill="x", pady=(30, 6))
