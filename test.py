# ---------- firebase ------------------
# from firebase import get_db

# db = get_db()
# print("Firebase 연결 성공!")

# # 테스트 데이터 Firestore에 써보기
# db.collection("test").document("test_doc").set({
#     "message": "Hello StudyPals!"
# })
# print("데이터 쓰기 성공!")

# ---------- auth-signup ------------------
# from auth import signup

# id = "apple"
# pw = "1234"
# nick = "애플"

# signup(id, pw, nick)

# ---------- auth-login ------------------
# from auth import login

# result = login("apple", "1234")
# print(result)