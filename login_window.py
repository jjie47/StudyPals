from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("StudyPals 로그인")
        layout = QVBoxLayout()

        # ID 입력창
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디 입력")

        # PW 입력창
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호 입력")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)  # 비밀번호 가리기

        # 버튼
        self.login_btn = QPushButton("로그인")
        self.signup_btn = QPushButton("회원가입")

        layout.addWidget(QLabel("아이디"))
        layout.addWidget(self.id_input)
        layout.addWidget(QLabel("비밀번호"))
        layout.addWidget(self.pw_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.signup_btn)
        self.setLayout(layout)

        # 버튼 연결
        self.login_btn.clicked.connect(self.on_login)
        self.signup_btn.clicked.connect(self.on_signup)

    def on_login(self):
        user_id = self.id_input.text()
        user_pw = self.pw_input.text()

        if not user_id or not user_pw:
            QMessageBox.warning(self, "경고", "아이디와 비밀번호를 입력해주세요.")
            return

        try:
            from auth import login
            user_data = login(user_id, user_pw)
            # 로그인 성공시 HUD 실행
            from hud import HUDWindow
            self.hud = HUDWindow(user_data)
            self.hud.show()
            self.hide()
        except ValueError as e:
            QMessageBox.warning(self, "오류", str(e))

    def on_signup(self):
        # 회원가입 창 열기
        from signup_window import SignupWindow
        self.signup = SignupWindow()
        self.signup.show()