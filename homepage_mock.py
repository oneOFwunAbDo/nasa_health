"""
Homepage for the Space Health app.
Opened by main.py after login, with the logged-in user's saved record.
All data comes from the user's own record. Nothing is demo data.

Layout is mirrored for Arabic (right-to-left): anchors, packing sides, text
justification and the side panels all flip with the active language.
"""

import ctypes
import datetime
import math
import random
import tkinter as tk

import user_store as store
from i18n import DAY_LABELS, HAZARDS, MONTHS, STATIONS, tr
from nutrition_page import NutritionPage

# Enable High-DPI crisp rendering on Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ---------------------------------------------------------------- palette + fonts
BG = "#090d16"
CARD = "#111726"
CARD_HOVER = "#1a2234"
BORDER = "#232e42"
SIDE_BG = "#0c111d"
SPACE = "#070a10"
TEXT = "#f0f6fc"
MUTED = "#8b949e"
DISABLED = "#3a4558"
ACCENT = "#39d353"
ACCENT_DIM = "#0f291e"
ACCENT_HOVER = "#13402b"
WARN = "#f0883e"

FONT = "Segoe UI"
MONO = "Consolas"

HEAT = ["#182030", "#0e4429", "#006d32", "#26a641", "#39d353"]

# ---------------------------------------------------------------- layout numbers
PAD = 32                      # outer page padding
CELL, GAP = 13, 3
PITCH = CELL + GAP
WEEKS = 53
LEFT_PAD, TOP_PAD = 38, 22
SIDEBAR_W = 270
PROFILE_W = 320
HAZARD_W, HAZARD_H = 800, 640
RING_SIZE = 230               # progress-ring canvas (square)
RING_R = 98                   # radius of the progress ring
PLANET_R = 62                 # radius of the Moon / Mars disc

# ---------------------------------------------------------------- mission rules
TASKS_PER_DAY = 4             # placeholder tasks: "Task 1" .. "Task 4"
MISSION_LENGTH = 30           # last mission day a user can reach

TOPICS = [
    ("Fitness", "💪"),
    ("Hydration", "💧"),
    ("Sleep", "🌙"),
    ("Nutrition", "🥗"),
    ("Mindfulness", "🧘"),
    ("Medication", "💊"),
    ("Progress", "📈"),
]
TOPIC_ICONS = dict(TOPICS)

# Crater layout for the Moon: (dx, dy, radius) from the centre of the disc.
MOON_CRATERS = [(-20, -18, 11), (18, -28, 7), (24, 10, 14), (-28, 18, 8),
                (2, 30, 6), (-4, -2, 5), (34, -6, 4)]
# Dark surface regions on Mars: (dx, dy, half-width, half-height).
MARS_MARKINGS = [(-18, 4, 16, 8), (14, 18, 12, 7), (26, -8, 9, 5), (-30, -14, 7, 4)]


# ------------------------------------------------------------------ pure helpers
def current_streak(tasks, today=None):
    """
    Consecutive days with at least one completed task. If today has nothing yet,
    counting starts from yesterday, so the streak is not lost before you log today.
    """
    day = today or datetime.date.today()
    if tasks.get(day, 0) <= 0:
        day -= datetime.timedelta(days=1)
    n = 0
    while tasks.get(day, 0) > 0:
        n += 1
        day -= datetime.timedelta(days=1)
    return n


def counts_from_missions(mission_tasks, start, per_day, saved=None):
    """
    Heatmap counts (date -> tasks done) derived from the mission checklists, so
    every mission day lands on its own calendar date. `saved` (the stored heatmap)
    is used only for dates that no mission day covers.
    """
    counts = dict(saved or {})
    for key, states in mission_tasks.items():
        if not str(key).isdigit() or not isinstance(states, list) or int(key) < 1:
            continue
        date = store.mission_date(start, int(key))
        done = sum(1 for s in states[:per_day] if s)
        if done:
            counts[date] = done
        else:
            counts.pop(date, None)
    return counts


def add_hover(widget, normal_bg, hover_bg, normal_fg=None, hover_fg=None):
    """Bind background/foreground hover effects. Disabled widgets are left alone."""
    def is_disabled():
        try:
            return str(widget.cget("state")) == "disabled"
        except tk.TclError:  # frames have no state option
            return False

    def on_enter(_):
        if is_disabled():
            return
        widget.config(bg=hover_bg)
        if hover_fg:
            widget.config(fg=hover_fg)

    def on_leave(_):
        if is_disabled():
            return
        widget.config(bg=normal_bg)
        if normal_fg:
            widget.config(fg=normal_fg)

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


