"""
Nutrition page for the Space Health app.
Displays a unified 21-micronutrient comparison chart on the left and the 4 meal
boxes (Breakfast, Lunch, Dinner, Snacks) with dropdown selectors on the right.
"""

from pathlib import Path
import tkinter as tk
from tkinter import ttk

import user_store as store
from i18n import tr
from nutrition_data import FOOD_FILE, MEALS, MENU, load_food_nutrients
from nutrition_logic import compare, compute_intake, menu_for_day, rotation_day

# Match homepage_mock.py theme
BG = "#090d16"
CARD = "#111726"
CARD_HOVER = "#1a2234"
BORDER = "#232e42"
SPACE = "#070a10"
TEXT = "#f0f6fc"
MUTED = "#8b949e"
DISABLED = "#3a4558"
ACCENT = "#39d353"
ACCENT_DIM = "#0f291e"
ACCENT_HOVER = "#13402b"
WARN = "#f0883e"
DANGER = "#f85149"
INFO = "#58a6ff"

FONT = "Segoe UI"
MONO = "Consolas"
PAD = 28

STATUS_COLORS = {
    "low": DANGER,
    "near": WARN,
    "met": ACCENT,
    "ok": INFO,
    "over": DANGER,
}


class NutritionPage(tk.Frame):
    """
    Embedded nutrition view rendered inside HomepageMock (or any parent container).
    """

    def __init__(self, parent, user, mission_day=1, lang="en", on_back=None):
        super().__init__(parent, bg=BG)
        self.user = user
        self.mission_day = mission_day
        self.lang = lang
        self.on_back = on_back

        self.foods, self.data_mode = self._load_foods_with_fallback()
        self.all_selections = dict(self.user.get("nutrition_selections", {}))

        self._configure_dropdown_style()
        self.build()

    # ---------------------------------------------------------------- styling
    def _configure_dropdown_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Space.TCombobox",
            fieldbackground=BG,
            background=CARD_HOVER,
            foreground=TEXT,
            arrowcolor=ACCENT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=6,
        )
        style.map(
            "Space.TCombobox",
            fieldbackground=[("readonly", BG)],
            foreground=[("readonly", TEXT)],
            selectbackground=[("readonly", BG)],
            selectforeground=[("readonly", TEXT)],
            bordercolor=[("focus", ACCENT), ("hover", ACCENT)],
        )

        # Style the dropdown popdown listbox
        self.option_add("*TCombobox*Listbox.background", CARD)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT_DIM)
        self.option_add("*TCombobox*Listbox.selectForeground", ACCENT)
        self.option_add("*TCombobox*Listbox.font", (FONT, 10))

    # ---------------------------------------------------------------- helpers
    def t(self, key, **kwargs):
        return tr(self.lang, key, **kwargs)

    @property
    def rtl(self):
        return self.lang == "ar"

    @property
    def near(self):
        return "right" if self.rtl else "left"

    @property
    def far(self):
        return "left" if self.rtl else "right"

    @property
    def start_anchor(self):
        return "e" if self.rtl else "w"

    @property
    def just(self):
        return "right" if self.rtl else "left"

    @staticmethod
    def _load_foods_with_fallback():
        real = load_food_nutrients(FOOD_FILE)
        if real:
            return real, "real"
        demo_path = Path(FOOD_FILE).with_name("food_nutrients_DEMO.json")
        demo = load_food_nutrients(demo_path)
        if demo:
            return demo, "demo"
        return {}, "none"

    def _day_selection(self):
        day_key = str(self.mission_day)
        raw = self.all_selections.get(day_key)
        if not isinstance(raw, dict):
            raw = {m: {} for m in MEALS}
            self.all_selections[day_key] = raw
        for m in MEALS:
            raw.setdefault(m, {})
        return raw

    def _save_selections(self):
        self.user["nutrition_selections"] = self.all_selections
        store.update_user(self.user["username"], nutrition_selections=self.all_selections)

    def _label(self, parent, text="", size=10, bold=False, fg=TEXT, bg=None,
               mono=False, wrap=0, **kw):
        return tk.Label(
            parent, text=text, bg=bg or parent.cget("bg"), fg=fg,
            font=(MONO if mono else FONT, size, "bold" if bold else "normal"),
            justify=self.just, wraplength=wrap, **kw
        )

    @staticmethod
    def _card(parent, bg=CARD, border=BORDER):
        return tk.Frame(parent, bg=bg, highlightbackground=border, highlightthickness=1)

    # ---------------------------------------------------------------- build UI
    def build(self):
        for w in self.winfo_children():
            w.destroy()

        a = self.start_anchor
        r_day = rotation_day(self.mission_day)
        planned_kcal = MENU[r_day]["kcal"]

        # ---- Header bar
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=PAD, pady=(14, 10))

        if self.on_back:
            back_arrow = "→" if self.rtl else "←"
            back_btn = tk.Button(
                header, text=f"{back_arrow}  {self.t('back')}",
                font=(FONT, 10, "bold"), bg=CARD, fg=TEXT, bd=0,
                padx=14, pady=6, cursor="hand2",
                activebackground=CARD_HOVER, activeforeground=ACCENT,
                highlightbackground=BORDER, highlightthickness=1,
                command=self.on_back
            )
            back_btn.pack(side=self.near, padx=(14, 0) if self.rtl else (0, 14))

        title_col = tk.Frame(header, bg=BG)
        title_col.pack(side=self.near, fill="x", expand=True)
        self._label(title_col, self.t("nut_title"), 20, True).pack(anchor=a)
        self._label(
            title_col,
            self.t("nut_sub", d=self.mission_day, r=r_day),
            10, fg=MUTED
        ).pack(anchor=a, pady=(2, 0))

        actions = tk.Frame(header, bg=BG)
        actions.pack(side=self.far)

        kcal_pill = self._card(actions, bg=ACCENT_DIM, border=ACCENT)
        kcal_pill.pack(side=self.near, padx=6)
        tk.Label(
            kcal_pill, text=self.t("nut_planned_kcal", kcal=planned_kcal),
            font=(MONO, 9, "bold"), fg=ACCENT, bg=ACCENT_DIM, padx=10, pady=5
        ).pack()

        reset_btn = tk.Button(
            actions, text=self.t("nut_reset"), font=(FONT, 9, "bold"),
            bg=CARD, fg=MUTED, bd=0, padx=12, pady=5, cursor="hand2",
            activebackground=CARD_HOVER, activeforeground=WARN,
            highlightbackground=BORDER, highlightthickness=1,
            command=self.clear_day
        )
        reset_btn.pack(side=self.near, padx=(6, 0))

        if self.data_mode in ("demo", "none"):
            msg_key = "nut_demo_notice" if self.data_mode == "demo" else "nut_no_data"
            banner = self._card(self, bg="#261a0d", border=WARN)
            banner.pack(fill="x", padx=PAD, pady=(0, 8))
            self._label(banner, f"⚠  {self.t(msg_key)}", 9, True, WARN, bg="#261a0d").pack(
                anchor=a, padx=12, pady=5
            )

        # ---- Main split body: Left = Unified Chart, Right = 4 Meal Dropdown Boxes
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=PAD, pady=(2, 16))
        body.grid_columnconfigure(0, weight=11, uniform="cols")
        body.grid_columnconfigure(1, weight=10, uniform="cols")
        body.grid_rowconfigure(0, weight=1)

        self._build_chart_panel(body, col=0)
        self._build_meals_panel(body, col=1)
        self.refresh_all()

    # ---------------------------------------------------------------- Left: Unified Chart
    def _build_chart_panel(self, parent, col):
        a = self.start_anchor
        card = self._card(parent)
        card.grid(row=0, column=col, sticky="nsew", padx=(0, 8))

        head = tk.Frame(card, bg=CARD)
        head.pack(fill="x", padx=16, pady=(12, 4))
        self._label(head, self.t("nut_chart_title"), 12, True).pack(anchor=a)
        self._label(head, self.t("nut_chart_sub"), 9, fg=MUTED).pack(anchor=a, pady=(2, 0))

        legend = tk.Frame(card, bg=CARD)
        legend.pack(fill="x", padx=16, pady=(6, 4))
        for key, color in (
            ("nut_status_low", DANGER),
            ("nut_status_near", WARN),
            ("nut_status_met", ACCENT),
            ("nut_status_ok", INFO),
        ):
            item = tk.Frame(legend, bg=CARD)
            item.pack(side=self.near, padx=(0, 12))
            tk.Frame(item, width=10, height=10, bg=color).pack(side=self.near, padx=(0, 4))
            tk.Label(item, text=self.t(key), font=(FONT, 8), fg=MUTED, bg=CARD).pack(side=self.near)

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(4, 0))

        self.chart_canvas = tk.Canvas(card, bg=CARD, highlightthickness=0)
        self.chart_canvas.pack(fill="both", expand=True, padx=12, pady=(6, 4))
        self.chart_canvas.bind("<Configure>", lambda e: self._draw_chart())

        foot = tk.Frame(card, bg=CARD)
        foot.pack(fill="x", padx=16, pady=(0, 10))
        self.chart_tip_lbl = tk.Label(foot, text="", font=(MONO, 9), fg=ACCENT, bg=CARD)
        self.chart_tip_lbl.pack(anchor=a)
        self.missing_lbl = tk.Label(foot, text="", font=(FONT, 8), fg=WARN, bg=CARD)
        self.missing_lbl.pack(anchor=a)

    # ---------------------------------------------------------------- Right: 4 Meal Boxes (Dropdowns)
    def _build_meals_panel(self, parent, col):
        wrapper = tk.Frame(parent, bg=BG)
        wrapper.grid(row=0, column=col, sticky="nsew", padx=(8, 0))

        for r in range(2):
            wrapper.grid_rowconfigure(r, weight=1, uniform="meal_rows")
        for c in range(2):
            wrapper.grid_columnconfigure(c, weight=1, uniform="meal_cols")

        self.meal_selected_frames = {}   # meal -> Frame holding selected items
        self.meal_combos = {}            # meal -> (Combobox, StringVar)
        day_menu = menu_for_day(self.mission_day)

        positions = [
            ("breakfast", 0, 0),
            ("lunch", 0, 1),
            ("dinner", 1, 0),
            ("snacks", 1, 1),
        ]

        for meal, r, c in positions:
            box = self._card(wrapper)
            box.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

            m_head = tk.Frame(box, bg=CARD)
            m_head.pack(fill="x", padx=14, pady=(10, 6))
            self._label(
                m_head, self.t(f"nut_meal_{meal}").upper(), 10, True, ACCENT, mono=True
            ).pack(side=self.near)

            tk.Frame(box, bg=BORDER, height=1).pack(fill="x", padx=14)

            # Dropdown selector (<select> style)
            drop_row = tk.Frame(box, bg=CARD)
            drop_row.pack(fill="x", padx=12, pady=(10, 6))

            combo_var = tk.StringVar(value=self.t("nut_select_placeholder"))
            combo = ttk.Combobox(
                drop_row,
                textvariable=combo_var,
                values=day_menu[meal],
                state="readonly",
                style="Space.TCombobox",
                font=(FONT, 10),
                justify=self.just,
            )
            combo.pack(fill="x")
            combo.bind(
                "<<ComboboxSelected>>",
                lambda e, m=meal, cb=combo, var=combo_var: self._on_dropdown_pick(m, cb, var)
            )

            # List of selected items underneath the dropdown
            selected_list = tk.Frame(box, bg=CARD)
            selected_list.pack(fill="both", expand=True, padx=12, pady=(2, 10))

            self.meal_combos[meal] = (combo, combo_var)
            self.meal_selected_frames[meal] = selected_list

    # ---------------------------------------------------------------- interactions
    def _on_dropdown_pick(self, meal, combo, combo_var):
        chosen = combo_var.get()
        if not chosen or chosen == self.t("nut_select_placeholder"):
            return
        sel = self._day_selection()
        sel[meal][chosen] = float(sel[meal].get(chosen, 0.0)) + 1.0
        self._save_selections()
        # Reset dropdown display back to placeholder so more items can be picked easily
        combo.set(self.t("nut_select_placeholder"))
        self.refresh_all()

    def adjust_serving(self, meal, food, delta):
        sel = self._day_selection()
        cur = float(sel[meal].get(food, 0.0))
        nxt = max(0.0, cur + delta)
        if nxt <= 0:
            sel[meal].pop(food, None)
        else:
            sel[meal][food] = nxt
        self._save_selections()
        self.refresh_all()

    def remove_food(self, meal, food):
        sel = self._day_selection()
        sel[meal].pop(food, None)
        self._save_selections()
        self.refresh_all()

    def clear_day(self):
        self.all_selections[str(self.mission_day)] = {m: {} for m in MEALS}
        self._save_selections()
        self.refresh_all()

    # ---------------------------------------------------------------- rendering updates
    def refresh_all(self):
        sel = self._day_selection()

        # Render selected items inside each meal box underneath its dropdown
        for meal, container in self.meal_selected_frames.items():
            for w in container.winfo_children():
                w.destroy()

            items = [(f, q) for f, q in sel.get(meal, {}).items() if q > 0]
            for food, qty in items:
                chip = tk.Frame(
                    container, bg=ACCENT_DIM,
                    highlightbackground=ACCENT, highlightthickness=1
                )
                chip.pack(fill="x", pady=2)

                # Controls on far edge: [ - ] qty [ + ] [ ✕ ]
                ctrl = tk.Frame(chip, bg=ACCENT_DIM)
                ctrl.pack(side=self.far, padx=4, pady=2)

                tk.Button(
                    ctrl, text="−", font=(FONT, 8, "bold"), width=2, bd=0,
                    bg=CARD, fg=TEXT, cursor="hand2",
                    activebackground=CARD_HOVER, activeforeground=WARN,
                    command=lambda m=meal, f=food: self.adjust_serving(m, f, -1.0)
                ).pack(side="left")

                qty_txt = f"{int(qty)}x" if float(qty).is_integer() else f"{qty:.1f}x"
                tk.Label(
                    ctrl, text=qty_txt, font=(MONO, 8, "bold"), width=3,
                    bg=ACCENT_DIM, fg=ACCENT
                ).pack(side="left", padx=2)

                tk.Button(
                    ctrl, text="+", font=(FONT, 8, "bold"), width=2, bd=0,
                    bg=CARD, fg=ACCENT, cursor="hand2",
                    activebackground=ACCENT_HOVER, activeforeground=ACCENT,
                    command=lambda m=meal, f=food: self.adjust_serving(m, f, 1.0)
                ).pack(side="left")

                tk.Button(
                    ctrl, text="✕", font=(FONT, 8, "bold"), width=2, bd=0,
                    bg=ACCENT_DIM, fg=MUTED, cursor="hand2",
                    activebackground=ACCENT_HOVER, activeforeground=DANGER,
                    command=lambda m=meal, f=food: self.remove_food(m, f)
                ).pack(side="left", padx=(2, 0))

                tk.Label(
                    chip, text=food, font=(FONT, 9, "bold"),
                    bg=ACCENT_DIM, fg=ACCENT,
                    anchor=self.start_anchor, justify=self.just
                ).pack(side=self.near, fill="x", expand=True, padx=(8, 4), pady=3)

        # Recalculate all 21 micronutrients and update the unified chart
        totals, missing = compute_intake(sel, self.foods)
        self.comparison_rows = compare(totals)

        if missing:
            self.missing_lbl.config(text=self.t("nut_missing_warn", items=", ".join(missing)))
        else:
            self.missing_lbl.config(text="")

        self._draw_chart()

    def _draw_chart(self):
        c = self.chart_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 120 or h < 120 or not hasattr(self, "comparison_rows"):
            return

        rows = self.comparison_rows
        n = len(rows)

        left_margin = 138
        right_margin = 76
        top_margin = 22
        bottom_margin = 14
        plot_w = max(80, w - left_margin - right_margin)
        plot_h = max(80, h - top_margin - bottom_margin)
        row_h = plot_h / n

        max_pct = max([120.0] + [r["percent"] for r in rows])
        scale_max = min(200.0, max(120.0, (int(max_pct // 20) + 1) * 20))

        def x_for_pct(pct):
            clamped = max(0.0, min(pct, scale_max))
            return left_margin + (clamped / scale_max) * plot_w

        for tick in (0, 50, 100, int(scale_max)):
            if tick > scale_max:
                continue
            tx = x_for_pct(tick)
            is_target = tick == 100
            c.create_line(
                tx, top_margin - 4, tx, top_margin + plot_h,
                fill=ACCENT if is_target else BORDER,
                width=1.5 if is_target else 1,
                dash=() if is_target else (3, 3)
            )
            c.create_text(
                tx, top_margin - 12, text=f"{tick}%",
                fill=ACCENT if is_target else MUTED,
                font=(MONO, 8, "bold" if is_target else "normal")
            )

        bar_h = max(6, min(14, row_h * 0.58))
        for idx, r in enumerate(rows):
            cy = top_margin + (idx + 0.5) * row_h
            y0 = cy - bar_h / 2
            y1 = cy + bar_h / 2

            label_text = r["name_ar"] if self.rtl else r["name_en"]
            c.create_text(
                left_margin - 8, cy, text=label_text,
                anchor="e", fill=TEXT, font=(FONT, 8)
            )

            c.create_rectangle(
                left_margin, y0, left_margin + plot_w, y1,
                fill=SPACE, outline=""
            )

            bar_x1 = x_for_pct(r["percent"])
            color = STATUS_COLORS.get(r["status"], ACCENT)
            if r["percent"] > 0:
                bar = c.create_rectangle(
                    left_margin, y0, max(left_margin + 2, bar_x1), y1,
                    fill=color, outline=""
                )
            else:
                bar = c.create_rectangle(
                    left_margin, y0, left_margin + plot_w, y1,
                    fill="", outline=""
                )

            pct_str = f"{r['percent']:.0f}%"
            c.create_text(
                left_margin + plot_w + 8, cy,
                text=f"{pct_str:>4}  ({r['amount']:.0f}/{r['target']}{r['unit']})",
                anchor="w", fill=color if r["percent"] > 0 else MUTED,
                font=(MONO, 8)
            )

            tip = self.t(
                "nut_tip",
                name=label_text,
                amount=r["amount"],
                target=r["target"],
                unit=r["unit"],
                pct=r["percent"],
            )
            c.tag_bind(bar, "<Enter>", lambda e, msg=tip: self.chart_tip_lbl.config(text=msg))
            c.tag_bind(bar, "<Leave>", lambda e: self.chart_tip_lbl.config(text=""))