# app_ui.py — Launch the GestureX desktop UI

from ui.font_loader import load_fonts, unload_fonts
from ui.app import GestureApp


def main():
    load_fonts()  # register bundled IBM Plex Mono before any widgets
    try:
        app = GestureApp()
        app.mainloop()
    finally:
        unload_fonts()  # clean up font resources


if __name__ == "__main__":
    main()
