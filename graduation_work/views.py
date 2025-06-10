from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control
from django.utils.deprecation import MiddlewareMixin
from .models import users_collection, results_collection, children_collection, teachers_collection, parents_collection, notice_collection
from . import models
from django.contrib import messages
import json, re
from bson import ObjectId

import bcrypt;

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
            if not User.objects.filter(username=username).exists():
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

            # 성공 메시지와 함께 로그인 페이지로 이동
            messages.success(request, f"{name} 님, 회원가입이 완료되었습니다. 로그인 해주세요!")
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
            
                # role에 따라 리디렉션
                if role == "parent":    # 부모님
                    # 로그인한 부모 사용자와 일치하는 부모 정보만 찾기
                    parent_data = parents_collection.find_one({"name": user_data['name']})
                    # 세션에 저장 (조건: 존재하고 children_ids가 비어있지 않으면)
                    if parent_data and 'children_ids' in parent_data:
                        request.session['children_ids'] = [str(cid) for cid in parent_data['children_ids']]
                    else:
                        request.session['children_ids'] = []  # 기본값
                    return redirect('showParent')
                elif role == "teacher": # 선생님
                    teacher_data = teachers_collection.find_one({"username": username})
                    if teacher_data and 'classroom' in teacher_data:
                        request.session['classroom'] = teacher_data['classroom']
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

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_user')  # 로그인 안 했으면 로그인 페이지로 리다이렉트
@never_cache
def parentsPage(request):
    # 로그인 안 햇는데도 URL로 접근하려고 하면 막음
    if not request.user.is_authenticated:
        return redirect('login_user')
    name = request.session.get('name')  # 세션에 저장했던 값 꺼냄
    children_ids = request.session.get('children_ids', [])  # 리스트 형태로 불러오기

    return render(request, 'graduation_work/parents_page.html', {
        'name' : name,
        'children_ids': children_ids
    })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='login_user')  # 로그인 안 했으면 로그인 페이지로 리다이렉트
@never_cache
def teachersPage(request):
    # 로그인 안 햇는데도 URL로 접근하려고 하면 막음
    if not request.user.is_authenticated:
        return redirect('login_user')
    name = request.session.get('name')
    classroom = request.session.get('classroom')

    return render(request, 'graduation_work/teachers_page.html', {
        'name' : name,
        'classroom': classroom
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
            timestamp = request.POST.get('timestamp')

            # 데이터 생성
            data = {
                "child_id": child_id,
                "event_type": event_type,
                "confidence": confidence,
                "timestamp": timestamp
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

# 부모님 컬렉션 값 보기
def showParents(request):
    for parent_doc in parents_collection.find({}):
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

    return render(request, 'graduation_work/parents_page.html', {
        "parents": parent
    })

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
            "parent_id": parent_id,
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
        res.append({"childId": str(childId), "name": name, "birthdate": birthdate, "parent_id": parent_id, "classroom": classroom})
    
    return JsonResponse({'res': res}, safe=False, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=UTF-8")

# 어린이 데이터 삭제
def deleteChildren(request):
    res = children_collection.delete_many({})
    return HttpResponse(f"{res.deleted_count} documents deleted from 'actions'")

# 선생님이 알림장 내용 작성해서 저장할 때
def writeNotice(request):
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
            "parent_id": parent_id,
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

# 학부모가 알림장 내용 확인할 때 (알림장 내용과 위험 행동분석 결과 다 들고 오기)
def showNotice_cont(id):
    try:
        cont = notice_collection.find_one({'_id': ObjectId(id)}, {'content': 1, '_id': 0})

        # 오늘 날짜 검색하기
        today = datetime.today()
        start = datetime(today.year, today.month, today.day)    # 오늘 자정에서 
        end = start + timedelta(days = 1)   # 내일 자정까지

        # ISO 8601 문자열로 변환(yyyy-mm-ddThh:mm:dd)
        start_str = start.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end.strftime("%Y-%m-%dT%H:%M:%S")

        query = {
            'child_id': id,
            'date': {
                '$gte': start_str,
                '$lt': end_str
            }
        }
        result = results_collection.find_one(query)
        total_res = results_collection.count_documents(query)   # 오늘 하루의 행동 분석 갯수
        event_counts = {}   # 각 행동들의 갯수

        for doc in result:
            event_type = doc.get('event_type')
            if event_type:
                event_counts[event_type] = event_counts.get(event_type, 0) + 1

        if cont:
            sum_data = {
                **cont,
                'total_res': total_res,
                'event_counts': event_counts
            }

            return JsonResponse(sum_data)
        else:
            return JsonResponse({'error': 'Not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)