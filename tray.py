import threading
from pystray import Icon, Menu, MenuItem
from PyQt6.QtCore import QMetaObject, Qt
from PIL import Image


class TrayIcon:
    def __init__(self, window):
        self.window = window    # HUDWindow 를 받아서 제어
        self.icon = None

    def setup(self):
        # 트레이 아이콘 이미지 로드
        image = Image.open("assets/tray_icon.png")

        # 트레이 아이콘 생성
        self.icon = Icon(
            name="StudyPals",
            icon=image,
            menu=Menu(
                MenuItem("보이기/숨기기", self.on_toggle, default=True),
                MenuItem("종료", self.on_quit)
            )
        )

        # 별도 스레드로 실행
        threading.Thread(target=self.icon.run, daemon=True).start()

    def on_toggle(self):
        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show()

    def on_quit(self):
        self.window.monitor.listener_kb.stop()
        self.window.monitor.listener_ms.stop()
        self.icon.stop()
        QMetaObject.invokeMethod(self.window, "close", Qt.ConnectionType.QueuedConnection)