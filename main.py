import sys
from PyQt6.QtWidgets import QApplication
from auth import auto_login
from hud import HUDWindow
from login_window import LoginWindow

def main():
    app = QApplication(sys.argv)

    try:
        # 자동로그인 시도
        user_data = auto_login()
        # 성공시 HUD 실행
        window = HUDWindow(user_data)
    except Exception as e:
        print(f"자동로그인 실패 : {e}")
        # 실패시 로그인 창 실행
        window = LoginWindow()

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()