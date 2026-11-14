"""
Homepage for the Space Health app.
Opened by main.py after login, with the logged-in user's saved record.
All data comes from the user's own record. Nothing is demo data.
"""

import datetime
import math
import tkinter as tk

import user_store as store
from i18n import DAY_LABELS, MONTHS, STATIONS, tr

BG, CARD, BORDER = "#0d1117", "#161b22", "#30363d"
SIDE_BG, TEXT, MUTED, ACCENT = "#0b0f14", "#e6edf3", "#8b949e", "#39d353"
HEAT = ["#22272e", "#0e4429", "#006d32", "#26a641", "#39d353"]  # level 0 = visible empty square

CELL, GAP = 11, 3
PITCH = CELL + GAP
WEEKS = 53
LEFT_PAD, TOP_PAD = 34, 20
SIDEBAR_W = 110

# The donut's shading differs per station
STATION_RAMPS = {
    "ISS": ".,-~:;=!*#$@",
    "Mars": " .:-=+*#%@",
    "Moon": ".'`^\",:;Il!i~+_?][}{1)(|/",
}

# ------------------------------------------------------------- ASCII donut
def donut_frame(A, B, ramp, W=48, H=22):
    """Render one frame of the spinning ASCII torus (the classic donut.c math)."""
    zbuf = [0.0] * (W * H)
    out = [" "] * (W * H)
    cA, sA, cB, sB = math.cos(A), math.sin(A), math.cos(B), math.sin(B)
    R1, R2, K2 = 1.0, 2.0, 5.0
    K1 = W * K2 * 3 / (8 * (R1 + R2))

    for j in range(0, 628, 7):          # theta around the tube
        ct, st = math.cos(j / 100), math.sin(j / 100)
        for i in range(0, 628, 2):      # phi around the ring
            cp, sp = math.cos(i / 100), math.sin(i / 100)
            circlex = R2 + R1 * ct
            circley = R1 * st
            x = circlex * (cB * cp + sA * sB * sp) - circley * cA * sB
            y = circlex * (sB * cp - sA * cB * sp) + circley * cA * cB
            z = K2 + cA * circlex * sp + circley * sA
            ooz = 1 / z
            xp = int(W / 2 + K1 * ooz * x)
            yp = int(H / 2 - K1 * ooz * y * 0.5)   # 0.5 corrects character aspect
            L = cp * ct * sB - cA * ct * sp - sA * st + cB * (cA * st - ct * sA * sp)
            if L > 0 and 0 <= xp < W and 0 <= yp < H:
                idx = xp + yp * W
                if ooz > zbuf[idx]:
                    zbuf[idx] = ooz
                    lum = max(0, min(int(L * 8), len(ramp) - 1))
                    out[idx] = ramp[lum]

    return "\n".join("".join(out[r * W:(r + 1) * W]) for r in range(H))


def current_streak(tasks):
    """Consecutive days, ending today, with at least one completed task."""
    day = datetime.date.today()
    n = 0
    while tasks.get(day, 0) > 0:
        n += 1
        day -= datetime.timedelta(days=1)
    return n


