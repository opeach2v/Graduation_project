import logging
logger = logging.getLogger('graduation_work')
from zoneinfo import ZoneInfo
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponse
from datetime import date, datetime, timedelta, timezone
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.utils.deprecation import MiddlewareMixin
import pytz
from .models import users_collection, results_collection, children_collection, teachers_collection, parents_collection, notice_collection
from . import models
from django.contrib import messages
import json, re
from bson import ObjectId

# 로그인 페이지 (메인)
def main(request):
    return render(request,'graduation_work/main.html')

# 회원가입
@csrf_exempt
@never_cache
def add_users(request):
    if request.method == 'POST':
        try:
            # POST 데이터 받기
            username = request.POST.get('username')
            password = request.POST.get('password')
            role = request.POST.get('role')
            name = request.POST.get('name')
            contact = request.POST.get('phoneNumber')
            if role == "teacher":
                classroom = request.POST.get('classroom')

            # 모든 항목이 입력되었는지 확인
            if not all([username, password, role, name, contact]):
                messages.error(request, "모든 항목을 입력해주세요.")
                return redirect('add_users')  # 회원가입 페이지로 다시 이동

            # username과 password는 영어(알파벳)만 허용
            if not re.fullmatch(r'[A-Za-z0-9]+', username) or not re.fullmatch(r'[A-Za-z0-9]+', password):
                messages.error(request, "아이디와 비밀번호는 영문자만 사용 가능합니다.")
                return redirect('add_users')

            # 비밀번호 해싱
            # hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Django User 모델에도 계정 추가 
            if User.objects.filter(username=username).exists():
                messages.error(request, "이미 존재하는 아이디입니다.")
                return redirect('add_users')
            else:
                user = User.objects.create_user(username=username, password=password)

            # 데이터 생성
            data = {
                "username": username,
                "password": user.password,  # 해시된 비번 저장
                "role": role,
                "name": name,
                "createdAt": datetime.now()
            }

            # mongoDB users 컬렉션에 저장 저장
            users_collection.insert_one(data)

            if role == "parent":
                parents_collection.insert_one({
                    "name": name,
                    "contact": contact,
                    "children_ids": []
                })
            elif role == "teacher":
                teachers_collection.insert_one({
                    "name": name,
                    "contact": contact,
                    "classroom": classroom
                })

            return redirect('login_user')  # 회원가입 후 로그인 페이지로 리다이렉션
        except Exception as e:
            return JsonResponse({"signup error" : str(e)}, status=500)

    # GET 요청이 들어오면 회원가입 페이지를 렌더링
    return render(request, 'graduation_work/createId_page.html')

# 로그인 처리
@csrf_exempt
@never_cache
def login_user(request):
    if request.method == 'POST':
        try:
            # POST 데이터 받기
            username = request.POST.get('username')
            input_password = request.POST.get('password')
            role = request.POST.get('role')

            # Django 인증 시스템으로 먼저 인증 시도
            user = authenticate(request, username=username, password=input_password)

            # 후 MongoDB에서 연할 등 추가 정보 확인
            # 데이터 조회 (username, password가 일치하는 데이터가 있는지 확인)
            user_data = users_collection.find_one({"username": username, "role": role})
            print(f"user_data: {user_data}")  # Debugging
            if user is not None and user_data:
                login(request, user)  # Django 인증 시스템에 로그인 처리 (세션 생성)

                request.session['username'] = user_data.get("username")
                request.session['role'] = user_data.get("role")
                request.session['name'] = user_data.get("name")
                name = user_data.get("name")
                print(f"로그인된 사용자: {name}")
            
                # role에 따라 리디렉션
                if role == "parent":    # 부모님
                    # 로그인한 부모 사용자와 일치하는 부모 정보만 찾기
                    parent_data = parents_collection.find_one({"name": user_data['name']})
                    print(f"parent_name: {user_data['name']}")
                    # 세션에 저장 (조건: 존재하고 children_ids가 비어있지 않으면)
                    if parent_data and 'children_ids' in parent_data:
                        request.session['children_ids'] = [str(cid) for cid in parent_data['children_ids']]
                    else:
                        request.session['children_ids'] = []  # 기본값
                    return redirect('showParent')
                elif role == "teacher": # 선생님
                    teacher_data = teachers_collection.find_one({"name": name})
                    if teacher_data and 'classroom' in teacher_data:
                        request.session['classroom'] = teacher_data.get('classroom')
                    return redirect('teachers_page')
                else:
                    # 로그인 실패
                    return render(request, 'graduation_work/main.html', {'error': '학부모와 선생님을 다시 선택해주세요.'})
            else:
                # 로그인 실패
                return render(request, 'graduation_work/main.html', {'error': '아이디 또는 비밀번호가 일치하지 않습니다.'})

        except Exception as e:
            return render(request, 'graduation_work/main.html', {'error': f"로그인 중 오류가 발생했습니다: {str(e)}"})
    return render(request, 'graduation_work/main.html')


