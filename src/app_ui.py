# app_ui.py — Launch the GestureX desktop UI

from ui.app import GestureApp


def main():
    app = GestureApp()
    app.mainloop()


if __name__ == "__main__":
    main()
