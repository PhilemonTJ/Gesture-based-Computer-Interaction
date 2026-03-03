# ui/settings.py — Settings modal

import customtkinter as ctk
from ui.theme import *
from core.config import Config
from ui.engine import GestureEngine


class SettingsModal(ctk.CTkToplevel):
    """Settings overlay with camera, sensitivity, and gesture toggle controls."""

    def __init__(self, parent, config: Config, engine: GestureEngine):
        super().__init__(parent)
        self.config = config
        self.engine = engine

        # ── Window ──
        self.title("Settings")
        self.geometry("700x580")
        self.configure(fg_color=SURFACE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 580) // 2
        self.geometry(f"+{x}+{y}")

        self._build()

    def _build(self):
        # Title
        title = ctk.CTkLabel(
            self, text="Settings", font=(FONT_FAMILY, 18, "bold"),
            text_color=LIGHT
        )
        title.pack(padx=24, pady=(20, 16), anchor="w")

        # ── Top row: Camera + Sensitivity (side by side) ──
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(padx=24, fill="x")
        top_row.grid_columnconfigure(0, weight=1)
        top_row.grid_columnconfigure(1, weight=1)

        self._build_camera_section(top_row)
        self._build_sensitivity_section(top_row)

        # ── Gesture Controls ──
        self._build_toggles()

        # ── Bottom buttons ──
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=24, pady=(16, 20), fill="x")

        ctk.CTkButton(
            btn_frame, text="Cancel", font=(FONT_FAMILY, 11),
            fg_color=SURFACE2, hover_color=BORDER2,
            border_width=1, border_color=BORDER,
            text_color=LIGHT, width=120, height=38, corner_radius=6,
            command=self.destroy
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="Save Settings", font=(FONT_FAMILY, 11, "bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="white", width=140, height=38, corner_radius=6,
            command=self._save
        ).pack(side="right")

    # ==================================================================
    #  CAMERA SETTINGS
    # ==================================================================
    def _build_camera_section(self, parent):
        card = ctk.CTkFrame(parent, fg_color=SURFACE2, corner_radius=8,
                             border_width=1, border_color=BORDER)
        card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(
            card, text="Camera Settings", font=(FONT_FAMILY, 13, "bold"),
            text_color=LIGHT
        ).pack(padx=16, pady=(16, 12), anchor="w")

        # Resolution
        ctk.CTkLabel(card, text="Resolution", font=(FONT_FAMILY, 10),
                      text_color=MID).pack(padx=16, anchor="w")
        self.resolution_var = ctk.StringVar(value=f"{self.config.CAM_WIDTH} × {self.config.CAM_HEIGHT}")
        ctk.CTkOptionMenu(
            card, variable=self.resolution_var,
            values=["640 × 480", "1280 × 720"],
            fg_color=BLACK, button_color=DEEP, button_hover_color=BORDER2,
            dropdown_fg_color=SURFACE, dropdown_hover_color=BORDER2,
            text_color=LIGHT, font=(FONT_FAMILY, 11), width=200
        ).pack(padx=16, pady=(4, 12), anchor="w")

        # FPS
        self.fps_label = ctk.CTkLabel(card, text=f"FPS: {self.config.CAM_FPS}",
                                       font=(FONT_FAMILY, 10), text_color=MID)
        self.fps_label.pack(padx=16, anchor="w")
        self.fps_slider = ctk.CTkSlider(
            card, from_=15, to=60, number_of_steps=9,
            fg_color=BLACK, progress_color=ACCENT, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER, width=200,
            command=lambda v: self.fps_label.configure(text=f"FPS: {int(v)}")
        )
        self.fps_slider.set(self.config.CAM_FPS)
        self.fps_slider.pack(padx=16, pady=(4, 12), anchor="w")

        # Show landmarks toggle
        self.landmarks_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            card, text="Show Hand Landmarks",
            font=(FONT_FAMILY, 10), text_color=LIGHT,
            fg_color=BLACK, progress_color=ACCENT,
            variable=self.landmarks_var
        ).pack(padx=16, pady=(0, 16), anchor="w")

    # ==================================================================
    #  SENSITIVITY SETTINGS
    # ==================================================================
    def _build_sensitivity_section(self, parent):
        card = ctk.CTkFrame(parent, fg_color=SURFACE2, corner_radius=8,
                             border_width=1, border_color=BORDER)
        card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(
            card, text="Sensitivity Settings", font=(FONT_FAMILY, 13, "bold"),
            text_color=LIGHT
        ).pack(padx=16, pady=(16, 12), anchor="w")

        # Cursor speed
        self.cursor_label = ctk.CTkLabel(
            card, text=f"Cursor Speed: {int(self.config.FILTER_MIN_CUTOFF * 100)}%",
            font=(FONT_FAMILY, 10), text_color=MID
        )
        self.cursor_label.pack(padx=16, anchor="w")
        self.cursor_slider = ctk.CTkSlider(
            card, from_=0.2, to=3.0,
            fg_color=BLACK, progress_color=ACCENT, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER, width=200,
            command=lambda v: self.cursor_label.configure(
                text=f"Cursor Speed: {int(v * 100 / 3)}%")
        )
        self.cursor_slider.set(self.config.FILTER_MIN_CUTOFF)
        self.cursor_slider.pack(padx=16, pady=(4, 4), anchor="w")

        sub_row = ctk.CTkFrame(card, fg_color="transparent")
        sub_row.pack(padx=16, fill="x", pady=(0, 12))
        ctk.CTkLabel(sub_row, text="Slow", font=(FONT_FAMILY, 8), text_color=DEEP).pack(side="left")
        ctk.CTkLabel(sub_row, text="Fast", font=(FONT_FAMILY, 8), text_color=DEEP).pack(side="right")

        # Click threshold
        self.click_label = ctk.CTkLabel(
            card, text=f"Click Distance: {self.config.JOIN_THRESHOLD}px",
            font=(FONT_FAMILY, 10), text_color=MID
        )
        self.click_label.pack(padx=16, anchor="w")
        self.click_slider = ctk.CTkSlider(
            card, from_=20, to=80, number_of_steps=12,
            fg_color=BLACK, progress_color=ACCENT, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER, width=200,
            command=lambda v: self.click_label.configure(
                text=f"Click Distance: {int(v)}px")
        )
        self.click_slider.set(self.config.JOIN_THRESHOLD)
        self.click_slider.pack(padx=16, pady=(4, 4), anchor="w")

        sub_row2 = ctk.CTkFrame(card, fg_color="transparent")
        sub_row2.pack(padx=16, fill="x", pady=(0, 12))
        ctk.CTkLabel(sub_row2, text="Less Sensitive", font=(FONT_FAMILY, 8), text_color=DEEP).pack(side="left")
        ctk.CTkLabel(sub_row2, text="More Sensitive", font=(FONT_FAMILY, 8), text_color=DEEP).pack(side="right")

        # Volume sensitivity
        self.vol_label = ctk.CTkLabel(
            card, text=f"Volume Sensitivity: {int(self.config.KNOB_STEP_ANGLE)}°",
            font=(FONT_FAMILY, 10), text_color=MID
        )
        self.vol_label.pack(padx=16, anchor="w")
        self.vol_slider = ctk.CTkSlider(
            card, from_=3, to=25, number_of_steps=22,
            fg_color=BLACK, progress_color=ACCENT, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER, width=200,
            command=lambda v: self.vol_label.configure(
                text=f"Volume Sensitivity: {int(v)}°")
        )
        self.vol_slider.set(self.config.KNOB_STEP_ANGLE)
        self.vol_slider.pack(padx=16, pady=(4, 4), anchor="w")

        sub_row3 = ctk.CTkFrame(card, fg_color="transparent")
        sub_row3.pack(padx=16, fill="x", pady=(0, 16))
        ctk.CTkLabel(sub_row3, text="Low", font=(FONT_FAMILY, 8), text_color=DEEP).pack(side="left")
        ctk.CTkLabel(sub_row3, text="High", font=(FONT_FAMILY, 8), text_color=DEEP).pack(side="right")

    # ==================================================================
    #  GESTURE TOGGLES
    # ==================================================================
    def _build_toggles(self):
        card = ctk.CTkFrame(self, fg_color=SURFACE2, corner_radius=8,
                             border_width=1, border_color=BORDER)
        card.pack(padx=24, pady=(12, 0), fill="x")

        ctk.CTkLabel(
            card, text="Gesture Controls", font=(FONT_FAMILY, 13, "bold"),
            text_color=LIGHT
        ).pack(padx=16, pady=(16, 8), anchor="w")

        toggles_frame = ctk.CTkFrame(card, fg_color="transparent")
        toggles_frame.pack(padx=16, pady=(0, 16), fill="x")

        # Two columns of toggles
        self.toggle_vars = {}
        labels = [
            ("cursor", "Cursor Movement"),
            ("left_click", "Left Click"),
            ("right_click", "Right Click"),
            ("drag", "Drag & Drop"),
            ("scroll", "Scroll"),
            ("volume", "Volume Control"),
            ("screenshot", "Screenshot"),
        ]

        for i, (key, text) in enumerate(labels):
            col = i % 2
            row = i // 2
            var = ctk.BooleanVar(value=self.engine.toggles.get(key, True))
            self.toggle_vars[key] = var

            sw = ctk.CTkSwitch(
                toggles_frame, text=text,
                font=(FONT_FAMILY, 10), text_color=LIGHT,
                fg_color=BLACK, progress_color=ACCENT,
                variable=var, width=200
            )
            sw.grid(row=row, column=col, padx=(0, 24), pady=4, sticky="w")

    # ==================================================================
    #  SAVE
    # ==================================================================
    def _save(self):
        # Update config values
        res = self.resolution_var.get()
        if "1280" in res:
            self.config.CAM_WIDTH = 1280
            self.config.CAM_HEIGHT = 720
        else:
            self.config.CAM_WIDTH = 640
            self.config.CAM_HEIGHT = 480

        self.config.CAM_FPS = int(self.fps_slider.get())
        self.config.FILTER_MIN_CUTOFF = round(self.cursor_slider.get(), 2)
        self.config.JOIN_THRESHOLD = int(self.click_slider.get())
        self.config.KNOB_STEP_ANGLE = round(self.vol_slider.get(), 1)

        # Update gesture toggles
        for key, var in self.toggle_vars.items():
            self.engine.toggles[key] = var.get()

        self.destroy()
