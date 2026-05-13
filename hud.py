import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import Qt, QSize


# [동물 카드]
class AnimalCard(QWidget):
    def __init__(self, user_id, nickname, animal):
        super().__init__()
        self.user_id = user_id
        self.nickname = nickname
        self.animal = animal
        self.init_ui()

    def init_ui(self):
        # 세로 레이아웃 (동물 이미지 위, 닉네임 아래)
        layout = QVBoxLayout()
        
        # 이미지 표시할 라벨 생성
        self.img_label = QLabel()

        # 닉네임 표시할 라벨 생성
        self.nickname_label = QLabel(self.nickname)
        self.nickname_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.img_label)
        layout.addWidget(self.nickname_label)
        self.setLayout(layout)

        # 초기 이미지 설정 (closed 상태)
        self.set_status("closed")

    # 상태에 따라 이미지 전환하는 함수
    def set_status(self, status):
        base_path = f"assets/animals/{self.animal}"
        img_w = 100
        img_h = 125

        if status == "closed":
            # PNG 표시
            pixmap = QPixmap(f"{base_path}/close.png")
            pixmap = pixmap.scaled(img_w, img_h, Qt.AspectRatioMode.KeepAspectRatio)
            self.img_label.setPixmap(pixmap)
        else:
            # GIF 재생
            gif_map = {
                "opening": "open.gif",
                "working": "ing.gif",
                "closing": "close.gif"
            }
            movie = QMovie(f"{base_path}/{gif_map[status]}")
            movie.setScaledSize(QSize(img_w, img_h))
            self.img_label.setMovie(movie)
            movie.start()



# [메인 창]
class HUDWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("StudyPals")
        self.show()

        # 테두리 없애기
        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint |   # 테두리 제거
            Qt.WindowType.WindowStaysOnTopHint |   # 항상 최상단 유지
            Qt.WindowType.Tool   # 작업표시줄에 표시 안되는 툴창 형태
        ) 
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)   # 창 배경 투명 설정

        # 우측 하단 위치
        screen = QApplication.primaryScreen().geometry()  # 모니터 크기
        self.resize(120, 150)
        self.move(
            screen.width() - self.width() - 20,    # 오른쪽에서 20px
            screen.height() - self.height() - 60   # 아래에서 60px
        )

        # 레이아웃 설정 (카드들을 가로로 나열)
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # 내 카드 (임시 데이터로 테스트)
        # my_card = AnimalCard(
        #     user_id="apple",
        #     nickname="애플",
        #     animal="cat"
        # )
        # my_card.set_status("working")
        # layout.addWidget(my_card)

        self.setLayout(layout)
        self.show()


    # ------ 드래그 이동 ------
    # 마우스 클릭 시작점 저장
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    # 드래그로 창 이동
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            diff = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + diff)
            self.drag_pos = event.globalPosition().toPoint()


# 앱 실행
app = QApplication(sys.argv)
window = HUDWindow()
sys.exit(app.exec())