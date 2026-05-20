from firebase import get_db
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from google.cloud.firestore_v1.base_query import FieldFilter

# [닉네임 변경]
class NicknameDialog(QDialog):
    def __init__(self, user_id, card):
        super().__init__()
        self.user_id = user_id
        self.card = card
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Nickname 변경")
        layout = QVBoxLayout()

        # 입력창
        self.input = QLineEdit()
        self.input.setPlaceholderText("변경할 닉네임 입력 (최대 4글자)")
        self.input.setMaxLength(4)

        # 버튼들
        self.save_btn = QPushButton("저장")
        self.cancel_btn = QPushButton("취소")

        layout.addWidget(QLabel("변경할 닉네임"))
        layout.addWidget(self.input)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.cancel_btn)
        self.setLayout(layout)

        # 버튼 연결
        self.save_btn.clicked.connect(self.save_nickname)
        self.cancel_btn.clicked.connect(self.close)


    def save_nickname(self):
        nickname = self.input.text()
        db = get_db()
        db.collection("users").document(self.user_id).update({
            "nickname": nickname
        })

        # 카드 닉네임 즉시 업데이트 추가!
        self.card.nickname = nickname
        self.card.nickname_label.setText(nickname)

        QMessageBox.information(self, "완료", "닉네임이 변경되었습니다.")
        self.close()