from django.urls import path

from . import views

urlpatterns = [
    path('', views.main, name='main'),    # 메인 페이지(로그인 페이지)
    path('login/', views.login_user, name='login_user'),    # 로그인 페이지
    path('signup/', views.add_users, name='add_users'),    # 회원가입 페이지 및 회원가입 처리
    # path('parents/', views.parentsPage, name='parents_page'),    # 부모님 페이지
    path('teachers/', views.teachersPage, name='teachers_page'),    # 선생님 페이지
    path('logout/', views.logout_view, name='logout'),

    # 알림장 내용 확인
    path('api/showNotice_cont/<str:id>/', views.showNotice_cont, name='showNotice_cont'),
    path('show_content/', views.show_content, name='show_content'),    # 알림장 내용 확인 페이지(내가 확인하는 거 )
    # 알림장 쓰기
    path('api/writeNotice/<str:teacher_id>/<str:classroom>/', views.writeNotice, name='writeNotice'),
    # 알림장 모든 내용 가져오기
    path('api/get_notice_logs/<str:id>/', views.get_notice_logs, name='get_notice_logs'),

    # 회원 탈퇴용
    path("bye/<str:name>/", views.withdrawalUser, name='withdrawalUser'),

    # 데이터 확인용 
    path('show/', views.show_users),
    path('res_show/', views.showResults),
    path('show_children/', views.show_children),
    path('show_parents/', views.showParents, name='showParent'),    # 찐 학부모 페이지
    path('showparents/', views.show_parents),

    path('chart-data/<str:classroom>', views.chart_data, name='chart_data'),
    path( 'today-chart-data/', views.today_chart_data, name='today_chart_data'),

    path('show_teachers/', views.showTeachers),

    path('addresult/', views.input_results, name='input_results'),  # 임시로 만든 거
    path('addchild/', views.add_child, name='add_child'),

    # 데이터 전체 삭제용
    path('removedata/', views.deleteRes, name='deleteRes'),
    path('removeuser/', views.deleteUsers, name='deleteUsers'),
    path('removeparents/', views.deleteParents, name='deleteParents'),
    path('removeteachers/', views.deleteTeachers, name='deleteTeachers'),
    path('removechildren/', views.deleteChildren, name='deleteChildren'),
    path('removenotice/', views.deleteNotice, name='deleteNotice'),
]