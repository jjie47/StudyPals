from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QMessageBox
from auth import signup

class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("StudyPals 회원가입")
        layout = QVBoxLayout()

        # ID 입력창
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디 입력")

        # PW 입력창
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호 입력")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Nickname 입력창
        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText("닉네임 입력 (최대 4글자)")
        self.nickname_input.setMaxLength(4) 

        # 동물 선택 드롭박스
        self.animal_combo = QComboBox()
        self.animal_combo.addItems(["cat", "dog", "rabbit", "bear", "panda", "tiger"])

        # 버튼
        self.signup_btn = QPushButton("회원가입")
        self.cancel_btn = QPushButton("취소")

        layout.addWidget(QLabel("아이디"))
        layout.addWidget(self.id_input)
        layout.addWidget(QLabel("비밀번호"))
        layout.addWidget(self.pw_input)
        layout.addWidget(QLabel("닉네임"))
        layout.addWidget(self.nickname_input)
        layout.addWidget(QLabel("동물 선택"))
        layout.addWidget(self.animal_combo)
        layout.addWidget(self.signup_btn)
        layout.addWidget(self.cancel_btn)
        self.setLayout(layout)

        self.signup_btn.clicked.connect(self.on_signup)
        self.cancel_btn.clicked.connect(self.close)

    def on_signup(self):
        user_id = self.id_input.text()
        user_pw = self.pw_input.text()
        nickname = self.nickname_input.text()
        animal = self.animal_combo.currentText()

        if not user_id or not user_pw or not nickname:
            QMessageBox.warning(self, "경고", "모든 항목을 입력해주세요.")
            return

        try:
            signup(user_id, user_pw, nickname, animal)
            QMessageBox.information(self, "완료", "회원가입이 완료되었습니다!")
            self.close()
        except ValueError as e:
            QMessageBox.warning(self, "오류", str(e))