# ui/app.py — Main application window

import customtkinter as ctk
from PIL import Image, ImageTk
from pathlib import Path
from ui.theme import *
from ui.engine import GestureEngine
from core.config import Config
from core import preferences


class GestureApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ── Window setup ──
        # Set window size and disable resizing
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.title("GestureX")
        self.minsize(800, 500)
        self.configure(fg_color=BLACK)

        # Set window icon
        import sys
        if getattr(sys, "frozen", False):
            icon_path = Path(sys._MEIPASS) / "logo.ico"
        else:
            icon_path = Path(__file__).resolve().parent.parent.parent / "logo.ico"

        if icon_path.exists():
            self.iconbitmap(str(icon_path))

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Engine ──
        self.config_obj = Config()
        self.engine = GestureEngine(self.config_obj)
        self._show_preview = True  # camera preview toggle

        # ── Build UI ──
        self._build_layout()

        # ── Polling loop for live updates ──
        self._poll_interval = 33  # ~30 FPS
        self._poll()

        # ── Handle window close ──
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ==================================================================
    #  LAYOUT
    # ==================================================================
    def _build_layout(self):
        # Main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)

        # ── LEFT: Camera area ──
        self.camera_frame = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=2,
                                          border_width=1, border_color=BORDER)
        self.camera_frame.grid(row=0, column=0, padx=(16, 8), pady=(16, 8), sticky="nsew")
        self.camera_frame.grid_rowconfigure(0, weight=1)
        self.camera_frame.grid_columnconfigure(0, weight=1)

        # Camera preview label
        self.camera_label = ctk.CTkLabel(
            self.camera_frame, text="",
            fg_color=BLACK, corner_radius=2
        )
        self.camera_label.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")

        # Status overlay (centered on camera area)
        self.status_frame = ctk.CTkFrame(self.camera_label, fg_color="transparent")
        self.status_frame.place(relx=0.5, rely=0.45, anchor="center")

        self.status_dot = ctk.CTkLabel(
            self.status_frame, text="●", font=(FONT_FAMILY, 24),
            text_color=DEEP, fg_color="transparent"
        )
        self.status_dot.pack(side="left", padx=(0, 8))

        self.status_label = ctk.CTkLabel(
            self.status_frame, text="System Status: INACTIVE",
            font=(FONT_FAMILY, 16, "bold"), text_color=LIGHT,
            fg_color="transparent"
        )
        self.status_label.pack(side="left")

        # ── RIGHT: Sidebar ──
        self.sidebar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=2,
                                     border_width=1, border_color=BORDER,
                                     width=SIDEBAR_WIDTH)
        self.sidebar.grid(row=0, column=1, padx=(8, 16), pady=(16, 8), sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.pack_propagate(False)

        self._build_sidebar()

        # ── BOTTOM: Control buttons ──
        self.controls_frame = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=2,
                                            border_width=1, border_color=BORDER)
        self.controls_frame.grid(row=1, column=0, columnspan=2,
                                  padx=16, pady=(8, 4), sticky="ew")
        self._build_controls()

        # ── FOOTER ──
        self.footer = ctk.CTkLabel(
            self, text="TOUCH-FREE HUMAN COMPUTER INTERACTION SYSTEM",
            font=(FONT_FAMILY, 9), text_color=DEEP, fg_color="transparent"
        )
        self.footer.grid(row=2, column=0, columnspan=2, pady=(2, 8))

    # ==================================================================
    #  SIDEBAR
    # ==================================================================
    def _build_sidebar(self):
        title = ctk.CTkLabel(
            self.sidebar, text="System Info",
            font=(FONT_FAMILY, 12, "bold"), text_color=LIGHT,
            anchor="w"
        )
        title.pack(padx=16, pady=(16, 12), anchor="w")

        # Info cards
        self.card_camera = self._create_info_card("📷  Camera", "Checking...")
        self.card_fps = self._create_info_card("⚡  FPS", "0")
        self.card_hand = self._create_info_card("🖐  Hand Detection", "Inactive")
        self.card_gesture = self._create_info_card("🎯  Current Gesture", "None")

        # Settings button at bottom
        settings_btn = ctk.CTkButton(
            self.sidebar, text="⚙  SETTINGS",
            font=(FONT_FAMILY, 10, "bold"), height=36,
            fg_color=SURFACE2, hover_color=BORDER2,
            border_width=1, border_color=BORDER,
            text_color=LIGHT, corner_radius=2,
            command=self._open_settings
        )
        settings_btn.pack(padx=16, pady=(16, 16), fill="x", side="bottom")

    def _create_info_card(self, title: str, value: str):
        card = ctk.CTkFrame(self.sidebar, fg_color=SURFACE2, corner_radius=2,
                             border_width=1, border_color=BORDER)
        card.pack(padx=16, pady=(0, 8), fill="x")

        lbl_title = ctk.CTkLabel(
            card, text=title, font=(FONT_FAMILY, 9),
            text_color=MID, anchor="w"
        )
        lbl_title.pack(padx=12, pady=(10, 2), anchor="w")

        lbl_value = ctk.CTkLabel(
            card, text=value, font=(FONT_FAMILY, 18, "bold"),
            text_color=LIGHT, anchor="w"
        )
        lbl_value.pack(padx=12, pady=(0, 10), anchor="w")

        return lbl_value  # return the value label for live updates

    # ==================================================================
    #  CONTROLS
    # ==================================================================
    def _build_controls(self):
        inner = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        inner.pack(padx=16, pady=12)

        self.btn_start = ctk.CTkButton(
            inner, text="▶  START GESTURE CONTROL",
            font=(FONT_FAMILY, 10, "bold"), height=42, width=260,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            border_width=1, border_color=BORDER2,
            text_color=LIGHT, corner_radius=2,
            command=self._on_start
        )
        self.btn_start.pack(side="left", padx=(0, 12))

        self.btn_pause = ctk.CTkButton(
            inner, text="⏸  PAUSE", font=(FONT_FAMILY, 10),
            height=42, width=120,
            fg_color=SURFACE2, hover_color=BORDER2,
            border_width=1, border_color=BORDER,
            text_color=LIGHT, corner_radius=2,
            command=self._on_pause, state="disabled"
        )
        self.btn_pause.pack(side="left", padx=(0, 8))

        self.btn_stop = ctk.CTkButton(
            inner, text="⏹  STOP", font=(FONT_FAMILY, 10),
            height=42, width=120,
            fg_color=SURFACE2, hover_color=BORDER2,
            border_width=1, border_color=BORDER,
            text_color=LIGHT, corner_radius=2,
            command=self._on_stop, state="disabled"
        )
        self.btn_stop.pack(side="left", padx=(0, 8))

        self.btn_preview = ctk.CTkButton(
            inner, text="📷  HIDE CAMERA", font=(FONT_FAMILY, 10),
            height=42, width=150,
            fg_color=SURFACE2, hover_color=BORDER2,
            border_width=1, border_color=BORDER,
            text_color=LIGHT, corner_radius=2,
            command=self._toggle_preview, state="disabled"
        )
        self.btn_preview.pack(side="left")

    # ==================================================================
    #  BUTTON HANDLERS
    # ==================================================================
    def _on_start(self):
        # Check camera permission before starting
        if preferences.get("camera_always_allow"):
            self._start_engine()
        else:
            self._show_camera_permission()

    def _start_engine(self):
        """Actually start the gesture engine."""
        self.engine.start()
        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        self.btn_stop.configure(state="normal")
        self.btn_preview.configure(state="normal")

    def _show_camera_permission(self):
        """Show a camera permission dialog matching the app theme."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Camera Access")
        dialog.geometry("420x260")
        dialog.configure(fg_color=SURFACE)
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Set icon
        import sys
        if getattr(sys, "frozen", False):
            icon_path = Path(sys._MEIPASS) / "logo.ico"
        else:
            icon_path = Path(__file__).resolve().parent.parent.parent / "logo.ico"

        if icon_path.exists():
            dialog.after(200, lambda: dialog.iconbitmap(str(icon_path)))

        # Center on parent
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 420) // 2
        y = self.winfo_y() + (self.winfo_height() - 260) // 2
        dialog.geometry(f"+{x}+{y}")

        # Title
        ctk.CTkLabel(
            dialog, text="📷  CAMERA ACCESS REQUIRED",
            font=(FONT_FAMILY, 14, "bold"), text_color=LIGHT
        ).pack(padx=24, pady=(24, 8), anchor="w")

        # Description
        ctk.CTkLabel(
            dialog,
            text="GestureX needs access to your camera\nto detect hand gestures.",
            font=(FONT_FAMILY, 11), text_color=MID,
            justify="left"
        ).pack(padx=24, pady=(0, 16), anchor="w")

        # Separator
        ctk.CTkFrame(dialog, fg_color=BORDER, height=1).pack(
            padx=24, fill="x", pady=(0, 16)
        )

        # Always allow checkbox
        always_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            dialog, text="Always allow (don't ask again)",
            font=(FONT_FAMILY, 10), text_color=LIGHT,
            fg_color=BLACK, hover_color=BORDER2,
            checkmark_color=LIGHT, border_color=BORDER,
            variable=always_var
        ).pack(padx=24, pady=(0, 20), anchor="w")

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(padx=24, pady=(0, 24), fill="x")

        def on_allow():
            if always_var.get():
                preferences.set("camera_always_allow", True)
            dialog.destroy()
            self._start_engine()

        ctk.CTkButton(
            btn_frame, text="ALLOW", font=(FONT_FAMILY, 10, "bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            border_width=1, border_color=BORDER2,
            text_color=LIGHT, width=120, height=38, corner_radius=2,
            command=on_allow
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_frame, text="DENY", font=(FONT_FAMILY, 10),
            fg_color=SURFACE2, hover_color=BORDER2,
            border_width=1, border_color=BORDER,
            text_color=LIGHT, width=120, height=38, corner_radius=2,
            command=dialog.destroy
        ).pack(side="right")

    def _on_pause(self):
        if self.engine._paused:
            self.engine.resume()
            self.btn_pause.configure(text="⏸  PAUSE")
        else:
            self.engine.pause()
            self.btn_pause.configure(text="▶  RESUME")

    def _on_stop(self):
        self.engine.stop()
        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled", text="⏸  PAUSE")
        self.btn_stop.configure(state="disabled")
        self.btn_preview.configure(state="disabled", text="📷  HIDE CAMERA")
        self._show_preview = True
        # Clear camera preview
        self.camera_label.configure(image=None)
        self.status_frame.place(relx=0.5, rely=0.45, anchor="center")
        self._update_status("INACTIVE")

    def _toggle_preview(self):
        self._show_preview = not self._show_preview
        if self._show_preview:
            self.btn_preview.configure(text="📷  HIDE CAMERA")
        else:
            self.btn_preview.configure(text="📷  SHOW CAMERA")
            self.camera_label.configure(image=None)
            self.camera_label._image = None
            self.status_frame.place(relx=0.5, rely=0.45, anchor="center")
            self._update_status(self.engine.state["status"])

    def _on_close(self):
        self.engine.stop()
        self.destroy()

    def _open_settings(self):
        from ui.settings import SettingsModal
        SettingsModal(self, self.config_obj, self.engine)

    # ==================================================================
    #  POLLING (reads engine.state every 33ms)
    # ==================================================================
    def _poll(self):
        state = self.engine.state

        # Update status
        self._update_status(state["status"])

        # Update sidebar cards
        status = state["status"]
        if status == "INACTIVE":
            cam_text = "Ready"
        elif status == "CONNECTING":
            cam_text = "Connecting..."
        else:
            cam_text = "Connected"
        self.card_camera.configure(text=cam_text)
        self.card_fps.configure(text=str(state["fps"]))

        hand_text = "Active" if state["hand_detected"] else "Inactive"
        hand_color = GREEN if state["hand_detected"] else MID
        self.card_hand.configure(text=hand_text, text_color=hand_color)

        self.card_gesture.configure(text=state["gesture"])

        # Update camera frame (only if preview is on)
        frame = state.get("frame")
        if frame is not None and self._show_preview:
            self.status_frame.place_forget()

            self.camera_label.update_idletasks()
            label_w = max(self.camera_label.winfo_width(), 320)
            label_h = max(self.camera_label.winfo_height(), 240)
            frame_resized = frame.resize((label_w, label_h), Image.LANCZOS)

            photo = ImageTk.PhotoImage(frame_resized)
            self.camera_label.configure(image=photo)
            self.camera_label._image = photo

        # Schedule next poll
        self.after(self._poll_interval, self._poll)

    def _update_status(self, status: str):
        if status == "ACTIVE":
            self.status_dot.configure(text_color=LIGHT)
            self.status_label.configure(text=f"System Status: {status}")
        elif status == "PAUSED":
            self.status_dot.configure(text_color=MID)
            self.status_label.configure(text=f"System Status: {status}")
        elif status == "CONNECTING":
            self.status_dot.configure(text_color=MID)
            self.status_label.configure(text="System Status: CONNECTING...")
        else:
            self.status_dot.configure(text_color=DEEP)
            self.status_label.configure(text=f"System Status: {status}")
            self.status_frame.place(relx=0.5, rely=0.45, anchor="center")