# ----------------------------------------------------------------- the app
class HomepageMock(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.title("Space Health")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(bg=BG)

        self.user = user
        self.lang = user["language"]
        self.tasks = {datetime.date.fromisoformat(k): v for k, v in user.get("tasks", {}).items()}

        # settings state (persists across rebuilds)
        self.station = tk.StringVar(value=user["station"])
        self.reminders = tk.BooleanVar(value=True)
        self.animate = tk.BooleanVar(value=True)
        self.lang_var = tk.StringVar(value=self.lang)
        self.A, self.B = 0.0, 0.0

        self.build()
        self._tick()

    def t(self, key, **kwargs):
        return tr(self.lang, key, **kwargs)

    def station_name(self):
        return self.t("st_" + self.station.get())

    # ----- build the whole screen (also used when the language changes)
    def build(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.left_open = False
        self.right_open = False

        self._build_topbar()
        self._build_content()
        self._build_left_sidebar()
        self._build_right_panel()
        self.on_station_change()

    # ----- top bar: menu button left, profile picture right
    def _build_topbar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(14, 0))

        tk.Button(bar, text="☰", font=("Helvetica", 16), bg=BG, fg=TEXT, bd=0,
                  activebackground=CARD, activeforeground=TEXT,
                  command=self.toggle_left).pack(side="left")

        self.avatar = tk.Canvas(bar, width=44, height=44, bg=BG,
                                highlightthickness=0, cursor="hand2")
        self.avatar.pack(side="right")
        self.avatar.create_oval(2, 2, 42, 42, fill=BORDER, outline=ACCENT, width=2)
        initials = (self.user["first_name"][:1] + self.user["last_name"][:1]).upper()
        self.avatar.create_text(22, 22, text=initials, fill=TEXT, font=("Helvetica", 12, "bold"))
        self.avatar.bind("<Button-1>", lambda e: self.toggle_right())

    # ----- main content: welcome + donut, then heatmap
    def _build_content(self):
        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=28, pady=10)

        top = tk.Frame(content, bg=BG)
        top.pack(fill="x")

        welcome = tk.Frame(top, bg=BG)
        welcome.pack(side="left", anchor="n", pady=(30, 0))
        tk.Label(welcome, text=self.t("home_welcome", name=self.user["first_name"]),
                 font=("Helvetica", 24, "bold"), fg=TEXT, bg=BG).pack(anchor="w")
        tk.Label(welcome, text=self.t("home_sub"), font=("Helvetica", 11),
                 fg=MUTED, bg=BG).pack(anchor="w", pady=(4, 0))

        station_card = tk.Frame(top, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        station_card.pack(side="right", anchor="n")
        self.station_title = tk.Label(station_card, text="", font=("Helvetica", 10, "bold"),
                                      fg=TEXT, bg=CARD)
        self.station_title.pack(padx=12, pady=(8, 0))
        self.donut = tk.Label(station_card, font=("Courier", 7), fg=ACCENT, bg=CARD, justify="left")
        self.donut.pack(padx=12, pady=(2, 10))

        card = tk.Frame(content, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(24, 0))

        total = sum(self.tasks.values())
        head = tk.Frame(card, bg=CARD)
        head.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(head, text=self.t("tasks_total", n=total), font=("Helvetica", 12),
                 fg=TEXT, bg=CARD).pack(side="left")
        tk.Label(head, text=self.t("streak", n=current_streak(self.tasks)),
                 font=("Helvetica", 11, "bold"), fg=ACCENT, bg=CARD).pack(side="right")
        if total == 0:
            tk.Label(card, text=self.t("no_tasks"), font=("Helvetica", 11),
                     fg=MUTED, bg=CARD).pack(anchor="w", padx=16)

        self.heat = tk.Canvas(card, bg=CARD, highlightthickness=0)
        self.heat.pack(padx=16, anchor="w")
        self._draw_heatmap()

        legend = tk.Frame(card, bg=CARD)
        legend.pack(anchor="e", padx=16, pady=(4, 12))
        tk.Label(legend, text=self.t("less"), font=("Helvetica", 9), fg=MUTED, bg=CARD).pack(side="left")
        for col in HEAT:
            tk.Canvas(legend, width=CELL, height=CELL, bg=col,
                      highlightthickness=0).pack(side="left", padx=2)
        tk.Label(legend, text=self.t("more"), font=("Helvetica", 9), fg=MUTED, bg=CARD).pack(side="left")

    def _draw_heatmap(self):
        c = self.heat
        c.delete("all")
        today = datetime.date.today()
        # first column starts on a Sunday, 52 weeks back
        start = today - datetime.timedelta(days=52 * 7 + (today.weekday() + 1) % 7)

        for w in range(WEEKS):
            for d in range(7):
                day = start + datetime.timedelta(days=w * 7 + d)
                if day > today:
                    continue
                n = min(self.tasks.get(day, 0), len(HEAT) - 1)
                x, y = LEFT_PAD + w * PITCH, TOP_PAD + d * PITCH
                c.create_rectangle(x, y, x + CELL, y + CELL, fill=HEAT[n], outline="")
                if day.day == 1 or (w == 0 and d == 0):  # month label on the 1st, and on the first column
                    c.create_text(x, 8, text=MONTHS[self.lang][day.month - 1], anchor="w",
                                  fill=MUTED, font=("Helvetica", 8))

        for d in (1, 3, 5):
            c.create_text(0, TOP_PAD + d * PITCH + CELL / 2, text=DAY_LABELS[self.lang][d],
                          anchor="w", fill=MUTED, font=("Helvetica", 8))

        c.config(width=LEFT_PAD + WEEKS * PITCH, height=TOP_PAD + 7 * PITCH)

    # ----- left sidebar: pops up over the page, emoji per topic, closes with ✕
    def _build_left_sidebar(self):
        self.left = tk.Frame(self, bg=SIDE_BG, width=SIDEBAR_W,
                             highlightbackground=BORDER, highlightthickness=1)

        close_row = tk.Frame(self.left, bg=SIDE_BG)
        close_row.pack(fill="x", pady=(8, 0))
        tk.Button(close_row, text="✕", bg=SIDE_BG, fg=TEXT, bd=0, activebackground=BORDER,
                  activeforeground=TEXT, command=self.toggle_left).pack(side="right", padx=8)



    def toggle_left(self):
        if self.left_open:
            self.left.place_forget()
        else:
            self.left.place(x=0, y=0, relheight=1, width=SIDEBAR_W)
            self.left.lift()
        self.left_open = not self.left_open

    # ----- right panel: profile, station, crew, settings
    def _build_right_panel(self):
        self.right = tk.Frame(self, bg=SIDE_BG, width=300,
                              highlightbackground=BORDER, highlightthickness=1)

        head = tk.Frame(self.right, bg=SIDE_BG)
        head.pack(fill="x", padx=16, pady=12)
        tk.Label(head, text=self.t("profile"), font=("Helvetica", 13, "bold"),
                 fg=TEXT, bg=SIDE_BG).pack(side="left")
        tk.Button(head, text="✕", bg=SIDE_BG, fg=TEXT, bd=0, activebackground=BORDER,
                  command=self.toggle_right).pack(side="right")

        ident = tk.Frame(self.right, bg=SIDE_BG)
        ident.pack(fill="x", padx=16, pady=(4, 12))
        full_name = f"{self.user['first_name']} {self.user['last_name']}"
        tk.Label(ident, text=full_name, font=("Helvetica", 16, "bold"),
                 fg=TEXT, bg=SIDE_BG).pack(anchor="w")
        self.station_label = tk.Label(ident, text="", font=("Helvetica", 10),
                                      fg=MUTED, bg=SIDE_BG)
        self.station_label.pack(anchor="w")

        tk.Label(self.right, text=self.t("crew"), font=("Helvetica", 9, "bold"),
                 fg=MUTED, bg=SIDE_BG).pack(anchor="w", padx=16, pady=(8, 4))
        tk.Label(self.right, text=self.t("no_crew"), font=("Helvetica", 10),
                 fg=MUTED, bg=SIDE_BG).pack(anchor="w", padx=16)

        tk.Label(self.right, text=self.t("settings"), font=("Helvetica", 9, "bold"),
                 fg=MUTED, bg=SIDE_BG).pack(anchor="w", padx=16, pady=(18, 4))

        tk.Label(self.right, text=self.t("current_station"), font=("Helvetica", 10),
                 fg=TEXT, bg=SIDE_BG).pack(anchor="w", padx=16)
        for key in STATIONS:
            tk.Radiobutton(self.right, text=self.t("st_" + key), variable=self.station, value=key,
                           command=self.pick_station, bg=SIDE_BG, fg=TEXT, selectcolor=CARD,
                           activebackground=SIDE_BG, activeforeground=TEXT).pack(anchor="w", padx=24)

        tk.Checkbutton(self.right, text=self.t("reminders"), variable=self.reminders,
                       bg=SIDE_BG, fg=TEXT, selectcolor=CARD, activebackground=SIDE_BG,
                       activeforeground=TEXT).pack(anchor="w", padx=16, pady=(10, 0))
        tk.Checkbutton(self.right, text=self.t("animate"), variable=self.animate,
                       bg=SIDE_BG, fg=TEXT, selectcolor=CARD, activebackground=SIDE_BG,
                       activeforeground=TEXT).pack(anchor="w", padx=16)

        tk.Label(self.right, text=self.t("language"), font=("Helvetica", 10),
                 fg=TEXT, bg=SIDE_BG).pack(anchor="w", padx=16, pady=(14, 0))
        for code in ("en", "ar"):
            tk.Radiobutton(self.right, text=tr(code, "lang_" + code), variable=self.lang_var,
                           value=code, command=lambda: self.set_lang(self.lang_var.get()),
                           bg=SIDE_BG, fg=TEXT, selectcolor=CARD, activebackground=SIDE_BG,
                           activeforeground=TEXT).pack(anchor="w", padx=24)

    def toggle_right(self):
        if self.right_open:
            self.right.place_forget()
        else:
            self.right.place(relx=1.0, rely=0, anchor="ne", relheight=1, width=300)
            self.right.lift()
        self.right_open = not self.right_open

    # ----- settings actions
    def pick_station(self):
        store.update_user(self.user["username"], station=self.station.get())
        self.on_station_change()

    def on_station_change(self):
        name = self.station_name()
        self.station_title.config(text=self.t("orbiting", station=name))
        self.station_label.config(text=self.t("station_line", station=name))

    def set_lang(self, lang):
        """Translate the whole app: save the choice, then rebuild every screen in that language."""
        self.lang = lang
        store.update_user(self.user["username"], language=lang)
        reopen_right = self.right_open
        self.build()
        if reopen_right:
            self.toggle_right()

    # ----- donut animation loop
    def _tick(self):
        if self.animate.get():
            self.A += 0.07
            self.B += 0.03
        ramp = STATION_RAMPS[self.station.get()]
        self.donut.config(text=donut_frame(self.A, self.B, ramp))
        self.after(50, self._tick)