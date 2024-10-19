from django.urls import path

from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('login/', views.loginPage, name="login"),

    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),

    path('', views.home, name="home"),
    path('home_studybuddy', views.home_studybuddy, name="home_studybuddy"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),

    path('update-user/', views.updateUser, name="update-user"),

    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),

    #----------------------------- Course Section -------------------------------------#

    path('teachers_page', views.teachers_page, name="teachers_page"),
    path('create_content', views.create_content, name="create_content"),
    path('classroom/<int:classroom_id>/create-assignment/', views.create_assignment, name='create_assignment'),
    path('dashboard', views.lessons_landing_page_main, name="dashboard"),
    path('admindashboard', views.admindashboard, name="admindashboard"),
    path('save_code/', views.save_code, name='save_code'),
    path('teacherredirect/', views.mark_as_teacher, name='teacherredirect'),
    path('project/<int:project_id>', views.project_view, name='project_view'),
    path('create_project', views.create_project, name='create_project'),
    path('classroom/<str:classroom_id>/announcement/create/', views.create_announcement, name='create_announcement'),
    path('lessons_landing_page/<int:course_id>/', views.lessons_landing_page, name='lessons_landing_page'),
    path('lesson/<int:lesson_id>/redirect/', views.lesson_redirect, name='lesson_redirect'),
    path('lesson/<int:lesson_id>/<int:lesson_page_id>/', views.lesson_page_detail, name='lesson_page_detail'),
    path('complete_lesson/<int:lesson_page_id>/', views.complete_lesson, name='complete_lesson'),
    path('assignment/<int:assignment_id>/', views.lesson_page_detail_assignment, name='lesson_page_detail_assignment'),
    path('calculate_progress', views.calculate_progress, name="calculate_progress"),
    path('calculate_classroom_progress', views.calculate_classroom_progress, name="calculate_classroom_progress"),
    path('teacherpage', views.teacherpage, name="teacherpage"),
    path('createclassroom', views.createclassroom, name="createclassroom"),
    path('joinclassroom', views.joinclassroom, name="joinclassroom"),
    path('classroom/<int:classroom_id>/', views.classroom_detail, name='classroom_detail'),
    path('teacherclassroomdetail/<int:classroom_id>', views.teacherclassroomdetail, name="teacherclassroomdetail"),
    path('course/create/', views.course_create_view, name='course_create'),
    path('lesson/create/', views.lesson_create_view, name='lesson_create'),
    path('project/delete/<int:pk>/', views.delete_project, name='delete_project'),

    path('lesson/create/<int:course_id>/', views.course_lesson_create_view, name='lesson_create_for_course'),



    path('lesson-page/create/', views.lesson_page_create_view, name='lesson_page_create'),

    path('lesson-page/create/<int:lesson_id>/', views.lesson_lesson_page_create_view, name='lesson_page_create_for_lesson'),

    path('course_catalog', views.course_catalog, name='course_catalog'),
    path('assignment/<int:assignment_id>/view', views.assignment_view, name='assignmentview'),
    path('complete_lesson_page/<int:lesson_page_id>/<int:assignment_id>/', views.complete_lesson_page_assignment, name='complete_lesson_page_assignment'),
    path('prev_lesson_page/<int:lesson_page_id>/<int:assignment_id>/', views.prev_lesson_page, name='prev_lesson_page'),

    path('course/<int:course_id>/view', views.course_view, name='course_view'),
    path('course/<int:course_id>/lesson_page/<int:lesson_page_id>/view', views.course_lesson_page_view, name='course_lesson_page_view'),

    path('lesson/<int:lesson_id>/view', views.lesson_view, name='lesson_view'),
    path('lesson/<int:lesson_id>/lesson_page/<int:lesson_page_id>/view', views.lesson_lesson_page_view, name='lesson_lesson_page_view'),

    path('lesson_page/<int:lesson_page_id>/view', views.lesson_page_view, name='lesson_page_view'),

    path('classroom/<int:classroom_id>/edit/', views.edit_classroom, name='edit_classroom'),

    path('lesson_page/<int:lesson_page_id>/edit', views.lesson_page_edit, name='lesson_page_edit'),

    path('course/<int:course_id>/edit', views.course_edit, name='course_edit'),
    path('lesson/<int:lesson_id>/edit', views.lesson_edit, name='lesson_edit'),

    path('update-lesson-order/', views.update_lesson_order, name='update_lesson_order'),
    path('update-lesson-page-order/', views.update_lesson_page_order, name='update_lesson_page_order'),

    path('course/<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('lesson/<int:pk>/delete/', views.delete_lesson, name='delete_lesson'),
    path('lessonpage/<int:pk>/delete/', views.delete_lessonpage, name='delete_lessonpage'),
    #----------------------------------Misc.----------------------------------------------#

    path('go/course/<int:course_id>/view', views.user_course_view, name='user_course_view'),
    path('go/course/<int:course_id>/lesson/<int:lesson_id>/view', views.user_course_lesson_view, name='user_course_lesson_view'),


    path('go/course/<int:course_id>/lesson/<int:lesson_id>/lesson_page/<int:lesson_page_id>/view', views.user_course_lesson_page_view, name='user_course_lesson_page_view'),

    path('go/lesson/<int:lesson_id>/view', views.user_lesson_view, name='user_lesson_view'),
    path('go/lesson/<int:lesson_id>/lesson_page/<int:lesson_page_id>/view', views.user_lesson_lesson_page_view, name='user_lesson_lesson_page_view'),

    path('go/lesson_page/<int:lesson_page_id>/view', views.user_lesson_page_view, name='user_lesson_page_view'),



    path('go/course/<int:course_id>/lesson_page/<int:lesson_page_id>/view/c', views.complete_user_course_lesson_page, name='complete_user_course_lesson_page'),
    path('go/lesson/<int:lesson_id>/lesson_page/<int:lesson_page_id>/view/c', views.complete_lesson_lesson_page_page, name='complete_lesson_lesson_page'),
    path('go/lesson_page/<int:lesson_page_id>/view/c', views.complete_lesson_page_page, name='complete_lesson_page'),



    path('compiler', views.compiler, name='compiler'),







    #---------------------------------------------------------------------------------------#

    path('opportunitiesPage', views.opportunitiesPage, name='opportunitiesPage'),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path('sitemap.xml', views.sitemap, name='sitemap'),



    #-------------------------------------Admin-------------------------------------------#

    path('adminHome', views.adminHome, name='adminHome'),
    path('lessonAdminPage/<int:lesson_id>/', views.lessonAdminPage, name='lessonAdminPage'),
    path('lesson/<int:lesson_id>/edit', views.lesson_detail_admin, name='lesson_detail_admin'),

    path('lesson/<int:lesson_id>/page/<int:lesson_page_id>/edit/', views.edit_lesson_page, name='edit_lesson_page'),

    path('lesson/<int:lesson_id>/create-lesson-page/', views.create_lesson_page, name='create_lesson_page'),
    path('lesson/<int:lesson_id>/delete-lesson-page/<int:lesson_page_id>/', views.delete_lesson_page, name='delete_lesson_page'),

    path('loaderio-ab8b6ca1eff1d2b53086856e6650bc05/', views.loaderiotest, name='loaderio-ab8b6ca1eff1d2b53086856e6650bc05'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="base/reset_password.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="base/reset_password_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>//<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="base/password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="base/reset_password_complete.html"), name="password_reset_complete"),



]

    #path('lessons_landing_page_main', views.lessons_landing_page_main, name="lessons_landing_page_main"),
    #path('create_assignment', views.create_assignment, name='create_assignment'),
    #path('lessons_landing_page_main', views., name="lessons_landing_page_main"),