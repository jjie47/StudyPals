from firebase import get_db
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import random
import string


db = get_db()

# [내 그룹 목록 조회]
def get_my_groups(user_id):
    groups = db.collection("groups").where(
        filter=FieldFilter("members", "array_contains", user_id)
    ).get()

    return [{"group_code": g.id, "group_name": g.to_dict()["group_name"]} for g in groups]


# [그룹 랜덤코드 생성]
def generate_group_code():
    # 대문자 + 숫자 조합 6자리
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


# [그룹 생성]
def create_group(user_id, group_name):
    group_code = generate_group_code()

    try:
        db.collection("groups").document(group_code).set({
            "group_name": group_name,
            "members": [user_id]
        })
        print("그룹 생성 성공!")
    except Exception as e:
        print(f"그룹 생성 DB 저장 중 오류 발생 : {e}")


# [그룹 입장]
def join_group(user_id, group_code):
    db_group = db.collection("groups").document(group_code).get()

    if not db_group.exists:
        raise ValueError("존재하지 않는 그룹입니다.")
    
    try:
        # 배열에 추가
        db.collection("groups").document(group_code).update({
            "members": firestore.ArrayUnion([user_id])
        })
        print("그룹 입장 성공")
    except Exception as e:
        print(f"그룹 입장 DB 저장 중 오류 발생 : {e}")


# [그룹 퇴장]
def leave_group(user_id, group_code):
    db_group = db.collection("groups").document(group_code).get()
    data = db_group.to_dict()

    if not user_id in data["members"]:
        raise ValueError("존재하지 않는 멤버입니다.")
    
    try:
        # 배열에서 멤버 제거
        db.collection("groups").document(group_code).update({
            "members": firestore.ArrayRemove([user_id])
        })

        # 멤버 제거 후 다시 조회
        db_group = db.collection("groups").document(group_code).get()
        if len(db_group.to_dict()["members"]) == 0:
            db.collection("groups").document(group_code).delete()
            print("그룹이 삭제되었습니다.")
        else:
            print("그룹 퇴장 성공!")

    except Exception as e:
        print(f"그룹 퇴장 DB 저장 중 오류 발생 : {e}")