# ------------------------------------------------------------------ the app
class HomepageMock(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.title("Space Health")
        self.geometry("1120x820")
        self.minsize(980, 720)
        self.configure(bg=BG)

        # Merge passed user dict with the full record saved in users.json
        record = store.get_user(user["username"]) or user
        self.user = record
        self.lang = record.get("language", "en")

        # Mission state: each mission day maps to one calendar date from mission_start
        try:
            self.mission_start = datetime.date.fromisoformat(record["mission_start"])
        except (KeyError, ValueError):
            self.mission_start = datetime.date.today()
        self.mission_tasks = record.get("mission_tasks", {})

        saved = {}
        for key, value in record.get("tasks", {}).items():
            try:
                saved[datetime.date.fromisoformat(key)] = int(value)
            except ValueError:
                continue
        self.tasks = counts_from_missions(
            self.mission_tasks, self.mission_start, TASKS_PER_DAY, saved
        )
        self.mission_day = self._clamp_day(int(record.get("current_mission_day", 1)))

        # Settings state (persisted per user)
        self.station = tk.StringVar(value=record["station"])
        self.reminders = tk.BooleanVar(value=bool(record.get("reminders", True)))
        self.animate = tk.BooleanVar(value=bool(record.get("animate", True)))
        self.lang_var = tk.StringVar(value=self.lang)

        # Station graphic + hazard panel + sub-page state
        self.orbit_angle = math.pi / 2
        self.orbit_dot = None
        self.orbit_glow = None
        self.hazard_panel = None
        self.hazard_idx = None
        self.active_page = None
        rng = random.Random(42)  # fixed seed: same star field every time
        self._stars = [(rng.uniform(4, RING_SIZE - 4), rng.uniform(4, RING_SIZE - 4),
                        rng.choice((0.8, 0.8, 1.3))) for _ in range(46)]

        self.bind("<Escape>", lambda e: self.close_hazard())
        self.build()
        self._save_progress()  # writes back any migrated / re-derived progress
        self._tick()

    # ================================================================ language helpers
    def t(self, key, **kwargs):
        return tr(self.lang, key, **kwargs)

    @property
    def rtl(self):
        return self.lang == "ar"

    @property
    def start_anchor(self):
        """Anchor for text that starts at the reading edge: "e" in Arabic, "w" otherwise."""
        return "e" if self.rtl else "w"

    @property
    def near(self):
        """Pack side where the reading direction begins."""
        return "right" if self.rtl else "left"

    @property
    def far(self):
        """Pack side where the reading direction ends."""
        return "left" if self.rtl else "right"

    @property
    def just(self):
        return "right" if self.rtl else "left"

    def station_name(self):
        return self.t("st_" + self.station.get())

    # ================================================================ widget helpers
    def _label(self, parent, text="", size=10, bold=False, fg=TEXT, bg=None,
               mono=False, wrap=0, **kw):
        """Label with the right font, justification and (optional) wrapping for the language."""
        return tk.Label(
            parent, text=text, bg=bg or parent.cget("bg"), fg=fg,
            font=(MONO if mono else FONT, size, "bold" if bold else "normal"),
            justify=self.just, wraplength=wrap, **kw
        )

    @staticmethod
    def _card(parent, bg=CARD, border=BORDER):
        return tk.Frame(parent, bg=bg, highlightbackground=border, highlightthickness=1)

    @staticmethod
    def _divider(parent, padx=0, pady=0):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=padx, pady=pady)

    @staticmethod
    def _oval(canvas, cx, cy, dx, dy, rx, ry=None, **kw):
        """Oval centred at (cx+dx, cy+dy) with radii rx, ry (ry defaults to rx)."""
        ry = rx if ry is None else ry
        return canvas.create_oval(cx + dx - rx, cy + dy - ry,
                                  cx + dx + rx, cy + dy + ry, **kw)

    # ================================================================ mission day logic
    def max_mission_day(self):
        """Highest mission day the user may open: the real elapsed day, capped at the mission length."""
        return min(MISSION_LENGTH, store.elapsed_mission_day(self.mission_start))

    def _clamp_day(self, day):
        return max(1, min(day, self.max_mission_day()))

    def _get_day_checklist(self, day_num):
        """
        Checked/unchecked states for one mission day. Existing states are always kept:
        a shorter saved list is padded with unchecked items, and a longer one is left
        intact (callers only show the first TASKS_PER_DAY), so nothing saved is lost.
        """
        key = str(day_num)
        saved = self.mission_tasks.get(key)
        checklist = [bool(x) for x in saved] if isinstance(saved, list) else []
        if len(checklist) < TASKS_PER_DAY:
            checklist.extend([False] * (TASKS_PER_DAY - len(checklist)))
        self.mission_tasks[key] = checklist
        return checklist

    def _sync_day_count(self, day_num):
        """Set the heatmap count of the calendar date that mission day `day_num` maps to."""
        date = store.mission_date(self.mission_start, day_num)
        done = sum(1 for s in self._get_day_checklist(day_num)[:TASKS_PER_DAY] if s)
        if done:
            self.tasks[date] = done
        else:
            self.tasks.pop(date, None)

    def _save_progress(self):
        store.update_user(
            self.user["username"],
            tasks={d.isoformat(): v for d, v in self.tasks.items() if v > 0},
            current_mission_day=self.mission_day,
            mission_tasks=self.mission_tasks,
        )

    def change_mission_day(self, delta):
        new_day = self._clamp_day(self.mission_day + delta)
        if new_day == self.mission_day:
            return
        self.mission_day = new_day
        self._save_progress()
        self._render_mission_tasks()

    def toggle_mission_task(self, idx):
        if idx >= TASKS_PER_DAY:
            return
        checklist = self._get_day_checklist(self.mission_day)
        checklist[idx] = not checklist[idx]
        self._sync_day_count(self.mission_day)  # lands on this mission day's own date
        self._save_progress()
        self._render_mission_tasks()
        self._refresh_stats()

    # ================================================================ build the screen
    def build(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.menu_open = False
        self.profile_open = False
        self.hazard_panel = None
        self.hazard_idx = None
        self.active_page = None
        self.orbit_dot = None

        self._build_topbar()
        self._build_content()
        self._build_menu()
        self._build_profile_panel()
        self.on_station_change()

    # ----- top navigation bar
    def _build_topbar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=PAD, pady=(16, 6))

        menu_btn = tk.Button(
            bar, text="☰", font=(FONT, 15), bg=CARD, fg=TEXT, bd=0,
            padx=12, pady=4, activebackground=BORDER, activeforeground=TEXT,
            cursor="hand2", command=self.toggle_menu,
            highlightbackground=BORDER, highlightthickness=1
        )
        menu_btn.pack(side=self.near)
        add_hover(menu_btn, CARD, CARD_HOVER)

        brand = tk.Frame(bar, bg=BG)
        brand.pack(side=self.near, padx=14)
        tk.Label(brand, text="🚀", font=(FONT, 14), bg=BG, fg=ACCENT).pack(side=self.near)
        tk.Label(brand, text=self.t("app").upper(), font=(FONT, 11, "bold"),
                 bg=BG, fg=MUTED).pack(side=self.near, padx=6)

        # Profile chip: avatar on the right, name to its left, in both languages
        chip = self._card(bar)
        chip.config(cursor="hand2")
        chip.pack(side=self.far)

        self.avatar = tk.Canvas(chip, width=34, height=34, bg=CARD,
                                highlightthickness=0, cursor="hand2")
        self.avatar.pack(side="right", padx=(0, 8), pady=5)
        self.avatar.create_oval(2, 2, 32, 32, fill=ACCENT_DIM, outline=ACCENT, width=1.5)
        initials = (self.user["first_name"][:1] + self.user["last_name"][:1]).upper()
        self.avatar.create_text(17, 17, text=initials, fill=ACCENT, font=(FONT, 10, "bold"))

        name_lbl = tk.Label(chip, text=f"{self.user['first_name']} {self.user['last_name']}",
                            font=(FONT, 10, "bold"), bg=CARD, fg=TEXT)
        name_lbl.pack(side="right", padx=(14, 8), pady=6)

        for w in (chip, name_lbl, self.avatar):
            w.bind("<Button-1>", lambda e: self.toggle_profile())

        self._divider(self, padx=PAD, pady=(10, 0))

    # ----- main content: hero row + mission day task list + activity heatmap
    def _build_content(self):
        a = self.start_anchor
        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=True, padx=PAD, pady=14)

        top = tk.Frame(content, bg=BG)
        top.pack(fill="x")

        # ---- hero (welcome + stat pills)
        welcome = tk.Frame(top, bg=BG)
        welcome.pack(side=self.near, fill="both", expand=True, anchor="n")

        self._label(welcome, self.t("mission_control"), 9, True, ACCENT, mono=True).pack(anchor=a)
        self._label(welcome, self.t("home_welcome", name=self.user["first_name"]),
                    26, True).pack(anchor=a, pady=(2, 0))
        self._label(welcome, self.t("home_sub"), 11, fg=MUTED).pack(anchor=a, pady=(2, 16))

        stats_row = tk.Frame(welcome, bg=BG)
        stats_row.pack(anchor=a)
        total = sum(self.tasks.values())
        streak = current_streak(self.tasks)
        self.stat_station_val = self._make_stat_pill(
            stats_row, self.t("current_station"), self.station_name(), ACCENT)
        self.stat_streak_val = self._make_stat_pill(
            stats_row, self.t("streak", n=streak).replace("🔥 ", ""), f"🔥 {streak}", TEXT)
        self.stat_total_val = self._make_stat_pill(
            stats_row, self.t("topic_Progress"), f"{total}", TEXT)

        # ---- destination progress ring
        station_card = self._card(top)
        station_card.pack(side=self.far, anchor="n")

        head = tk.Frame(station_card, bg=CARD)
        head.pack(fill="x", padx=16, pady=(10, 8))
        tk.Label(head, text="●", font=(FONT, 9), fg=ACCENT, bg=CARD).pack(side=self.near)
        self.station_title = tk.Label(head, text="", font=(FONT, 10, "bold"), fg=TEXT, bg=CARD)
        self.station_title.pack(side=self.near, padx=(6, 6))
        self._divider(station_card)

        self.station_canvas = tk.Canvas(station_card, width=RING_SIZE, height=RING_SIZE,
                                        bg=SPACE, highlightthickness=0)
        self.station_canvas.pack(padx=14, pady=(12, 4))
        self.ring_caption = tk.Label(station_card, text="", font=(FONT, 9, "bold"),
                                     fg=MUTED, bg=CARD)
        self.ring_caption.pack(pady=(0, 12))

        # ---- mission day task card
        mission_card = self._card(content)
        mission_card.pack(fill="x", pady=(16, 0))

        m_head = tk.Frame(mission_card, bg=CARD)
        m_head.pack(fill="x", padx=22, pady=(14, 10))

        m_title_col = tk.Frame(m_head, bg=CARD)
        m_title_col.pack(side=self.near)
        self.mission_title_lbl = self._label(m_title_col, "", 13, True)
        self.mission_title_lbl.pack(anchor=a)
        # wrap so long (Arabic) text breaks inside the card instead of clipping
        self._label(m_title_col, self.t("mission_tasks_sub"), 9, fg=MUTED,
                    wrap=470).pack(anchor=a, pady=(2, 0))

        # stepper: arrows are mirrored in Arabic so "previous" always points backwards
        stepper = tk.Frame(m_head, bg=BG, highlightbackground=BORDER, highlightthickness=1)
        stepper.pack(side=self.far, anchor="center")

        self.prev_btn = self._nav_button(stepper, "▶" if self.rtl else "◀",
                                         lambda: self.change_mission_day(-1))
        self.prev_btn.pack(side=self.near)
        self.day_badge_lbl = tk.Label(stepper, text="", font=(MONO, 11, "bold"),
                                      fg=ACCENT, bg=BG, padx=14, pady=4)
        self.day_badge_lbl.pack(side=self.near)
        self.next_btn = self._nav_button(stepper, "◀" if self.rtl else "▶",
                                         lambda: self.change_mission_day(1))
        self.next_btn.pack(side=self.near)

        self.done_count_lbl = tk.Label(m_head, text="", font=(FONT, 10, "bold"),
                                       fg=ACCENT, bg=CARD, padx=14)
        self.done_count_lbl.pack(side=self.far)

        self._divider(mission_card, padx=22)
        self.tasks_row = tk.Frame(mission_card, bg=CARD)
        self.tasks_row.pack(fill="x", padx=18, pady=14)
        self._render_mission_tasks()

        # ---- heatmap card
        card = self._card(content)
        card.pack(fill="x", pady=(16, 0))

        h_head = tk.Frame(card, bg=CARD)
        h_head.pack(fill="x", padx=22, pady=(14, 4))

        self.tasks_total_lbl = self._label(h_head, self.t("tasks_total", n=total), 12, True)
        self.tasks_total_lbl.pack(side=self.near)

        badge = tk.Frame(h_head, bg=ACCENT_DIM, highlightbackground=ACCENT, highlightthickness=1)
        badge.pack(side=self.far, anchor="n")
        self.streak_badge_lbl = tk.Label(badge, text=self.t("streak", n=streak),
                                         font=(FONT, 10, "bold"), fg=ACCENT, bg=ACCENT_DIM,
                                         padx=12, pady=3)
        self.streak_badge_lbl.pack()

        self.heat = tk.Canvas(card, bg=CARD, highlightthickness=0)
        self.heat.pack(padx=22, pady=(6, 4))

        foot = tk.Frame(card, bg=CARD)
        foot.pack(fill="x", padx=22, pady=(2, 12))

        self.hover_lbl = tk.Label(foot, text="", font=(MONO, 9), fg=MUTED, bg=CARD)
        self.hover_lbl.pack(side=self.near)
        self._draw_heatmap()

        legend = tk.Frame(foot, bg=CARD)
        legend.pack(side=self.far)
        tk.Label(legend, text=self.t("less"), font=(FONT, 9), fg=MUTED,
                 bg=CARD).pack(side=self.near, padx=6)
        for col in HEAT:
            tk.Frame(legend, width=CELL, height=CELL, bg=col, highlightbackground=BORDER,
                     highlightthickness=1).pack(side=self.near, padx=2)
        tk.Label(legend, text=self.t("more"), font=(FONT, 9), fg=MUTED,
                 bg=CARD).pack(side=self.near, padx=6)

    def _make_stat_pill(self, parent, label_text, value_text, val_color):
        pill = self._card(parent)
        pill.pack(side=self.near, padx=(12, 0) if self.rtl else (0, 12), ipadx=14, ipady=6)
        self._label(pill, label_text.upper(), 8, True, MUTED).pack(anchor=self.start_anchor, padx=12)
        val = self._label(pill, value_text, 13, True, val_color)
        val.pack(anchor=self.start_anchor, padx=12, pady=(2, 0))
        return val

    def _nav_button(self, parent, glyph, command):
        btn = tk.Button(
            parent, text=glyph, font=(FONT, 10, "bold"), bg=BG, fg=TEXT,
            disabledforeground=DISABLED, bd=0, padx=10, pady=4, cursor="hand2",
            activebackground=CARD_HOVER, activeforeground=ACCENT, command=command
        )
        add_hover(btn, BG, CARD_HOVER, TEXT, ACCENT)
        return btn

    @staticmethod
    def _set_nav_state(btn, enabled):
        """Enable the arrow, or mute it (grey, no hover, normal cursor) when at the limit."""
        btn.config(state="normal" if enabled else "disabled",
                   cursor="hand2" if enabled else "arrow", bg=BG, fg=TEXT)

    # ----- mission day task list rendering
    def _render_mission_tasks(self):
        for w in self.tasks_row.winfo_children():
            w.destroy()

        states = self._get_day_checklist(self.mission_day)[:TASKS_PER_DAY]
        done_count = sum(1 for s in states if s)

        self.mission_title_lbl.config(text=self.t("mission_tasks_title", d=self.mission_day))
        self.day_badge_lbl.config(text=self.t("mission_day", d=self.mission_day))
        self.done_count_lbl.config(
            text=self.t("tasks_done_count", done=done_count, total=TASKS_PER_DAY))

        for idx, is_done in enumerate(states):
            bg_col = ACCENT_DIM if is_done else BG
            hover_col = ACCENT_HOVER if is_done else CARD_HOVER
            border_col = ACCENT if is_done else BORDER
            fg_col = ACCENT if is_done else TEXT

            item = tk.Frame(self.tasks_row, bg=bg_col, highlightbackground=border_col,
                            highlightthickness=1, cursor="hand2")
            item.pack(side=self.near, fill="x", expand=True, padx=4)
            lbl = tk.Label(item, text=f"{'☑' if is_done else '☐'}   {self.t('task_item', n=idx + 1)}",
                           font=(FONT, 11, "bold"), bg=bg_col, fg=fg_col,
                           pady=12, padx=14, anchor=self.start_anchor, justify=self.just)
            lbl.pack(fill="x")

            for widget in (item, lbl):
                widget.bind("<Button-1>", lambda e, i=idx: self.toggle_mission_task(i))
                widget.bind("<Enter>", lambda e, a=item, b=lbl, c=hover_col:
                            (a.config(bg=c), b.config(bg=c)))
                widget.bind("<Leave>", lambda e, a=item, b=lbl, c=bg_col:
                            (a.config(bg=c), b.config(bg=c)))

        self._set_nav_state(self.prev_btn, self.mission_day > 1)
        self._set_nav_state(self.next_btn, self.mission_day < self.max_mission_day())
        self._draw_station_graphic()

    def _refresh_stats(self):
        total = sum(self.tasks.values())
        streak = current_streak(self.tasks)
        self.tasks_total_lbl.config(text=self.t("tasks_total", n=total))
        self.streak_badge_lbl.config(text=self.t("streak", n=streak))
        self.stat_streak_val.config(text=f"🔥 {streak}")
        self.stat_total_val.config(text=f"{total}")
        self._draw_heatmap()

    # ----- heatmap (the time axis stays left-to-right in both languages)
    def _draw_heatmap(self):
        c = self.heat
        c.delete("all")
        today = datetime.date.today()
        start = today - datetime.timedelta(days=52 * 7 + (today.weekday() + 1) % 7)

        for w in range(WEEKS):
            for d in range(7):
                day = start + datetime.timedelta(days=w * 7 + d)
                if day > today:
                    continue
                count = self.tasks.get(day, 0)
                n = min(count, len(HEAT) - 1)
                x, y = LEFT_PAD + w * PITCH, TOP_PAD + d * PITCH
                rect = c.create_rectangle(
                    x, y, x + CELL, y + CELL,
                    fill=HEAT[n], outline=BORDER if n == 0 else "", width=1
                )
                c.tag_bind(rect, "<Enter>", lambda e, dt=day, cnt=count: self.hover_lbl.config(
                    text=self.t("heat_tip", date=dt.isoformat(), n=cnt)))
                c.tag_bind(rect, "<Leave>", lambda e: self.hover_lbl.config(text=""))

                if day.day == 1 or (w == 0 and d == 0):
                    c.create_text(x, 8, text=MONTHS[self.lang][day.month - 1], anchor="w",
                                  fill=MUTED, font=(FONT, 9))

        for d in (1, 3, 5):
            c.create_text(0, TOP_PAD + d * PITCH + CELL / 2, text=DAY_LABELS[self.lang][d],
                          anchor="w", fill=MUTED, font=(FONT, 9))

        c.config(width=LEFT_PAD + WEEKS * PITCH, height=TOP_PAD + 7 * PITCH)

    # ================================================================ destination progress ring
    def _draw_station_graphic(self):
        """Progress ring (today's mission-day tasks) around a Moon, Mars or ISS illustration."""
        c = self.station_canvas
        c.delete("all")
        cx = cy = RING_SIZE / 2

        for x, y, r in self._stars:
            c.create_oval(x - r, y - r, x + r, y + r, fill="#8b9bb8", outline="")

        done = sum(1 for s in self._get_day_checklist(self.mission_day)[:TASKS_PER_DAY] if s)
        fraction = done / TASKS_PER_DAY
        box = (cx - RING_R, cy - RING_R, cx + RING_R, cy + RING_R)
        c.create_oval(*box, outline=BORDER, width=10)
        if fraction > 0:
            c.create_arc(*box, start=90, extent=-min(fraction * 360, 359.9),
                         style="arc", outline=ACCENT, width=10)

        {"Moon": self._draw_moon, "Mars": self._draw_mars,
         "ISS": self._draw_iss}[self.station.get()](c, cx, cy)

        self.orbit_glow = c.create_oval(0, 0, 0, 0, fill=ACCENT_DIM, outline="")
        self.orbit_dot = c.create_oval(0, 0, 0, 0, fill=ACCENT, outline=SPACE, width=2)
        self._move_orbit_dot()

        self.ring_caption.config(
            text=self.t("tasks_done_count", done=done, total=TASKS_PER_DAY))

    def _draw_moon(self, c, cx, cy):
        r = PLANET_R
        self._oval(c, cx, cy, 0, 0, r, fill="#6f7580", outline="#4a505a", width=2)
        self._oval(c, cx, cy, -5, -5, r - 8, fill="#c4c8cf", outline="")  # sunlit side
        for dx, dy, cr in MOON_CRATERS:
            self._oval(c, cx, cy, dx, dy, cr, fill="#a3a9b2", outline="#80868f")
            self._oval(c, cx, cy, dx + 1, dy + 1, cr * 0.6, fill="#8f959e", outline="")

    def _draw_mars(self, c, cx, cy):
        r = PLANET_R
        self._oval(c, cx, cy, 0, 0, r, fill="#9b3a12", outline="#5e1f06", width=2)
        self._oval(c, cx, cy, -5, -5, r - 8, fill="#c9561f", outline="")  # sunlit side
        for dx, dy, rx, ry in MARS_MARKINGS:
            self._oval(c, cx, cy, dx, dy, rx, ry, fill="#8a3010", outline="")
        self._oval(c, cx, cy, 0, -52, 15, 6, fill="#f3e6da", outline="")   # north polar cap
        self._oval(c, cx, cy, 4, 56, 9, 3, fill="#e8d6c8", outline="")     # south polar cap

    def _draw_iss(self, c, cx, cy):
        # main truss
        c.create_rectangle(cx - 70, cy - 2, cx + 70, cy + 2, fill="#9aa3b0", outline="")
        # solar array pairs at both ends of the truss
        for side in (-1, 1):
            for offset in (40, 62):
                x0, x1 = sorted((cx + side * offset - 7, cx + side * offset + 7))
                c.create_rectangle(x0, cy - 26, x1, cy + 26, fill="#1c4f9c",
                                   outline="#6fb1ff")
                c.create_line((x0 + x1) / 2, cy - 26, (x0 + x1) / 2, cy + 26, fill="#3f7fd0")
                for gy in (-13, 0, 13):
                    c.create_line(x0, cy + gy, x1, cy + gy, fill="#3f7fd0")
        # radiators
        for side in (-1, 1):
            c.create_rectangle(cx + side * 14 - 5, cy + 22, cx + side * 14 + 5, cy + 46,
                               fill="#eef1f5", outline="#aab2bf")
        # pressurised modules
        c.create_rectangle(cx - 22, cy - 7, cx + 22, cy + 7, fill="#d5d9e0", outline="#8d95a3")
        c.create_rectangle(cx - 6, cy - 24, cx + 6, cy + 24, fill="#b9bfca", outline="#8d95a3")
        self._oval(c, cx, cy, 0, 0, 8, fill="#e6e9ee", outline="#8d95a3")
        c.create_line(cx, cy - 24, cx, cy - 34, fill="#aab2bf")               # antenna
        self._oval(c, cx, cy, 0, -35, 2, fill="#f0f6fc", outline="")

    def _move_orbit_dot(self):
        if self.orbit_dot is None:
            return
        cx = cy = RING_SIZE / 2
        x = cx + RING_R * math.cos(self.orbit_angle)
        y = cy - RING_R * math.sin(self.orbit_angle)
        self.station_canvas.coords(self.orbit_glow, x - 8, y - 8, x + 8, y + 8)
        self.station_canvas.coords(self.orbit_dot, x - 4.5, y - 4.5, x + 4.5, y + 4.5)

    def _tick(self):
        """Animation loop: a satellite dot circles the ring (cheap: only moves two canvas items)."""
        if self.animate.get():
            self.orbit_angle -= 0.04   # clockwise
            try:
                self._move_orbit_dot()
            except tk.TclError:
                pass
        self.after(50, self._tick)

    # ================================================================ left menu
    def _menu_button(self, text, command=None):
        btn = tk.Button(
            self.menu, text=text, font=(FONT, 10), bg=SIDE_BG, fg=TEXT, bd=0,
            anchor=self.start_anchor, justify=self.just, padx=16, pady=8,
            cursor="hand2", activebackground=CARD_HOVER, activeforeground=ACCENT,
            command=command
        )
        btn.pack(fill="x", padx=8, pady=1)
        add_hover(btn, SIDE_BG, CARD_HOVER, TEXT, ACCENT)
        return btn

    def _menu_section(self, title):
        self._label(self.menu, title, 8, True, MUTED).pack(
            anchor=self.start_anchor, padx=20, pady=(14, 4))

    def _build_menu(self):
        self.menu = tk.Frame(self, bg=SIDE_BG, width=SIDEBAR_W,
                             highlightbackground=BORDER, highlightthickness=1)

        head = tk.Frame(self.menu, bg=SIDE_BG)
        head.pack(fill="x", padx=16, pady=(18, 12))
        tk.Label(head, text=self.t("app").upper(), font=(FONT, 10, "bold"),
                 fg=ACCENT, bg=SIDE_BG).pack(side=self.near)
        tk.Button(head, text="✕", font=(FONT, 11), bg=SIDE_BG, fg=MUTED, bd=0,
                  cursor="hand2", activebackground=BORDER, activeforeground=TEXT,
                  command=self.toggle_menu).pack(side=self.far)
        self._divider(self.menu, padx=16, pady=(0, 2))

        self._menu_section(self.t("menu_topics"))
        for key, icon in TOPICS:
            name = self.t("topic_" + key)
            label = f"{name}   {icon}" if self.rtl else f"{icon}   {name}"
            cmd = self.open_nutrition if key == "Nutrition" else None
            self._menu_button(label, command=cmd)

        self._divider(self.menu, padx=16, pady=(12, 0))
        self._menu_section(self.t("hazards_menu"))
        for idx, hazard in enumerate(HAZARDS):
            short = hazard[self.lang]["short"]
            text = f"{short}   {hazard['icon']}" if self.rtl else f"{hazard['icon']}   {short}"
            self._menu_button(text, lambda i=idx: self.open_hazard(i))

    def toggle_menu(self):
        if self.menu_open:
            self.menu.place_forget()
        elif self.rtl:   # the menu opens on the reading-start edge
            self.menu.place(relx=1.0, rely=0, anchor="ne", relheight=1, width=SIDEBAR_W)
            self.menu.lift()
        else:
            self.menu.place(x=0, y=0, relheight=1, width=SIDEBAR_W)
            self.menu.lift()
        self.menu_open = not self.menu_open

    # ================================================================ nutrition sub-page
    def open_nutrition(self):
        if self.menu_open:
            self.toggle_menu()
        if self.hazard_panel is not None:
            self.close_hazard()
        if self.active_page is not None:
            self.active_page.destroy()
        self.active_page = NutritionPage(
            self,
            user=self.user,
            mission_day=self.mission_day,
            lang=self.lang,
            on_back=self.close_nutrition,
        )
        self.active_page.place(x=0, y=0, relwidth=1, relheight=1)
        self.active_page.lift()

    def close_nutrition(self):
        if self.active_page is not None:
            self.active_page.destroy()
            self.active_page = None

    # ================================================================ NASA hazards panel
    def open_hazard(self, idx):
        """Show (or switch) the RIDGE hazard panel for HAZARDS[idx]."""
        if self.menu_open:
            self.toggle_menu()
        if self.hazard_panel is not None:
            self.hazard_panel.destroy()
        self.hazard_idx = idx
        self.hazard_panel = self._make_hazard_panel(idx)
        self.hazard_panel.place(relx=0.5, rely=0.5, anchor="center",
                                width=HAZARD_W, height=HAZARD_H)
        self.hazard_panel.lift()

    def close_hazard(self):
        if self.hazard_panel is not None:
            self.hazard_panel.destroy()
            self.hazard_panel = None
            self.hazard_idx = None

    def _make_hazard_panel(self, idx):
        a = self.start_anchor
        hazard = HAZARDS[idx]
        info = hazard[self.lang]
        panel = tk.Frame(self, bg=SIDE_BG, highlightbackground=ACCENT, highlightthickness=1)

        # header: section title + close
        head = tk.Frame(panel, bg=SIDE_BG)
        head.pack(fill="x", padx=24, pady=(16, 6))
        self._label(head, self.t("hazards_title"), 9, True, MUTED).pack(side=self.near)
        tk.Button(head, text="✕", font=(FONT, 11), bg=SIDE_BG, fg=MUTED, bd=0,
                  cursor="hand2", activebackground=BORDER, activeforeground=TEXT,
                  command=self.close_hazard).pack(side=self.far)

        # interactive tabs: one per hazard
        tabs = tk.Frame(panel, bg=SIDE_BG)
        tabs.pack(fill="x", padx=21, pady=(2, 12))
        for i, h in enumerate(HAZARDS):
            active = i == idx
            tab = tk.Button(
                tabs, text=f"{h['icon']}\n{h[self.lang]['short']}", wraplength=120,
                font=(FONT, 9, "bold"), pady=8, bd=0, cursor="hand2",
                bg=ACCENT_DIM if active else CARD, fg=ACCENT if active else TEXT,
                activebackground=CARD_HOVER, activeforeground=ACCENT,
                highlightbackground=ACCENT if active else BORDER, highlightthickness=1,
                command=lambda n=i: self.open_hazard(n)
            )
            tab.pack(side=self.near, fill="x", expand=True, padx=3)
            if not active:
                add_hover(tab, CARD, CARD_HOVER, TEXT, ACCENT)

        # title + summary
        title = f"{info['name']}  {hazard['icon']}" if self.rtl else f"{hazard['icon']}  {info['name']}"
        self._label(panel, title, 20, True).pack(anchor=a, padx=24, pady=(4, 4))
        self._label(panel, info["summary"], 11, fg=MUTED, wrap=HAZARD_W - 60).pack(
            anchor=a, padx=24, pady=(0, 12))

        # risks | countermeasures
        cols = tk.Frame(panel, bg=SIDE_BG)
        cols.pack(fill="x", padx=24)
        for heading, items, color in ((self.t("hz_risks"), info["risks"], WARN),
                                      (self.t("hz_counter"), info["counter"], ACCENT)):
            box = self._card(cols)
            box.pack(side=self.near, fill="both", expand=True, padx=4)
            self._label(box, heading, 9, True, color).pack(anchor=a, padx=14, pady=(12, 6))
            for item in items:
                self._label(box, f"•  {item}", 10, wrap=325).pack(
                    anchor=a, padx=14, pady=(0, 8))

        # link to the user's daily tasks
        link = self._card(panel, bg=ACCENT_DIM, border=ACCENT)
        link.pack(fill="x", padx=28, pady=(14, 0))
        self._label(link, self.t("hz_link"), 9, True, ACCENT).pack(anchor=a, padx=14, pady=(10, 4))
        self._label(link, info["link"], 10, wrap=HAZARD_W - 90).pack(anchor=a, padx=14)
        chips = tk.Frame(link, bg=ACCENT_DIM)
        chips.pack(anchor=a, padx=14, pady=(8, 12))
        for key in hazard["topics"]:
            tk.Label(chips, text=f"{TOPIC_ICONS[key]} {self.t('topic_' + key)}",
                     font=(FONT, 9, "bold"), bg=CARD, fg=TEXT, padx=10, pady=3,
                     highlightbackground=BORDER, highlightthickness=1).pack(
                side=self.near, padx=3)
        return panel

    # ================================================================ right profile panel
    def _build_profile_panel(self):
        a = self.start_anchor
        self.profile = tk.Frame(self, bg=SIDE_BG, width=PROFILE_W,
                                highlightbackground=BORDER, highlightthickness=1)

        head = tk.Frame(self.profile, bg=SIDE_BG)
        head.pack(fill="x", padx=20, pady=(18, 12))
        tk.Label(head, text=self.t("profile").upper(), font=(FONT, 10, "bold"),
                 fg=MUTED, bg=SIDE_BG).pack(side=self.near)
        tk.Button(head, text="✕", font=(FONT, 11), bg=SIDE_BG, fg=MUTED, bd=0,
                  cursor="hand2", activebackground=BORDER, activeforeground=TEXT,
                  command=self.toggle_profile).pack(side=self.far)

        ident = self._card(self.profile)
        ident.pack(fill="x", padx=20, pady=(0, 16))
        self._label(ident, f"{self.user['first_name']} {self.user['last_name']}",
                    15, True).pack(anchor=a, padx=14, pady=(12, 2))
        self.station_label = self._label(ident, "", 10, fg=ACCENT)
        self.station_label.pack(anchor=a, padx=14, pady=(0, 12))

        self._label(self.profile, self.t("crew"), 9, True, MUTED).pack(anchor=a, padx=20, pady=(4, 4))
        crew_box = self._card(self.profile)
        crew_box.pack(fill="x", padx=20, pady=(0, 16))
        self._label(crew_box, self.t("no_crew"), 10, fg=MUTED).pack(anchor=a, padx=14, pady=10)

        self._label(self.profile, self.t("settings"), 9, True, MUTED).pack(
            anchor=a, padx=20, pady=(4, 8))
        self._label(self.profile, self.t("current_station"), 10, True).pack(
            anchor=a, padx=20, pady=(0, 4))

        for key in STATIONS:
            tk.Radiobutton(
                self.profile, text=self.t("st_" + key), variable=self.station, value=key,
                command=self.pick_station, indicatoron=0, bd=0, padx=14, pady=7,
                font=(FONT, 10, "bold"), bg=CARD, fg=TEXT, selectcolor=ACCENT,
                activebackground=CARD_HOVER, activeforeground=TEXT, cursor="hand2",
                anchor=a
            ).pack(fill="x", padx=20, pady=2)

        for text, var, top_pad in ((self.t("reminders"), self.reminders, 10),
                                   (self.t("animate"), self.animate, 2)):
            tk.Checkbutton(
                self.profile, text=text, variable=var, command=self.save_toggle_settings,
                bg=SIDE_BG, fg=TEXT, selectcolor=CARD, activebackground=SIDE_BG,
                activeforeground=TEXT, font=(FONT, 10), cursor="hand2", anchor=a,
                justify=self.just
            ).pack(fill="x", padx=20, pady=(top_pad, 2))

        self._label(self.profile, self.t("language"), 10, True).pack(
            anchor=a, padx=20, pady=(14, 4))
        lang_row = tk.Frame(self.profile, bg=SIDE_BG)
        lang_row.pack(fill="x", padx=20)
        for code in ("en", "ar"):
            tk.Radiobutton(
                lang_row, text=tr(code, "lang_" + code), variable=self.lang_var, value=code,
                command=lambda: self.set_lang(self.lang_var.get()), indicatoron=0, bd=0,
                pady=7, font=(FONT, 10, "bold"), bg=CARD, fg=TEXT, selectcolor=ACCENT,
                activebackground=CARD_HOVER, cursor="hand2"
            ).pack(side=self.near, fill="x", expand=True, padx=2)

    def toggle_profile(self):
        if self.profile_open:
            self.profile.place_forget()
        elif self.rtl:   # the profile panel opens on the reading-end edge
            self.profile.place(x=0, y=0, relheight=1, width=PROFILE_W)
            self.profile.lift()
        else:
            self.profile.place(relx=1.0, rely=0, anchor="ne", relheight=1, width=PROFILE_W)
            self.profile.lift()
        self.profile_open = not self.profile_open

    # ================================================================ settings actions
    def pick_station(self):
        store.update_user(self.user["username"], station=self.station.get())
        self.on_station_change()

    def save_toggle_settings(self):
        store.update_user(self.user["username"],
                          reminders=self.reminders.get(), animate=self.animate.get())

    def on_station_change(self):
        name = self.station_name()
        self.station_title.config(text=self.t("orbiting", station=name))
        self.station_label.config(text=self.t("station_line", station=name))
        if hasattr(self, "stat_station_val"):
            self.stat_station_val.config(text=name)
        self._draw_station_graphic()

    def set_lang(self, lang):
        """Translate and mirror the whole app: save the choice, then rebuild every screen."""
        self.lang = lang
        store.update_user(self.user["username"], language=lang)
        reopen_profile = self.profile_open
        reopen_hazard = self.hazard_idx if self.hazard_panel is not None else None
        reopen_nutrition = self.active_page is not None
        self.build()
        if reopen_nutrition:
            self.open_nutrition()
        if reopen_profile:
            self.toggle_profile()
        if reopen_hazard is not None:
            self.open_hazard(reopen_hazard)