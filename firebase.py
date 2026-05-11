'''
Firestore
├── users/                     ← 유저 컬렉션
│   └── {userID}/              ← 유저 문서
│       ├── id       : string
│       ├── password : string  (암호화된 값)
│       ├── nickname : string
│       ├── animal   : string
│       └── status   : string  ("active" / "idle")
│
└── groups/                    ← 그룹 컬렉션
    └── {groupCode}/           ← 그룹 문서
        ├── name     : string
        └── members  : array   (userID 목록)
'''

import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    # 이미 초기화 됐으면 스킵 (중복 초기화 방지)
    

