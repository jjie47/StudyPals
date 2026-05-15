import json
from firebase import get_db
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QMetaObject, Qt
from menu.nickname import NicknameDialog
from menu.animal import AnimalDialog
from menu.group import GroupDialog


# HUD창 우클릭시 나오는 메뉴
class SettingsMenu:
    def __init__(self, window):
        self.window = window

    def show(self, pos):
        menu = QMenu()

        # 메뉴 항목 추가
        nickname_action = QAction("닉네임 변경")
        animal_action = QAction("동물 변경")
        group_action = QAction("그룹 관리")
        logout_action = QAction("로그아웃")
        quit_action = QAction("종료")

        menu.addAction(nickname_action)
        menu.addAction(animal_action)
        menu.addAction(group_action)
        menu.addSeparator()            # 구분선
        menu.addAction(logout_action)
        menu.addAction(quit_action)

        # 각 항목 클릭시 연결
        nickname_action.triggered.connect(self.show_nickname_dialog)
        animal_action.triggered.connect(self.show_animal_dialog)
        group_action.triggered.connect(self.show_group_dialog)
        logout_action.triggered.connect(self.on_logout)
        quit_action.triggered.connect(self.on_quit)

        menu.exec(pos)
    
    def show_nickname_dialog(self):
        dialog = NicknameDialog(user_id=self.window.monitor.user_id, card=self.window.my_card)
        dialog.setParent(self.window, dialog.windowFlags())
        dialog.exec()

    def show_animal_dialog(self):
        dialog = AnimalDialog(
            user_id=self.window.monitor.user_id,
            card=self.window.my_card,     # AnimalCard 전달
            monitor=self.window.monitor
        )
        dialog.setParent(self.window, dialog.windowFlags())
        dialog.exec()

    def show_group_dialog(self):
        dialog = GroupDialog(
            user_id=self.window.monitor.user_id
        )
        dialog.setParent(self.window, dialog.windowFlags())
        dialog.exec()

    def on_logout(self):
        # config.json 토큰 삭제
        with open("secrets/config.json", "w") as f:
            json.dump({}, f)
        
        # 리스너 종료
        self.window.monitor.listener_kb.stop()
        self.window.monitor.listener_ms.stop()
        
        # 트레이 아이콘 제거
        self.window.tray.icon.stop()
        
        # 로그인 창 열기
        from login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        
        # HUD 창 닫기
        QMetaObject.invokeMethod(self.window, "close", Qt.ConnectionType.QueuedConnection)

    def on_quit(self):
        self.window.tray.on_quit()


