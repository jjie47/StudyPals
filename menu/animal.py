from firebase import get_db 
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel

class AnimalDialog(QDialog):
    def __init__(self, user_id, card, monitor):   # card 는 AnimalCard 인스턴스
        super().__init__()
        self.user_id = user_id
        self.card = card                 # HUD 즉시 반영용
        self.monitor = monitor 
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("동물 변경")
        layout = QVBoxLayout()

        # 드롭박스
        self.combo = QComboBox()
        self.combo.addItems(["cat", "dog", "rabbit"])  # 동물 목록

        # 버튼
        self.save_btn = QPushButton("저장")
        self.cancel_btn = QPushButton("취소")

        layout.addWidget(QLabel("동물 선택"))
        layout.addWidget(self.combo)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.cancel_btn)
        self.setLayout(layout)

        self.save_btn.clicked.connect(self.save_animal)
        self.cancel_btn.clicked.connect(self.close)

    def save_animal(self):
        animal = self.combo.currentText()   # 선택한 동물
        db = get_db()
        # Firestore 업데이트
        db.collection("users").document(self.user_id).update({
            "animal": animal
        })

        # monitor 상태 리셋
        self.monitor.set_closed()
        
        # HUD 즉시 반영
        self.card.animal = animal
        self.card.set_status("closed")
        self.close()