import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget

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

        # 우측 하단 위치
        screen = QApplication.primaryScreen().geometry()  # 모니터 크기
        self.resize(120, 150)
        self.move(
            screen.width() - self.width() - 20,    # 오른쪽에서 20px
            screen.height() - self.height() - 60   # 아래에서 60px
        )

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