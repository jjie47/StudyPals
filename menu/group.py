from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QWidget, QInputDialog, QMessageBox
from firebase import get_db
from group import get_my_groups, join_group, leave_group, create_group
from PyQt6.QtCore import Qt

class GroupDialog(QDialog):
    def __init__(self, user_id, window):
        super().__init__()
        self.user_id = user_id
        self.window = window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("그룹 관리")
        self.setMinimumWidth(300)
        self.layout = QVBoxLayout()

        # 그룹 목록
        self.load_groups()

        # 그룹 입장
        join_layout = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("그룹코드 입력")
        self.join_btn = QPushButton("입장")
        self.join_btn.clicked.connect(self.join_group)
        join_layout.addWidget(self.code_input)
        join_layout.addWidget(self.join_btn)

        # 새 그룹 생성
        self.create_btn = QPushButton("새 그룹 생성")
        self.create_btn.clicked.connect(self.create_group)

        self.layout.addLayout(join_layout)
        self.layout.addWidget(self.create_btn)
        self.setLayout(self.layout)

    def load_groups(self):
        # 내 그룹 목록 가져오기
        groups = get_my_groups(self.user_id)
        for group in groups:
            row = QHBoxLayout()
            label = QLabel(f"{group['group_name']} | {group['group_code']}")
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            leave_btn = QPushButton("X")
            leave_btn.clicked.connect(lambda _, code=group['group_code']: self.leave_group(code))
            row.addWidget(label)
            row.addWidget(leave_btn)
            self.layout.addLayout(row)

    def join_group(self):
        code = self.code_input.text()

        if not code:
            QMessageBox.warning(self, "경고", "그룹코드를 입력해주세요.")
            return
        
        try:
            join_group(self.user_id, code)
            self.window.refresh_friend_cards()
            QMessageBox.information(self, "완료", "그룹에 입장했습니다.")
            self.refresh()      # 목록 새로고침
        except ValueError as e:
            QMessageBox.warning(self, "오류", str(e))

    def leave_group(self, group_code):
        try:
            leave_group(self.user_id, group_code)
            self.window.refresh_friend_cards()
            QMessageBox.information(self, "완료", "그룹에서 퇴장했습니다.")
            self.refresh()      # 목록 새로고침
        except ValueError as e:
            QMessageBox.warning(self, "오류", str(e))

    def create_group(self):
        # 간단한 입력창
        name, ok = QInputDialog.getText(self, "그룹 생성", "그룹 이름 입력")

        if ok and name:
            create_group(self.user_id, name)
            QMessageBox.information(self, "완료", "그룹이 생성되었습니다.")
            self.refresh()      # 목록 새로고침

    def refresh(self):
        self.close()
        new_dialog = GroupDialog(self.user_id, self.window)
        new_dialog.setParent(self.parent(), new_dialog.windowFlags())
        new_dialog.exec()