# 이게 진짜 학부모 페이지 역할
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_user')  # 로그인 안 했으면 로그인 페이지로 리다이렉트
@never_cache
def showParents(request):
    # 로그인 세션에서 부모 이름 가져오기
    parent_name = request.session.get('name')
    parent_doc = parents_collection.find_one({"name": parent_name})
    if not parent_name:
        # 세션에 이름이 없으면 로그인 페이지로 리다이렉트하거나 처리
        return redirect('login_user')
    else:
        parent = {
            "id": str(parent_doc.get("_id")),
            "name": parent_doc.get("name"),
            "contact": parent_doc.get("contact"),
            "children": []
        }

        for cid in parent_doc.get("children_ids", []):
            child = children_collection.find_one({"_id": ObjectId(cid)})
            if child:
                birthdate = child.get("birthdate")
                if birthdate and isinstance(birthdate, datetime):
                    age = calculate_age(birthdate.date())  # datetime.date로 변환
                else:
                    age = "정보 없음"

                parent["children"].append({
                    "id": str(child["_id"]),
                    "name": child["name"],
                    "age": f"{age}세" if isinstance(age, int) else age,
                })

    print(f"로그인 후 부모님 이름: {parent["name"]}")
    return render(request, 'graduation_work/parents_page.html', {
        "parents": parent
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_user')  # 로그인 안 했으면 로그인 페이지로 리다이렉트
@never_cache
def teachersPage(request):
    # 로그인 세션에서 정보 가져오기
    teacher_name = request.session.get('name')
    teacher_doc = teachers_collection.find_one({"name": teacher_name})
    if not teacher_name:
        # 세션에 이름 없으면 로그인 페이지로 리다이렉트하거나 처리
        return redirect('login_user')
    else:
        teacher = {
            "id": str(teacher_doc.get("_id")),
            "name": teacher_name,
            "contact": teacher_doc.get("contact"),
            "classroom": teacher_doc.get("classroom"),
            "children": []  # 선생님이 담당하는 어린이 목록
        }

        # 선생님이 담당하는 어린이 목록 가져오기
        for child in children_collection.find({"classroom": teacher_doc.get("classroom")}):
            # 아이들 나이 계산 추가
            birthdate = child.get("birthdate")
            if birthdate and isinstance(birthdate, datetime):
                age = calculate_age(birthdate.date())  # datetime.date로 변환
            else:
                age = "정보 없음"

            teacher["children"].append({
                "id": str(child["_id"]),
                "name": child["name"],
                "age": f"{age}세" if isinstance(age, int) else age,
                "parent_id": str(child.get("parent_id"))
            })


    return render(request, 'graduation_work/teachers_page.html', {
        "teachers": teacher
    })

def show_users(request):
    users = []
    for doc in users_collection.find({}):
        username = doc.get("username")
        password = doc.get("password")
        role = doc.get("role")
        name = doc.get("name")
        createdAt = doc.get("createdAt")
        users.append({"username": username, "password": password, "role": role, "name": name, "createdAt": createdAt})
    
    return JsonResponse({'users': users}, safe=False, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=UTF-8")

# 로그아웃
@never_cache
def logout_view(request) :
    request.session.flush()  # 세션 데이터 초기화
    request.session.clear_expired()  # 만료된 세션 데이터 제거
    logout(request)
    return redirect('login_user')


# 파일 업로드
def uplooadFile(request):
    if request.method == "POST":
        fileTitle = request.POST['fileTitle']
        uploadedFile = request.FILES["uploadedFile"]

        # DB에 저장
        fileUploads = models.FileUploads(
            title = fileTitle,
            uploadedFile = uploadedFile
        )
        fileUploads.save()

    fileUpload = models.FileUploads.objects.all()

    return render(request, "teachers_page.html", context = {
        "files": fileUpload
    })


# DB ai_results 컬렉션에 값 입력해서 넣기
def input_results(request):
    if request.method == 'POST':
        try:
            # POST 데이터 받기
            child_id = request.POST.get('child_id')
            event_type = request.POST.get('action')
            confidence = request.POST.get('confidence')
            timestamp_str = request.POST.get('timestamp')

            kst = pytz.timezone('Asia/Seoul')
            dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")  # naive datetime
            dt_kst = kst.localize(dt)  # KST timezone-aware datetime

            # 데이터 생성
            data = {
                "child_id": child_id,
                "event_type": event_type,
                "confidence": confidence,
                "timestamp": dt_kst
            }

            # mongoDB에 저장
            results_collection.insert_one(data)
            return redirect('input_results')
        except Exception as e:
            return JsonResponse({"input error" : str(e)}, status=500)

    # GET 요청이 들어오면 입력창을 렌더링
    return render(request, 'graduation_work/temporary_inputResult.html')

# ai_results 값 보기
def showResults(request):
    res = []
    for doc in results_collection.find({}):
        child_id = doc.get("child_id")
        event_type = doc.get("event_type")
        confidence = doc.get("confidence")
        timestamp = doc.get("timestamp")
        res.append({"child_id": child_id, "event_type": event_type, "confidence": confidence, "timestamp": timestamp})
    
    return JsonResponse({'res': res}, safe=False, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=UTF-8")

# ai_results 데이터 삭제
def deleteRes(request):
    res = results_collection.delete_many({})
    return HttpResponse(f"{res.deleted_count} documents deleted from 'actions'")

# 유저 데이터 삭제
def deleteUsers(request):
    res = users_collection.delete_many({})
    return HttpResponse(f"{res.deleted_count} documents deleted from 'actions'")

# 따로 홈페이지에서 부모 컬렉션 값 보기
def show_parents(request):
    parents = []
    for doc in parents_collection.find({}):
        name = doc.get("name")
        contact = doc.get("contact")
        children_ids = doc.get("children_ids", [])
        if isinstance(children_ids, list):
            children_ids_str = [str(cid) for cid in children_ids]
        else:   # 단일 id일 경우
            children_ids_str = str(children_ids)

        parents.append({"name": name, "contact": contact, "children_ids": children_ids_str})
    
    return JsonResponse({'parents': parents}, safe=False, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=UTF-8")


# 만 나이 계산 함수
def calculate_age(birthdate):
    today = date.today()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

# 부모님 데이터 삭제
def deleteParents(request):
    res = parents_collection.delete_many({})
    return HttpResponse(f"{res.deleted_count} documents deleted from 'actions'")

# 선생님 컬렉션 값 보기
def showTeachers(request):
    res = []
    for doc in teachers_collection.find({}):
        _id = doc.get("_id")
        name = doc.get("name")
        contact = doc.get("contact")
        classroom = doc.get("classroom")
        res.append({"_id": str(_id), "name": name, "contact": contact, "classroom": classroom})
    
    return JsonResponse({'res': res}, safe=False, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=UTF-8")

# 선생님 데이터 삭제
def deleteTeachers(request):
    res = teachers_collection.delete_many({})
    return HttpResponse(f"{res.deleted_count} documents deleted from 'actions'")

@csrf_exempt
def add_child(request):
    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        child_name = request.POST.get('childname')
        birthdate = request.POST.get('birthdate')
        classroom = request.POST.get('classroom')

        format_birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
        # 데이터 생성
        data = {
            "name": child_name,
            "birthdate": format_birthdate,
            "parent_id": ObjectId(parent_id),
            "classroom": classroom
        }

        # mongoDB에 어린이 데이터 저장
        inserted_child = children_collection.insert_one(data)

        child_id = inserted_child.inserted_id   # 자녀의 _id 가져오기

        # 그리고 생성된 어린이 고유 id를 부모님 컬렉션에 업데이트
        parents_collection.update_one(
            {"_id": ObjectId(parent_id)},
            {"$push": {"children_ids": child_id}}  # child_id
        )
        return redirect('showParent')  # 다시 부모 페이지로
    
# 어린이 컬렉션 보기 
def show_children(request):
    res = []
    for doc in children_collection.find({}):
        childId = doc.get("_id")
        name = doc.get("name")
        birthdate = doc.get("birthdate")
        parent_id = doc.get("parent_id")
        classroom = doc.get("classroom")
        res.append({"childId": str(childId), "name": name, "birthdate": birthdate, "parent_id": str(parent_id), "classroom": classroom})
    
    return JsonResponse({'res': res}, safe=False, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=UTF-8")

# 어린이 데이터 삭제
def deleteChildren(request):
    res = children_collection.delete_many({})
    return HttpResponse(f"{res.deleted_count} documents deleted from 'actions'")

# 선생님이 알림장 내용 작성해서 저장할 때 사용
def writeNotice(request, teacher_id, classroom):
    if request.method == 'POST':      
        try:
            content = request.POST.get('content')
            child_id = request.POST.get('child_id')  # 열려있는 알림장 주인(어린이 ID)

            print(f"child_id: {child_id}, teacher_id: {teacher_id}, classroom: {classroom}, content: {content}")

            if not content:
                return JsonResponse({"error": "내용을 입력해주세요."}, status=400)
            if not child_id or not teacher_id or not classroom:
                return JsonResponse({"error": "필수 데이터가 누락되었습니다."}, status=400)

            child_doc = children_collection.find_one({"_id": ObjectId(child_id)})
            if child_doc is None:
                raise ValueError("child_doc를 찾을 수 없습니다.")

            date = datetime.now(timezone.utc)
            format_date = datetime(date.year, date.month, date.day)
            notice = {
                "child_id": child_id,
                "content": content,
                "date": format_date,  # 현재 시간
                "teacher_id": teacher_id,
                "classroom": classroom
            }

            notice_collection.insert_one(notice)
            return JsonResponse({"message": "알림장 내용이 저장되었습니다."}, status=201)

        except Exception as e:
            import traceback
            traceback.print_exc()  # 터미널에 전체 에러 스택 출력
            logger.error(f"서버 에러 발생: {e}", exc_info=True)
            return JsonResponse({"error": "서버 오류가 발생했습니다. 관리자에게 문의하세요."}, status=500)
    return HttpResponseNotAllowed(['POST'])

# 알림장 내용 전체 삭제 ..
def deleteNotice(request):
    res = notice_collection.delete_many({})
    return HttpResponse(f"{res.deleted_count} documents deleted from 'actions'")

# 학부모가 알림장 내용 확인할 때 (알림장 내용과 위험 행동분석 결과 다 들고 오기)
def showNotice_cont(request, id):
    # 이거 실행 됐는지 확인하려고
    print(f"child_id: {id}")

    try:
        # 한국 시간대
        kst = pytz.timezone('Asia/Seoul')
        # 오늘 날짜 검색하기
        today = datetime.now(kst)
        # 자정으로 초기화 + 타임존 유지
        start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        querys = {
            'child_id': id,
            'date': start.replace(tzinfo=None)
        }
        notice_doc = notice_collection.find_one({'child_id': id})
        cont = notice_collection.find_one(querys, {'content': 1, '_id': 0})
        print(f"notice_doc", notice_doc)
        print(f"query:", querys)
        print(f"cont:", cont)

        query = {
            'child_id': id,
            'timestamp': {
                '$gte': start,
                '$lt': end
            }
        }

        results_collection.find(query)
        total_res = results_collection.count_documents(query)   # 오늘 하루의 행동 분석 갯수
        event_counts = {}   # 각 행동들의 갯수

        ALL_EVENTS = ["standing", "sitting", "walking", "running", "playing", "fighting", "falldown"]
        event_counts = {event: 0 for event in ALL_EVENTS}

        for doc in results_collection.find(query):
            event_type = doc.get('event_type')
            if event_type in event_counts:
                event_counts[event_type] += 1

        sum_data = {}
        if cont and 'content' in cont:
            sum_data['content'] = cont['content']

        if total_res > 0:
            sum_data['total_res'] = total_res
        else: sum_data['total_res'] = 0

        sum_data['event_counts'] = event_counts

        print(f"total_res: {total_res}, event_counts: {event_counts}")

        return JsonResponse(sum_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# 선생님 그동안 쓴 모든 알림장 내용 확인하기
def get_notice_logs(request, teacher_id):
    # teacher_id로 선생님이 쓴 알림장 모두 가져오기
    notice_doc = list(notice_collection.find({"teacher_id": teacher_id}, {"content": 1, "_id": 0}).sort("timestamp", -1))

    notice = []
    for doc in notice_doc:
        # 날짜만 추출 (timestamp가 datetime인 경우)
        date_only = doc["date"].strftime("%Y-%m-%d") if "timestamp" in doc else ""

        # child_id로 이름 조회
        child_name = children_collection.find_one({"_id": doc.get("child_id")}, {"name": 1})

        # 최종 정리
        notice.append({
            "child_id": str(doc.get("child_id")),
            "teacher_id": teacher_id,
            "classroom": doc.get("classroom", ""),
            "content": doc.get("content", ""),
            "date": date_only,
            "child_name": child_name
        })

    # MongoDB의 ObjectId 등 직렬화 문제 해결 위해 dumps 사용
    return JsonResponse({"notices": notice})

# 탈퇴하기
@never_cache
@login_required
def withdrawalUser(request, name):
    if request.method == 'POST':
        user = request.user
        # 몽고디비에서 해당 username 데이터 삭제
        username = user.username
        print(f"탈퇴 시도: username={username}")
        delete_user = users_collection.delete_one({'username': username})  # username 기준 삭제
        print(f"users 컬렉션 삭제 결과: {delete_user.deleted_count}건 삭제됨")
        if parents_collection.find_one({'name': name}):
            parent = parents_collection.find_one({'name': name})
            print(list(parent))
            parent_id = parents_collection.find_one({'name': name}, {"_id": 1})
            delete_parent = parents_collection.delete_many({'name': name})  # parents 기준 삭제
            print(f"학부모 컬렉션 삭제 결과: {delete_parent.deleted_count}건 삭제됨")

            print(parent_id)
            child_id = list(children_collection.find({'parent_id': parent_id}, {"_id": 1}))
            print(child_id)
            for ids in child_id:
                ress = results_collection.delete_many({'child_id': ids})
                print(f"{ids}의 ai 결과 컬렉션 삭제 결과: {ress.deleted_count}건 삭제됨")

            delete_children = children_collection.delete_many({'parent_id': parent_id})
            print(f"학부모의 자녀 컬렉션 삭제 결과: {delete_children.deleted_count}건 삭제됨")

        elif teachers_collection.find_one({'name': name}):
            delete_teacher = teachers_collection.delete_many({'name': name})    # teachers 기준 삭제
            print(f"선생님 컬렉션 삭제 결과: {delete_teacher.deleted_count}건 삭제됨")
        else:
            print(f"존재하지 않음")

        # Django auth User 삭제
        user.delete()
        # 로그아웃 처리
        logout(request)
        return redirect('login_user')
    

# 이건 내가 알림장 내용 확인 하는 거
def show_content(request):
    res = []
    for doc in notice_collection.find({}):
        child_id = doc.get("child_id")
        content = doc.get("content")
        date = doc.get("date")
        teacher_id = doc.get("teacher_id")
        classroom = doc.get("classroom")
        res.append({"childId": str(child_id), "content": content, "date": date, "teacher_id": str(teacher_id), "classroom": classroom})
    
    return JsonResponse({'res': res}, safe=False, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=UTF-8")

# 그래프 그릴 때 값 가져오기
def chart_data(request):
    labels = ["Standing", "Walking", "Running", "Sitting", "Playing", "Fighting", "fall down"]
    result = {label: 0 for label in labels}

    for doc in results_collection.find():
        event_type = doc.get("event_type")
        if event_type in result:
            result[event_type] += 1

    return JsonResponse({
        "labels": labels,
        "data": [result[label] for label in labels]
    })