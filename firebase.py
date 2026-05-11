import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화 (연결 설정 및 인증준비가 완료되었는지)
def initialize_firebase():
    # Firebase가 이미 실행 중인지 확인
    # 실행중이 아니라면
    if not firebase_admin._apps:
        cred = credentials.Certificate("secrets/firebase-key.json")
        firebase_admin.initialize_app(cred)

# Firebase 데이터베이스 객체 가져오기
def get_db():
    initialize_firebase()   # Firebase 초기화
    return firestore.client()   # 연결 객체 생성

'''
Firestore
├── users/                     ← 유저 컬렉션
│   └── {userID}/              ← 유저 문서
│       ├── user_id       : string
│       ├── user_pw : string  (암호화된 값)
│       ├── nickname : string
│       ├── animal   : string
│       └── status   : string  ("active" / "idle")
│
└── groups/                    ← 그룹 컬렉션
    └── {groupCode}/           ← 그룹 문서
        ├── name     : string
        └── members  : array   (userID 목록)
'''
