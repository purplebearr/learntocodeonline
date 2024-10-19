from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User, Lesson, UserProgress, LessonPage, UserLessonProgress
from .forms import RoomForm, UserForm, MyUserCreationForm, LessonPageForm, ClassroomForm, JoinClassroomForm, ClassroomGroupForm
from .forms import *
from django.utils.safestring import mark_safe
from django.views.generic.edit import UpdateView
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Lesson, LessonPage, UserProgress
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.contrib.auth.password_validation import validate_password

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Lesson, LessonPage, UserProgress, UserLessonProgress, ClassroomGroup, ClassroomLesson, ClassroomLessonPage, ClassroomUserProgress, ClassroomUserLessonProgress
from .forms import UserProfileForm, UserPasswordChangeForm, UserEmailChangeForm
from django.contrib.auth import update_session_auth_hash

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.models import AnonymousUser
from datetime import date, timedelta
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import CourseForm, LessonForm, LessonPageForm, ProjectForm, UserDeleteForm
from .forms import ClassroomAnnouncementForm
from django.contrib.auth.password_validation import validate_password

# Create your views here.

# rooms = [
#     {'id':1, 'name':'Lets learn Python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend developement'},
# ]

#------------------------------------------------------ Chat app section --------------------------------------------------------------------------#
def is_teacher(user):
    return user.is_teacher

from .forms import LoginForm
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    previous_page = request.META.get('HTTP_REFERER')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                validate_password(password)
            except ValidationError as e:
                messages.error(request, f"Password error: {', '.join(e.messages)}")
                return render(request, 'base/login_register_old.html', {'form': form, 'page': 'login'})
            
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_page = request.GET.get('next') or previous_page or 'home'
                return redirect(next_page)
            else:
                # Check if the email exists
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Incorrect password. Please try again.')
                else:
                    messages.error(request, 'No account found with this email. Please check your email or register.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = LoginForm()

    context = {'form': form, 'page': 'login'}
    return render(request, 'base/login_register_old.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            try:
                validate_password(form.cleaned_data['password1'])
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'Registration successful. Welcome!')
                return redirect('home')
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, f"Password error: {error}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, mark_safe(f"General error: {error}"))
                    else:
                        messages.error(request, mark_safe(f"{field.capitalize()}: {error}"))
    else:
        form = MyUserCreationForm()

    return render(request, 'base/login_register_old.html', {'form': form, 'page': 'register'})

def home(request):
    return render(request, 'base/home.html')

def room(request, pk):
    if request.user.is_authenticated == False:
        return redirect('login')
    else:
        room = Room.objects.get(id=pk)
        room_messages = room.message_set.all()#sdfsdfsdf
        participants = room.participants.all()

        if request.method == 'POST':
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=request.POST.get('body')
            )
            room.participants.add(request.user)
            return redirect('room', pk=room.id)
        context = {'room':room, 'room_messages':room_messages, 'participants':participants}
        return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms': rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' :room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You cannot!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' :message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    profile_form = UserProfileForm(instance=user)
    password_form = UserPasswordChangeForm(user)
    email_form = UserEmailChangeForm(user)
    delete_form = UserDeleteForm(user)

    if request.method == 'POST':
        if 'profile_update' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('update-user')

        elif 'password_change' in request.POST:
            password_form = UserPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been changed successfully.')
                return redirect('update-user')

        elif 'email_change' in request.POST:
            email_form = UserEmailChangeForm(user, request.POST)
            if email_form.is_valid():
                user.email = email_form.cleaned_data['new_email']
                user.save()
                messages.success(request, 'Your email has been changed successfully.')
                return redirect('update-user')

        elif 'delete_account' in request.POST:
            delete_form = UserDeleteForm(user, request.POST)
            if delete_form.is_valid():
                user.delete()
                logout(request)
                messages.success(request, 'Your account has been deleted successfully.')
                return redirect('home')  # Redirect to home or login page

    context = {
        'user': user,
        'profile_form': profile_form,
        'password_form': password_form,
        'email_form': email_form,
        'delete_form': delete_form,
    }
    return render(request, 'base/update-user-new.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') !=  None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})

#------------------------------------------------------------------------------------ end chat app section --------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------- start course section -------------------------------------------------------------------------------#
def calculate_progress(user, lesson):
    total_pages = lesson.lesson_pages.count()
    completed_pages = UserProgress.objects.filter(user=user, lesson_page__lesson=lesson, is_completed=True).count()
    if total_pages == 0:
        return 0
    return (completed_pages / total_pages) * 100

def calculate_classroom_progress(user, classroom):
    total_lessons = classroom.lessons.count()
    completed_lessons = ClassroomUserLessonProgress.objects.filter(user=user, lesson__classroom_group=classroom, is_completed=True).count()
    if total_lessons == 0:
        return 0
    return round((completed_lessons / total_lessons) * 100)

#@cache_page(timeout=60 * 30)  # cache for 30 minutes
def teachers_page(request):
    return render(request, 'base/teachers_page.html')

from django.db.models import Prefetch

#@cache_page(timeout=60 * 30, cache='valkey')  # cache for 30 minutes
def course_catalog(request):
    all_topics = Course.objects.filter(is_private=False).values_list('category', flat=True).distinct()
    trending_courses = Course.objects.filter(is_trending=True, is_private=False)
    featured_courses = Course.objects.filter(is_featured=True, is_private=False)
    all_courses = Course.objects.filter(is_private=False)
    
    context = {
        'all_topics': all_topics,
        'trending_courses': trending_courses,
        'featured_courses': featured_courses,
        'all_courses': all_courses,
    }
    return render(request, 'base/courses_page.html', context)

def lessons_landing_page_main(request):
    user = request.user
    today = date.today()
    one_week_from_now = today + timedelta(days=7)
    urgent_assignment = None

    if user.is_authenticated:
        # Get courses the user has progress for
        user_course_progress = UserCourseProgress.objects.filter(user=user).select_related('course')
        courses = [progress.course for progress in user_course_progress]
        user_projects = UserProject.objects.filter(user=user)
        # Get classrooms the user is a member of
        classrooms = ClassroomGroup.objects.filter(classroommembership__user=user).distinct()
        
        # Get assignments for the user
        assignments = Assignment.objects.filter(
            Q(classroom_group__classroommembership__user=user) |
            Q(course__in=courses)
        ).distinct().select_related('course', 'lesson', 'lesson_page')

        # Process assignments
        uncompleted_assignments = []
        for assignment in assignments:
            student_assignment = StudentAssignment.objects.filter(student=user, assignment=assignment).first()
            
            is_completed = False
            if student_assignment and student_assignment.is_completed:
                is_completed = True
            else:
                # Check completion based on assignment type
                if assignment.assignment_type == 'course':
                    course_progress = UserCourseProgress.objects.filter(user=user, course=assignment.course).first()
                    is_completed = course_progress.is_completed if course_progress else False
                elif assignment.assignment_type == 'lesson':
                    lesson_progress = UserLessonProgress.objects.filter(user=user, lesson=assignment.lesson).first()
                    is_completed = lesson_progress.is_completed if lesson_progress else False
                elif assignment.assignment_type == 'lesson_page':
                    page_progress = UserProgress.objects.filter(user=user, lesson_page=assignment.lesson_page).first()
                    is_completed = page_progress.is_completed if page_progress else False
            
            if not is_completed:
                uncompleted_assignment = {
                    'title': assignment.title,
                    'id': assignment.pk,
                    'description': assignment.description,
                    'type': assignment.get_assignment_type_display(),
                    'due_date': assignment.due_date,
                    'is_completed': is_completed
                }
                
                uncompleted_assignments.append(uncompleted_assignment)

                # Find an urgent assignment (due within the next 7 days)
                if assignment.due_date and today <= assignment.due_date.date() <= one_week_from_now:
                    urgent_assignment = uncompleted_assignment
                    if not urgent_assignment:
                        urgent_assignment = uncompleted_assignment
        context = {
            'user': user,
            'courses': courses,
            'classrooms': classrooms,
            'uncompleted_assignments': uncompleted_assignments,
            'urgent_assignment': urgent_assignment,
            'user_projects': user_projects,
        }

    else:
        context = {
            'user': user,
            'courses': [],
            'classrooms': [],
            'uncompleted_assignments': [],
            'urgent_assignment': None,
        }
    return render(request, 'base/new_lessons_landing_page.html', context)


@login_required
def create_project(request):
    user = request.user

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = user  # Assuming you want to associate the project with the user
            project.save()  # Save the project instance
            return redirect('project_view', project_id=project.id)
    else:
        form = ProjectForm()

    return render(request, 'base/create_project.html', {'form': form})



def calculate_assignment_progress(student_progress):
    # Implement logic to calculate assignment progress based on the type of assignment
    # This is a placeholder function - you'll need to implement the actual logic
    return 0  # Return a percentage (0-100)

def calculate_course_progress(user, course):
    total_lessons = course.lesson_set.count()
    completed_lessons = UserLessonProgress.objects.filter(user=user, lesson__course=course, is_completed=True).count()
    return (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0


def lesson_redirect(request, lesson_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    user = request.user if request.user.is_authenticated else None

    # Get all lesson pages for the lesson
    lesson_pages = LessonPage.objects.filter(lesson=lesson)

    # Get all UserProgress objects for the lesson pages
    user_progresses = UserProgress.objects.filter(user=user, lesson_page__in=lesson_pages)

    # Check if UserProgress objects exist for all lesson pages
    if user_progresses.count() == lesson_pages.count():
        # Check if all UserProgress objects are completed
        if all(progress.is_completed for progress in user_progresses):
            # All lesson pages are completed, redirect to the last lesson page
            last_lesson_page = lesson_pages.order_by('-order').first()
            return redirect('lesson_page_detail', lesson_id=lesson_id, lesson_page_id=last_lesson_page.pk)
        else:
            # Not all lesson pages are completed, redirect to the first uncompleted lesson page
            first_uncompleted_page = next((progress.lesson_page for progress in user_progresses if not progress.is_completed), None)
            return redirect('lesson_page_detail', lesson_id=lesson_id, lesson_page_id=first_uncompleted_page.pk)
    else:
        # Not all lesson pages have UserProgress objects, create them and redirect to the first one
        for lesson_page in lesson_pages:
            UserProgress.objects.get_or_create(user=user, lesson_page=lesson_page, defaults={'is_completed': False})
        first_lesson_page = lesson_pages.order_by('order').first()
        return redirect('lesson_page_detail', lesson_id=lesson_id, lesson_page_id=first_lesson_page.pk)

def calculate_classroom_progress(user, classroom):
    # Implement logic to calculate classroom progress
    # This is a placeholder function - you'll need to implement the actual logic
    return 0  # R


#@cache_page(timeout=60 * 30)  # cache for N minutes
def home_studybuddy(request):
    q = request.GET.get('q') if request.GET.get('q') !=  None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'room_messages': room_messages}
    return render(request, 'base/home_studybuddy.html', context)




@login_required
def dashboard(request):
    # Get the classroom memberships for the current user
    memberships = ClassroomMembership.objects.filter(user=request.user)

    # Get the classroom groups from the memberships
    classroom_groups = [membership.classroom_group for membership in memberships]

    # Get the lesson pages for the user's classrooms
    lesson_pages = []
    for membership in memberships:
        lessons = membership.classroom_group.lessons.all()
        for lesson in lessons:
            lesson_pages.extend(lesson.lesson_pages.all())

    # Find an urgent assignment (due within the next 7 days)
    today = date.today()
    one_week_from_now = today + timedelta(days=7)
    urgent_assignment = None
    for lesson_page in lesson_pages:
        user_progress = ClassroomUserLessonProgress.objects.filter(user=request.user, lesson=lesson_page.lesson, is_completed=False).first()
        if user_progress:
            due_date = user_progress.entered_at.date()
            if today <= due_date <= one_week_from_now:
                urgent_assignment = lesson_page
                break

    # Pass the data to the template
    context = {
        'classroom_groups': classroom_groups,
        'lesson_pages': lesson_pages,
        'urgent_assignment': urgent_assignment,
    }
    return render(request, 'base/dashboard.html', context)

from django.utils import timezone

@login_required
def classroom_detail(request, classroom_id):
    classroom = get_object_or_404(ClassroomGroup, id=classroom_id)
    announcements = ClassroomAnnouncement.objects.filter(classroom_group=classroom)

    memberships = ClassroomMembership.objects.filter(classroom_group=classroom, user=request.user)
    if not memberships:
        # The user is not a member of this classroom
        return redirect('dashboard')

    assignments = classroom.assignments.all()
    now = timezone.now()

    # Get completed assignments for the current user
    completed_assignments = StudentAssignment.objects.filter(student=request.user, is_completed=True).values_list('assignment_id', flat=True)

    context = {
        'classroom': classroom,
        'assignments': assignments,
        'now': now,
        'completed_assignments': completed_assignments,
        'announcements': announcements,
    }
    return render(request, 'base/classroomdetail.html', context)
from .forms import AssignmentForm


@login_required
@user_passes_test(is_teacher)
def create_assignment(request, classroom_id):
    classroom = get_object_or_404(ClassroomGroup, id=classroom_id)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.classroom_group = classroom
            assignment.assigned_by = request.user
            
            if form.cleaned_data['assignment_type'] == 'course':
                assignment.course = form.cleaned_data['course']
            elif form.cleaned_data['assignment_type'] == 'lesson':
                assignment.lesson = form.cleaned_data['lesson']
            elif form.cleaned_data['assignment_type'] == 'lesson_page':
                assignment.lesson_page = form.cleaned_data['lesson_page']
            
            assignment.save()

            for student in classroom.classroommembership_set.all():
                StudentAssignment.objects.create(
                    student=student.user,
                    assignment=assignment
                )

            messages.success(request, 'Assignment created successfully!')
            return redirect('teacherpage')  # Assume you have an assignment list view for a specific classroom
    else:
        form = AssignmentForm()

    context = {
        'form': form,
        'classroom': classroom
    }
    return render(request, 'base/create_assignment.html', context)


def joinClassroom(request):
    return render(request, 'base/joinClassroom.html')

def lessons_landing_page_classroom(request):
    return render(request, 'lessons_landingpage_classroom.html')

def admindashboard(request):
    classroom_groups = ClassroomGroup.objects.all()
    lessons = ClassroomLesson.objects.all()

    context = {
        'classroom_groups': classroom_groups,
        'lessons': lessons,
    }

    return render(request, 'base/admindashboard.html', context)

@login_required
@user_passes_test(is_teacher)
def create_classroom(request):
    return redirect('home')


def delete_classroom(request):
    return redirect('')


def lessons_landing_page(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)
    user = request.user

    lessons_with_progress = []
    is_authenticated = not isinstance(user, AnonymousUser)

    if is_authenticated:
        for lesson in lessons:
            # Ensure UserLessonProgress exists for each lesson
            UserLessonProgress.objects.get_or_create(user=user, lesson=lesson)

            # Get progress for each lesson page in the lesson
            lesson_pages_with_progress = []
            for lesson_page in lesson.lesson_pages.all():
                user_progress = UserProgress.objects.filter(user=user, lesson_page=lesson_page).first()
                lesson_page_status = 'completed' if user_progress and user_progress.is_completed else 'in_progress' if user_progress else 'not_started'
                lesson_pages_with_progress.append((lesson_page, lesson_page_status))

            # Determine overall lesson status
            lesson_progress = UserLessonProgress.objects.filter(user=user, lesson=lesson).first()
            lesson_status = 'completed' if lesson_progress and lesson_progress.is_completed else 'in_progress' if any(page[1] == 'in_progress' for page in lesson_pages_with_progress) else 'not_started'

            lessons_with_progress.append((lesson, lesson_status, lesson_pages_with_progress))
    else:
        for lesson in lessons:
            lesson_pages_with_progress = [(lesson_page, 'not_started') for lesson_page in lesson.lesson_pages.all()]
            lessons_with_progress.append((lesson, 'not_started', lesson_pages_with_progress))

    return render(request, 'base/lessons_landing_page.html', {
        'course': course,
        'lessons_with_progress': lessons_with_progress,
        'is_authenticated': is_authenticated
    })



from django.urls import reverse

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import Lesson, LessonPage, User, UserLessonProgress
import json
import html

from django.shortcuts import render, get_object_or_404, reverse
import html
import json
from .models import Lesson, LessonPage

def lesson_page_detail(request, lesson_id, lesson_page_id):
    lesson = get_object_or_404(Lesson, pk=lesson_id)
    lesson_page = get_object_or_404(LessonPage, pk=lesson_page_id)
    user = request.user if request.user.is_authenticated else None

    # Get the next and previous lesson pages
    next_lesson_page = LessonPage.objects.filter(lesson=lesson, order__gt=lesson_page.order).order_by('order').first()
    prev_lesson_page = LessonPage.objects.filter(lesson=lesson, order__lt=lesson_page.order).order_by('-order').first()

    # Get the saved compiler code from MongoDB
    saved_compiler_code = None
    if user:
        code_collection = get_code_collection()
        result = code_collection.find_one({'user_id': user.id, 'lesson_id': lesson_id}, {'_id': 0, 'saved_compiler_code': 1})
        if result:
            saved_compiler_code = result.get('saved_compiler_code')

    # If saved_compiler_code is None, set it to "type your code here"
    if saved_compiler_code is None:
        saved_compiler_code = "#Type your code here!"

    # Determine the next URL based on the user's authentication status
    if user:
        next_url = reverse('complete_lesson', args=[lesson_page.id])
    else:
        if next_lesson_page:
            next_url = reverse('lesson_page_detail', args=[lesson.id, next_lesson_page.id])
        else:
            next_url = reverse('dashboard')

    context = {
        'lesson': lesson,
        'lesson_page': lesson_page,
        'next_lesson_page': next_lesson_page,
        'prev_lesson_page': prev_lesson_page,
        'next_url': next_url,
        'tips': lesson_page.tips,
        'saved_compiler_code': html.unescape(saved_compiler_code),
        'lesson_id_json': json.dumps(lesson.id),
        'user_id_json': json.dumps(request.user.id) if user else None,
        'canvaSVG': lesson_page.svg_file,
    }

    if lesson_page.isContentPage:
        return render(request, 'base/lesson_page_detail_content.html', context)
    else:
        if request.user.is_authenticated:
            return render(request, 'base/testpage.html', context)
        else:
            return render(request, 'base/testpage3.html', context)


from django.utils import timezone

def lesson_page_detail_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    user = request.user if request.user.is_authenticated else None
    
    if user:
        student_assignment = StudentAssignment.objects.filter(student=user, assignment=assignment).first()
        if student_assignment and student_assignment.is_completed and assignment.assignment_type =='lesson':
            # Redirect to a different URL if the assignment is completed
            lesson = assignment.lesson
            return redirect(reverse('lesson_redirect', args=[lesson.id]))

    if assignment.assignment_type == 'lesson_page':
        lesson_page = assignment.lesson_page
        lesson = lesson_page.lesson
    elif assignment.assignment_type == 'lesson':
        lesson = assignment.lesson
        # Get the first incomplete lesson page or the first lesson page if none are completed
        completed_pages = UserProgress.objects.filter(user=user, lesson_page__lesson=lesson, is_completed=True).values_list('lesson_page__id', flat=True)
        lesson_page = LessonPage.objects.filter(lesson=lesson).exclude(id__in=completed_pages).order_by('order').first() or LessonPage.objects.filter(lesson=lesson).order_by('order').first()
    else:
        return HttpResponse("Invalid assignment type")

    if LessonPage.objects.filter(lesson=lesson, order__gt=lesson_page.order).order_by('order').first():
        next_lesson_page = LessonPage.objects.filter(lesson=lesson, order__gt=lesson_page.order).order_by('order').first()
    else:
        next_lesson_page = redirect('home')
    prev_lesson_page = LessonPage.objects.filter(lesson=lesson, order__lt=lesson_page.order).order_by('-order').first()
    
    next_url = reverse('complete_lesson_page_assignment', args=[lesson_page.id, assignment_id])
    prev_url = reverse('prev_lesson_page', args=[lesson_page.id, assignment_id]) if prev_lesson_page else None


    saved_compiler_code = "#Type your code here!"
    if user:
        code_collection = get_code_collection()
        result = code_collection.find_one({'user_id': user.id, 'lesson_id': lesson_page.id}, {'_id': 0, 'saved_compiler_code': 1})
        if result and result.get('saved_compiler_code'):
            saved_compiler_code = result['saved_compiler_code']
    
    context = {
        'assignment': assignment,
        'lesson_page': lesson_page,
        'next_lesson_page': next_lesson_page,
        'prev_lesson_page': prev_lesson_page,
        'next_url': next_url,
        'prev_url': prev_url,
        'tips': lesson_page.tips,
        'saved_compiler_code': html.unescape(saved_compiler_code),
        'lesson_id_json': json.dumps(lesson_page.id),
        'user_id_json': json.dumps(user.id) if user else None,
        'canvaSVG': lesson_page.svg_file,
    }

    if lesson_page.isContentPage:
        return render(request, 'base/lesson_page_detail_content_assignment.html', context)
    else:
        template = 'base/lesson_page_detail_noncontent.html' if user else 'base/testpage3.html'
        return render(request, template, context)
    
def prev_lesson_page(request, lesson_page_id, assignment_id):
    current_lesson_page = get_object_or_404(LessonPage, pk=lesson_page_id)
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    lesson = current_lesson_page.lesson
    user = request.user if request.user.is_authenticated else None

    # Get the previous lesson page
    prev_lesson_page = LessonPage.objects.filter(lesson=lesson, order__lt=current_lesson_page.order).order_by('-order').first()

    if not prev_lesson_page:
        # If there's no previous page, redirect to the current page
        return redirect('lesson_page_detail_assignment', assignment_id=assignment_id)

    next_lesson_page = LessonPage.objects.filter(lesson=lesson, order__gt=prev_lesson_page.order).order_by('order').first()
    
    next_url = reverse('lesson_page_detail_assignment', args=[assignment_id])
    prev_url = reverse('prev_lesson_page', args=[prev_lesson_page.id, assignment_id]) if LessonPage.objects.filter(lesson=lesson, order__lt=prev_lesson_page.order).exists() else None

    saved_compiler_code = "#Type your code here!"
    if user:
        code_collection = get_code_collection()
        result = code_collection.find_one({'user_id': user.id, 'lesson_id': prev_lesson_page.id}, {'_id': 0, 'saved_compiler_code': 1})
        if result and result.get('saved_compiler_code'):
            saved_compiler_code = result['saved_compiler_code']
    
    context = {
        'assignment': assignment,
        'lesson_page': prev_lesson_page,
        'next_lesson_page': next_lesson_page,
        'prev_lesson_page': LessonPage.objects.filter(lesson=lesson, order__lt=prev_lesson_page.order).order_by('-order').first(),
        'next_url': next_url,
        'prev_url': prev_url,
        'tips': prev_lesson_page.tips,
        'saved_compiler_code': html.unescape(saved_compiler_code),
        'lesson_id_json': json.dumps(prev_lesson_page.id),
        'user_id_json': json.dumps(user.id) if user else None,
        'canvaSVG': prev_lesson_page.svg_file,
    }

    if prev_lesson_page.isContentPage:
        return render(request, 'base/lesson_page_detail_content_assignment.html', context)
    else:
        template = 'base/lesson_page_detail_noncontent.html' if user else 'base/testpage3.html'
        return render(request, template, context)

@login_required
def complete_lesson_page_assignment(request, lesson_page_id, assignment_id):
    lesson_page = get_object_or_404(LessonPage, pk=lesson_page_id)
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    user = request.user
    
    # Mark the current lesson page as completed
    user_progress, created = UserProgress.objects.get_or_create(user=user, lesson_page=lesson_page)

   

    user_progress.is_completed = True
    user_progress.save()
    
    # Check if all lesson pages are completed for lesson type assignments
    if assignment.assignment_type == 'lesson':
        all_lesson_pages = LessonPage.objects.filter(lesson=assignment.lesson)
        all_completed = all(UserProgress.objects.filter(user=user, lesson_page=page, is_completed=True).exists() for page in all_lesson_pages)
        
        if all_completed:
            student_assignment, created = StudentAssignment.objects.get_or_create(student=user, assignment=assignment)
            student_assignment.is_completed = True
            student_assignment.completed_at = timezone.now()
            student_assignment.save()
            
            lesson_progress, created = UserLessonProgress.objects.get_or_create(user=user, lesson=assignment.lesson)
            lesson_progress.is_completed = True
            lesson_progress.save()
            
            return redirect('dashboard')  # Redirect to main page when all pages are completed
    elif assignment.assignment_type == 'lesson_page':
        student_assignment, created = StudentAssignment.objects.get_or_create(student=user, assignment=assignment)
        student_assignment.is_completed = True
        student_assignment.completed_at = timezone.now()
        student_assignment.save()
    
    # Find the next incomplete lesson page
    next_lesson_page = LessonPage.objects.filter(
        lesson=lesson_page.lesson,
        order__gt=lesson_page.order
    ).exclude(
        id__in=UserProgress.objects.filter(user=user, is_completed=True).values_list('lesson_page__id', flat=True)
    ).order_by('order').first()

    if next_lesson_page:
        return redirect('lesson_page_detail_assignment', assignment_id=assignment.id)
    else:
        # If no more incomplete pages, redirect to the main page
        return redirect('dashboard')

#hello how are you doing today?

from pymongo import MongoClient
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils.html import escape


client = MongoClient('#####')
db = client['#####']

def get_code_collection():
    return db['user_code']    

from django.views.decorators.csrf import csrf_protect
from django_ratelimit.decorators import ratelimit


@csrf_protect
@require_POST
@ratelimit(key='user', rate='50/m', block=True)  
@login_required
def save_code(request):
    try:
        # Load and parse the request body
        data = json.loads(request.body)
        user_id = request.user.id  # Get user_id from the authenticated user
        lesson_id = int(data.get('lesson'))  # Ensure lesson_id is an integer
        code = escape(data.get('saved_compiler_code', ''))  # Escape the code to prevent XSS


        # Validate that the lesson_id corresponds to a valid lesson or lesson page or user project
        is_valid_lesson = Lesson.objects.filter(id=lesson_id).exists()
        is_valid_lesson_page = LessonPage.objects.filter(id=lesson_id).exists()
        is_valid_user_project = UserProject.objects.filter(id=lesson_id).exists()

        if not (is_valid_lesson or is_valid_lesson_page or is_valid_user_project):
            raise PermissionDenied("Invalid lesson ID")


        # Check if the user has permission to save code for this lesson or lesson page or user project
        has_access = (
            UserCourseProgress.objects.filter(user_id=user_id, id=lesson_id).exists(),
            UserLessonProgress.objects.filter(user_id=user_id, lesson_id=lesson_id).exists() or
            UserProgress.objects.filter(user_id=user_id, lesson_page_id=lesson_id).exists() or
            UserProject.objects.filter(id=lesson_id, user_id=user_id).exists()
        )
        #print(has_access)

        if not has_access:
            raise PermissionDenied("You don't have permission to save code for this lesson")

        # Get the MongoDB collection where the code is stored
        code_collection = get_code_collection()

        # Update or insert the code into the database
        code_collection.update_one(
            {'user_id': user_id, 'lesson_id': lesson_id},
            {'$set': {'saved_compiler_code': code}},
            upsert=True
        )

        return JsonResponse({'status': 'success'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
    except PermissionDenied as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=500)


@login_required
def project_view(request, project_id):
    user = request.user if request.user.is_authenticated else None
    project = get_object_or_404(UserProject, id=project_id, user=user)

    saved_compiler_code = None
    if user:
        code_collection = get_code_collection()
        result = code_collection.find_one({'user_id': user.id, 'lesson_id': project.pk}, {'_id': 0, 'saved_compiler_code': 1})
        if result:
            saved_compiler_code = result.get('saved_compiler_code')

    if saved_compiler_code is None:
        saved_compiler_code = "#Type your code here!"

   
    context = {
        'saved_compiler_code': html.unescape(saved_compiler_code),
        'lesson_id_json': json.dumps(project.pk),
        'user_id_json': json.dumps(request.user.id) if user else None,
    }

    #print(project.pk)
    return render(request, 'base/project_detail.html', context)
    

def compiler(request):
    return render(request, 'base/compiler.html')



from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from .models import LessonPage, UserProgress, UserLessonProgress, UserCourseProgress, Assignment, StudentAssignment, StudentProgress

def complete_lesson(request, lesson_page_id):
    lesson_page = get_object_or_404(LessonPage, id=lesson_page_id)
    lesson = lesson_page.lesson
    course = lesson.course
    user = request.user

    if user.is_authenticated:
        # Mark the lesson page as completed
        user_progress, created = UserProgress.objects.get_or_create(user=user, lesson_page=lesson_page)
        user_progress.is_completed = True
        user_progress.save()

        # Check if all lesson pages of the lesson are completed
        lesson_pages = LessonPage.objects.filter(lesson=lesson)
        user_progresses = UserProgress.objects.filter(user=user, lesson_page__in=lesson_pages)
        if all(progress.is_completed for progress in user_progresses):
            # If all lesson pages are completed, mark the lesson as completed
            user_lesson_progress, created = UserLessonProgress.objects.get_or_create(user=user, lesson=lesson)
            user_lesson_progress.is_completed = True
            user_lesson_progress.save()

            # Check if all lessons of the course are completed
            if course:
                lessons = Lesson.objects.filter(course=course)
                user_lesson_progresses = UserLessonProgress.objects.filter(user=user, lesson__in=lessons)
                if all(progress.is_completed for progress in user_lesson_progresses):
                    # If all lessons are completed, mark the course as completed
                    user_course_progress, created = UserCourseProgress.objects.get_or_create(user=user, course=course)
                    user_course_progress.is_completed = True
                    user_course_progress.save()

                    # Check if this course is part of an assignment
                    course_assignments = Assignment.objects.filter(course=course, assignment_type='course')
                    for assignment in course_assignments:
                        student_assignment, created = StudentAssignment.objects.get_or_create(
                            student=user,
                            assignment=assignment
                        )
                        student_assignment.is_completed = True
                        student_assignment.save()

        # Redirect to lessons_landing_page if this is the last lesson page
        if course:
            if lesson_pages.count() == user_progresses.count() and all(progress.is_completed for progress in user_progresses):
                return redirect('lessons_landing_page', course_id=course.id)
            else:
                return redirect('lesson_redirect', lesson_id=lesson.pk) 

    return redirect('lesson_redirect', lesson_id=lesson.pk)  # Or redirect to another page



def get_next_lesson_page(current_lesson_page, lesson, course):
    if lesson:
        # Get all lesson pages for this lesson ordered by their order field
        lesson_pages = lesson.lesson_pages.order_by('order')
        current_index = list(lesson_pages).index(current_lesson_page)
        
        if current_index + 1 < len(lesson_pages):
            return lesson_pages[current_index + 1]
        else:
            # If this was the last page of the lesson, get the next lesson
            if course:
                lessons = course.lesson_set.order_by('id')
                current_lesson_index = list(lessons).index(lesson)
                if current_lesson_index + 1 < len(lessons):
                    next_lesson = lessons[current_lesson_index + 1]
                    return next_lesson.lesson_pages.order_by('order').first()
    elif course:
        # If there's no lesson, but there's a course, get the first lesson page of the first lesson
        first_lesson = course.lesson_set.order_by('id').first()
        if first_lesson:
            return first_lesson.lesson_pages.order_by('order').first()
    
    # If there are no more lesson pages in the course, or if there's no course, return None
    return None

def update_lesson_progress(user, lesson, student_assignment=None):
    lesson_progress, created = UserLessonProgress.objects.get_or_create(user=user, lesson=lesson)
    
    # Check if all lesson pages are completed
    all_pages_completed = all(
        UserProgress.objects.filter(user=user, lesson_page=page, is_completed=True).exists()
        for page in lesson.lesson_pages.all()
    )
    
    lesson_progress.is_completed = all_pages_completed
    lesson_progress.save()

    if student_assignment:
        student_assignment.is_completed = all_pages_completed
        student_assignment.save()

def update_course_progress(user, course, student_assignment=None):
    course_progress, created = UserCourseProgress.objects.get_or_create(user=user, course=course)
    
    # Check if all lessons are completed
    all_lessons_completed = all(
        UserLessonProgress.objects.filter(user=user, lesson=lesson, is_completed=True).exists()
        for lesson in course.lesson_set.all()
    )
    
    course_progress.is_completed = all_lessons_completed
    course_progress.save()

    if student_assignment:
        student_assignment.is_completed = all_lessons_completed
        student_assignment.save()

def check_course_completion(user, course, assignment=None):
    all_lessons_completed = all(
        UserLessonProgress.objects.filter(user=user, lesson=lesson, is_completed=True).exists()
        for lesson in course.lesson_set.all()
    )

    if all_lessons_completed:
        user_course_progress, _ = UserCourseProgress.objects.get_or_create(user=user, course=course)
        user_course_progress.is_completed = True
        user_course_progress.save()

        if assignment:
            student_assignment = StudentAssignment.objects.get(student=user, assignment=assignment)
            student_assignment.is_completed = True
            student_assignment.save()

def aboutPage(request):
    #return render(request, 'base/aboutPage.html')
    return render(request, 'base/aboutPage.html')


def opportunitiesPage(request):
    return render(request, 'base/opportunitiespage.html')
#----------------------Admin Stuff ---------------------

def adminHome(request):
    if request.user.is_superuser:
        lessons = Lesson.objects.all()
        return render(request, 'base/adminHome.html', {'lessons': lessons})
    else:
        return redirect('home')

def lessonAdminPage(request, lesson_id): 
    if request.user.is_superuser:
        lesson = Lesson.objects.get(id=lesson_id)
        lesson_pages = lesson.lesson_pages.all()
        context = {
        'lesson': lesson,
        'lesson_pages': lesson_pages,
        }
        return render(request, 'base/lessonAdminPage.html', context)
    else:
        return redirect('home')

def create_lesson_page(request, lesson_id):
    
    if request.user.is_superuser:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        form = LessonPageForm(request.POST)
        if request.method == 'POST':
            form = LessonPageForm(request.POST)
        if form.is_valid():
            lesson_page = form.save(commit=False)
            lesson_page.lesson = lesson
            lesson_page.save()
            return redirect('lesson_detail_admin', lesson_id=lesson.id)
        else:
            form = LessonPageForm()
        context = {'lesson': lesson, 'form': form}
        return render(request, 'base/createLessonPage.html', context)
    else:
        return redirect('home')

    
    
    

def delete_lesson_page(request, lesson_id, lesson_page_id):
    if request.user.is_superuser:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        lesson_page = get_object_or_404(LessonPage, id=lesson_page_id)
    
        if request.method == 'POST':
            lesson_page.delete()
            return redirect('lesson_detail_admin', lesson_id=lesson.id)

        context = {'lesson': lesson, 'lesson_page': lesson_page}
        return render(request, 'base/deleteLessonPage.html', context)
    
    else:
        return redirect('home')

def lesson_detail_admin(request, lesson_id):
    if request.user.is_superuser:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        lesson_pages = lesson.lesson_pages.all().order_by('order')
        context = {'lesson': lesson, 'lesson_pages': lesson_pages}
        return render(request, 'base/lessonDetailAdmin.html', context)    
    else:
        return render('home')

def edit_lesson_page(request, lesson_id, lesson_page_id):
    if request.user.is_superuser:
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        lesson_page = get_object_or_404(LessonPage, pk=lesson_page_id)

        if request.method == 'POST':
            form = LessonPageForm(request.POST, instance=lesson_page)
            if form.is_valid():
                form.save()
                return redirect('lesson_detail', lesson_id=lesson.id)
        else:
            form = LessonPageForm(instance=lesson_page)

        return render(request, 'base/lesson_page_edit_admin.html', {'form': form, 'lesson_page': lesson_page})
    else:
        return redirect('home')


@login_required
@user_passes_test(is_teacher)
def teacherpage(request):
    classrooms = ClassroomGroup.objects.filter(created_by=request.user).prefetch_related('assignments')
    
    
    courses = Course.objects.filter(author=request.user, is_private=True)
    lessons = Lesson.objects.filter(author=request.user)
    lesson_pages = LessonPage.objects.filter(author=request.user)

    def add_model_name(item):
        item.model_name = item.__class__.__name__.lower()
        return item

    recent_updates = sorted(
        [add_model_name(course) for course in courses] +
        [add_model_name(lesson) for lesson in lessons] +
        [add_model_name(lesson_page) for lesson_page in lesson_pages],
        key=lambda x: x.last_updated,
        reverse=True
    )[:5]
    
    context = {
        'courses': courses,
        'lessons': lessons,
        'lesson_pages': lesson_pages,
        'recent_updates': recent_updates,
        'classrooms': classrooms,
        'active_tab': request.GET.get('active_tab', 'home'),  # Default to 'home' if not specified
    }
    return render(request, 'base/new_teacherpage_v2.html', context)


@login_required
@user_passes_test(is_teacher)
def createclassroom(request):
    user = request.user
    classroom_count = ClassroomGroup.objects.filter(created_by=user).count()

    if not user.is_super_teacher and classroom_count >= 3:
        return render(request, 'base/classroom_limit_error.html', {'classroom_count': classroom_count})

    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.created_by = user
            classroom.save()
            return redirect('teacherpage')
    else:
        form = ClassroomForm()
    
    return render(request, 'base/createclassroom.html', {'form': form})

@login_required
def joinclassroom(request):
    if request.method == 'POST':
        form = JoinClassroomForm(request.POST)
        if form.is_valid():
            if form.join_classroom(request.user):
                messages.success(request, "Successfully joined the classroom.")
                return redirect('dashboard')
    else:
        form = JoinClassroomForm()
    return render(request, 'base/joinClassroom.html', {'form': form})


@login_required
@user_passes_test(is_teacher)
def teacherclassroomdetail(request, classroom_id):
    classroom = get_object_or_404(ClassroomGroup, id=classroom_id, created_by=request.user)
    students = ClassroomMembership.objects.filter(classroom_group=classroom).select_related('user')
    assignments = Assignment.objects.filter(classroom_group=classroom)
    announcements = ClassroomAnnouncement.objects.filter(classroom_group=classroom)
    student_progress = StudentProgress.objects.filter(assignment__classroom_group=classroom).select_related('student', 'assignment')
    context = {
        'classroom': classroom,
        'students': students,
        'assignments': assignments,
        'student_progress': student_progress,
        'announcements': announcements,
    }

    return render(request, 'base/teacherclassroomdetail.html', context)


#courses section


@login_required
def user_course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if course.is_private:
        # Check if the course is part of an assignment for this user
        assignment = Assignment.objects.filter(course=course, classroom_group__classroommembership__user=request.user).first()
        if assignment:
            return render(request, 'go/course_detail.html', {'course': course, 'assignment': assignment})
        else:
            # Return forbidden if the user does not have access to the course
            return render(request, 'go/course_detail.html', {'course': course, 'assignment': assignment}) #TEMPORARY!!!!!
    else:
        # Public course, render course details
        return render(request, 'go/course_detail.html', {'course': course})
        
@login_required
def user_course_lesson_view(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    if lesson.is_private:
        assignment = Assignment.objects.filter(course=course, classroom_group__classroommembership__user=request.user).first()
        if not assignment:
            pass
    
    return render(request, 'go/course_lesson_detail.html', {'course': course, 'lesson': lesson})

@login_required
def user_course_lesson_page_view(request, course_id, lesson_id, lesson_page_id):
    course = get_object_or_404(Course, id=course_id)
    lesson_page = get_object_or_404(LessonPage, id=lesson_page_id, lesson__course=course)
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user = request.user

    
    if lesson_page.is_private:
        assignment = Assignment.objects.filter(
            lesson_page=lesson_page,
            classroom_group__classroommembership__user=request.user
        ).first()
        if not assignment:
            pass
    
    # Check if the user has completed this lesson page
    user_progress = UserProgress.objects.filter(user=request.user, lesson_page=lesson_page).first()
    if user_progress and user_progress.is_completed:
        # Get the next lesson page in the course
        next_lesson_page = LessonPage.objects.filter(lesson__course=course, order__gt=lesson_page.order).order_by('order').first()
        if next_lesson_page:
            next_url = reverse('user_course_lesson_page_view', args=[course.id, lesson.id, next_lesson_page.id])
        else:
            next_url = reverse('user_course_view', args=[course.id])  # Redirect to course overview if no more lesson pages
    else:
        next_url = reverse('complete_user_course_lesson_page', args=[course.id, lesson_page.id])

    prev_lesson_page = LessonPage.objects.filter(lesson__course=course, order__lt=lesson_page.order).order_by('-order').first()
    if prev_lesson_page:
        prev_url = reverse('user_course_lesson_page_view', args=[course.id, lesson_id, prev_lesson_page.id])
    else:
        prev_url = reverse('dashboard')  # Link back to the dashboard if no previous page


    saved_compiler_code = None
    if user:
        code_collection = get_code_collection()
        result = code_collection.find_one({'user_id': user.id, 'lesson_id': lesson.pk}, {'_id': 0, 'saved_compiler_code': 1})
        if result:
            saved_compiler_code = result.get('saved_compiler_code')

    if saved_compiler_code is None:
        saved_compiler_code = "#Type your code here!"

    

    context = {
        'course': course,
        'lesson_page': lesson_page,
        'next_url': next_url,
        'prev_url': prev_url,
        'course_id':course.id,
        'lesson_id': lesson_id,
        'saved_compiler_code': html.unescape(saved_compiler_code),
        'lesson_id_json': json.dumps(lesson.id),
        'user_id_json': json.dumps(request.user.id) if user else None,
    }

    if lesson_page.isContentPage:
        return render(request, 'go/course_lesson_page_detail_content.html', context)
    else:
        return render(request, 'go/course_lesson_page_detail_coding.html', context)
    
@login_required
def user_lesson_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if lesson.is_private:
        assignment = Assignment.objects.filter(
            lesson=lesson, 
            classroom_group__classroommembership__user=request.user
        ).first()
        if not assignment:
            pass
    
    return render(request, 'go/lesson_detail.html', {'lesson': lesson})

@login_required
def user_lesson_lesson_page_view(request, lesson_id, lesson_page_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson_page = get_object_or_404(LessonPage, id=lesson_page_id, lesson=lesson)
    user = request.user
    
    if lesson_page.is_private:
        assignment = Assignment.objects.filter(
            lesson_page=lesson_page,
            classroom_group__classroommembership__user=request.user
        ).first()
        if not assignment:
            pass
    
    # Check if the user has completed this lesson page
    user_progress = UserProgress.objects.filter(user=request.user, lesson_page=lesson_page).first()
    if user_progress and user_progress.is_completed:
        # Get the next lesson page in the lesson or course
        next_lesson_page = LessonPage.objects.filter(lesson=lesson, order__gt=lesson_page.order).order_by('order').first()
        if next_lesson_page:
            next_url = reverse('user_lesson_lesson_page_view', args=[lesson.id, next_lesson_page.id])
        else:
            next_url = reverse('user_lesson_view', args=[lesson.id])  # Redirect to course overview if no more lesson pages
    else:
        # If not completed, return the submit URL for the current lesson page
        next_url = reverse('complete_lesson_lesson_page', args=[lesson.id, lesson_page.id])
    
    prev_lesson_page = LessonPage.objects.filter(lesson=lesson, order__lt=lesson_page.order).order_by('-order').first()

    if prev_lesson_page:
        prev_url = reverse('user_lesson_lesson_page_view', args=[lesson.id, prev_lesson_page.id])
    else:
        prev_url = reverse('dashboard')  # Link back to the dashboard if no previous page

    saved_compiler_code = None
    if user:
        code_collection = get_code_collection()
        result = code_collection.find_one({'user_id': user.id, 'lesson_id': lesson.pk}, {'_id': 0, 'saved_compiler_code': 1})
        if result:
            saved_compiler_code = result.get('saved_compiler_code')

    if saved_compiler_code is None:
        saved_compiler_code = "#Type your code here!"

    context = {
        'lesson': lesson,
        'lesson_page': lesson_page,
        'next_url': next_url,
        'prev_url': prev_url,
        'lesson_id': lesson.id,
        'saved_compiler_code': html.unescape(saved_compiler_code),
        'lesson_id_json': json.dumps(lesson.id),
        'user_id_json': json.dumps(user.id) if user else None,

    }

    if lesson_page.isContentPage:
        return render(request, 'go/lesson_lesson_page_detail_content.html', context)
    else:
        return render(request, 'go/lesson_lesson_page_detail_coding.html', context)

@login_required
def user_lesson_page_view(request, lesson_page_id):
    lesson_page = get_object_or_404(LessonPage, id=lesson_page_id)
    user = request.user

    if lesson_page.is_private:
        assignment = Assignment.objects.filter(
            lesson_page=lesson_page,
            classroom_group__classroommembership__user=request.user
        ).first()
        if not assignment:
            pass
    
    # Check if the user has completed this lesson page
    user_progress = UserProgress.objects.filter(user=request.user, lesson_page=lesson_page).first()
    if user_progress and user_progress.is_completed:
        # Get the next lesson page (if any)
        next_lesson_page = LessonPage.objects.filter(lesson=lesson_page.lesson, order__gt=lesson_page.order).order_by('order').first()
        if next_lesson_page:
            next_url = reverse('user_lesson_page_view', args=[next_lesson_page.id])
        else:
            next_url = reverse('dashboard')
    else:
        next_url = reverse('complete_lesson_page', args=[lesson_page.id])

    prev_lesson_page = LessonPage.objects.filter(lesson=lesson_page.lesson, order__lt=lesson_page.order).order_by('-order').first()
    if prev_lesson_page:
        prev_url = reverse('user_lesson_page_view', args=[prev_lesson_page.id])
    else:
        prev_url = reverse('dashboard')  # Link back to the dashboard if no previous page
    
    saved_compiler_code = None
    if user:
        code_collection = get_code_collection()
        result = code_collection.find_one({'user_id': user.id, 'lesson_id': lesson_page.pk}, {'_id': 0, 'saved_compiler_code': 1})
        if result:
            saved_compiler_code = result.get('saved_compiler_code')

    if saved_compiler_code is None:
        saved_compiler_code = "#Type your code here!"
    

    context = {
        'lesson_page': lesson_page,
        'next_url': next_url,
        'prev_url': prev_url,
        'saved_compiler_code': html.unescape(saved_compiler_code),
        'lesson_id_json': json.dumps(lesson_page.pk),
        'user_id_json': json.dumps(request.user.id) if user else None,
    }

    print(saved_compiler_code)
    print(lesson_page.pk)
    print(user.pk)

    if lesson_page.isContentPage:
        return render(request, 'go/lesson_page_detail_content.html', context)
    else:
        return render(request, 'go/lesson_page_detail_coding.html', context)


from django.http import HttpResponseRedirect

@login_required
def complete_user_course_lesson_page(request, course_id, lesson_id, lesson_page_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    lesson_page = get_object_or_404(LessonPage, id=lesson_page_id, lesson=lesson)
    
    # Check if the lesson page is already completed
    user_progress, created = UserProgress.objects.get_or_create(user=request.user, lesson_page=lesson_page)
    
    if user_progress.is_completed:
        # If already completed, find the next uncompleted lesson page
        next_uncompleted_page = LessonPage.objects.filter(
            lesson__course=course,
            order__gt=lesson_page.order
        ).exclude(
            userprogress__user=request.user,
            userprogress__is_completed=True
        ).order_by('lesson__order', 'order').first()
        
        if next_uncompleted_page:
            return HttpResponseRedirect(reverse('user_course_lesson_page_view', kwargs={
                'course_id': course.id,
                'lesson_id': next_uncompleted_page.lesson.id,
                'lesson_page_id': next_uncompleted_page.id
            }))
        else:
            return redirect('dashboard')
    
    # Mark the lesson page as complete
    user_progress.is_completed = True
    user_progress.save()
    
    # Check if this lesson page is part of an assignment
    assignment = Assignment.objects.filter(
        classroom_group__classroommembership__user=request.user,
        assignment_type='lesson_page',
        lesson_page=lesson_page
    ).first()
    
    if assignment:
        student_assignment, _ = StudentAssignment.objects.get_or_create(student=request.user, assignment=assignment)
        student_progress, _ = StudentProgress.objects.get_or_create(student=request.user, assignment=assignment)
        student_progress.lesson_page_progress = user_progress
        student_progress.is_completed = True
        student_progress.save()
        
        student_assignment.is_completed = True
        student_assignment.completed_at = timezone.now()
        student_assignment.save()
    
    # Check if all lesson pages in the lesson are completed
    total_lesson_pages = lesson.lesson_pages.count()
    completed_lesson_pages = UserProgress.objects.filter(
        user=request.user,
        lesson_page__lesson=lesson,
        is_completed=True
    ).count()
    
    if total_lesson_pages == completed_lesson_pages:
        user_lesson_progress, _ = UserLessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        user_lesson_progress.is_completed = True
        user_lesson_progress.save()
        
        # Check if the lesson is part of an assignment
        lesson_assignment = Assignment.objects.filter(
            classroom_group__classroommembership__user=request.user,
            assignment_type='lesson',
            lesson=lesson
        ).first()
        
        if lesson_assignment:
            student_lesson_assignment, _ = StudentAssignment.objects.get_or_create(student=request.user, assignment=lesson_assignment)
            student_lesson_progress, _ = StudentProgress.objects.get_or_create(student=request.user, assignment=lesson_assignment)
            student_lesson_progress.lesson_progress = user_lesson_progress
            student_lesson_progress.is_completed = True
            student_lesson_progress.save()
            
            student_lesson_assignment.is_completed = True
            student_lesson_assignment.completed_at = timezone.now()
            student_lesson_assignment.save()
    
    # Check if all lessons in the course are completed
    total_lessons = course.lesson_set.count()
    completed_lessons = UserLessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        is_completed=True
    ).count()
    
    if total_lessons == completed_lessons:
        user_course_progress, _ = UserCourseProgress.objects.get_or_create(user=request.user, course=course)
        user_course_progress.is_completed = True
        user_course_progress.save()
        
        # Check if the course is part of an assignment
        course_assignment = Assignment.objects.filter(
            classroom_group__classroommembership__user=request.user,
            assignment_type='course',
            course=course
        ).first()
        
        if course_assignment:
            student_course_assignment, _ = StudentAssignment.objects.get_or_create(student=request.user, assignment=course_assignment)
            student_course_progress, _ = StudentProgress.objects.get_or_create(student=request.user, assignment=course_assignment)
            student_course_progress.course_progress = user_course_progress
            student_course_progress.is_completed = True
            student_course_progress.save()
            
            student_course_assignment.is_completed = True
            student_course_assignment.completed_at = timezone.now()
            student_course_assignment.save()
    
    # Find the next uncompleted lesson page
    next_uncompleted_page = LessonPage.objects.filter(
        lesson__course=course,
        order__gt=lesson_page.order
    ).exclude(
        userprogress__user=request.user,
        userprogress__is_completed=True
    ).order_by('lesson__order', 'order').first()
    
    if next_uncompleted_page:
        return HttpResponseRedirect(reverse('user_course_lesson_page_view', kwargs={
            'course_id': course.id,
            'lesson_id': next_uncompleted_page.lesson.id,
            'lesson_page_id': next_uncompleted_page.id
        }))
    else:
        return redirect('dashboard')

@login_required
def complete_lesson_lesson_page_page(request, lesson_id, lesson_page_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    lesson_page = get_object_or_404(LessonPage, id=lesson_page_id, lesson=lesson)
    
    # Check if the lesson page is already completed
    user_progress, created = UserProgress.objects.get_or_create(user=request.user, lesson_page=lesson_page)
    
    if user_progress.is_completed:
        # If already completed, find the next uncompleted lesson page
        next_uncompleted_page = LessonPage.objects.filter(
            lesson=lesson,
            order__gt=lesson_page.order
        ).exclude(
            userprogress__user=request.user,
            userprogress__is_completed=True
        ).order_by('order').first()
        
        if next_uncompleted_page:
            return HttpResponseRedirect(reverse('user_lesson_lesson_page_view', kwargs={
                'lesson_id': lesson.id,
                'lesson_page_id': next_uncompleted_page.id
            }))
        else:
            return redirect('dashboard')
    
    # Mark the lesson page as complete
    user_progress.is_completed = True
    user_progress.save()
    
    # Check if this lesson page is part of an assignment
    assignment = Assignment.objects.filter(
        classroom_group__classroommembership__user=request.user,
        assignment_type='lesson_page',
        lesson_page=lesson_page
    ).first()
    
    if assignment:
        student_assignment, _ = StudentAssignment.objects.get_or_create(student=request.user, assignment=assignment)
        student_progress, _ = StudentProgress.objects.get_or_create(student=request.user, assignment=assignment)
        student_progress.lesson_page_progress = user_progress
        student_progress.is_completed = True
        student_progress.save()
        
        student_assignment.is_completed = True
        student_assignment.completed_at = timezone.now()
        student_assignment.save()
    
    # Check if all lesson pages in the lesson are completed
    total_lesson_pages = lesson.lesson_pages.count()
    completed_lesson_pages = UserProgress.objects.filter(
        user=request.user,
        lesson_page__lesson=lesson,
        is_completed=True
    ).count()
    
    if total_lesson_pages == completed_lesson_pages:
        user_lesson_progress, _ = UserLessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        user_lesson_progress.is_completed = True
        user_lesson_progress.save()
        
        # Check if the lesson is part of an assignment
        lesson_assignment = Assignment.objects.filter(
            classroom_group__classroommembership__user=request.user,
            assignment_type='lesson',
            lesson=lesson
        ).first()
        
        if lesson_assignment:
            student_lesson_assignment, _ = StudentAssignment.objects.get_or_create(student=request.user, assignment=lesson_assignment)
            student_lesson_progress, _ = StudentProgress.objects.get_or_create(student=request.user, assignment=lesson_assignment)
            student_lesson_progress.lesson_progress = user_lesson_progress
            student_lesson_progress.is_completed = True
            student_lesson_progress.save()
            
            student_lesson_assignment.is_completed = True
            student_lesson_assignment.completed_at = timezone.now()
            student_lesson_assignment.save()
    
    # Find the next uncompleted lesson page
    next_uncompleted_page = LessonPage.objects.filter(
        lesson=lesson,
        order__gt=lesson_page.order
    ).exclude(
        userprogress__user=request.user,
        userprogress__is_completed=True
    ).order_by('order').first()
    
    if next_uncompleted_page:
        return HttpResponseRedirect(reverse('user_lesson_lesson_page_view', kwargs={
            'lesson_id': lesson.id,
            'lesson_page_id': next_uncompleted_page.id
        }))
    else:
        return redirect('dashboard')

@login_required
def complete_lesson_page_page(request, lesson_page_id):
    lesson_page = get_object_or_404(LessonPage, id=lesson_page_id)
    
    # Check if the lesson page is already completed
    user_progress, created = UserProgress.objects.get_or_create(user=request.user, lesson_page=lesson_page)
    
    if user_progress.is_completed:
        # If already completed, redirect to the dashboard
        return redirect('dashboard')
    
    # Mark the lesson page as complete
    user_progress.is_completed = True
    user_progress.save()
    
    # Check if this lesson page is part of an assignment
    assignment = Assignment.objects.filter(
        classroom_group__classroommembership__user=request.user,
        assignment_type='lesson_page',
        lesson_page=lesson_page
    ).first()
    
    if assignment:
        student_assignment, _ = StudentAssignment.objects.get_or_create(student=request.user, assignment=assignment)
        student_progress, _ = StudentProgress.objects.get_or_create(student=request.user, assignment=assignment)
        student_progress.lesson_page_progress = user_progress
        student_progress.is_completed = True
        student_progress.save()
        
        student_assignment.is_completed = True
        student_assignment.completed_at = timezone.now()
        student_assignment.save()
    
    # If the lesson page is part of a lesson, check if the lesson is completed
    if lesson_page.lesson:
        total_lesson_pages = lesson_page.lesson.lesson_pages.count()
        completed_lesson_pages = UserProgress.objects.filter(
            user=request.user,
            lesson_page__lesson=lesson_page.lesson,
            is_completed=True
        ).count()
        
        if total_lesson_pages == completed_lesson_pages:
            user_lesson_progress, _ = UserLessonProgress.objects.get_or_create(user=request.user, lesson=lesson_page.lesson)
            user_lesson_progress.is_completed = True
            user_lesson_progress.save()
            
            # Check if the lesson is part of an assignment
            lesson_assignment = Assignment.objects.filter(
                classroom_group__classroommembership__user=request.user,
                assignment_type='lesson',
                lesson=lesson_page.lesson
            ).first()
            
            if lesson_assignment:
                student_lesson_assignment, _ = StudentAssignment.objects.get_or_create(student=request.user, assignment=lesson_assignment)
                student_lesson_progress, _ = StudentProgress.objects.get_or_create(student=request.user, assignment=lesson_assignment)
                student_lesson_progress.lesson_progress = user_lesson_progress
                student_lesson_progress.is_completed = True
                student_lesson_progress.save()
                
                student_lesson_assignment.is_completed = True
                student_lesson_assignment.completed_at = timezone.now()
                student_lesson_assignment.save()
        
        # Find the next uncompleted lesson page
        next_uncompleted_page = LessonPage.objects.filter(
            lesson=lesson_page.lesson,
            order__gt=lesson_page.order
        ).exclude(
            userprogress__user=request.user,
            userprogress__is_completed=True
        ).order_by('order').first()
        
        if next_uncompleted_page:
            return HttpResponseRedirect(reverse('user_lesson_page_view', kwargs={
                'lesson_id': lesson_page.lesson.id,
                'lesson_page_id': next_uncompleted_page.id
            }))
    
    # If there's no next page or it's a standalone lesson page, redirect to dashboard
    return redirect('dashboard')










































@login_required
@user_passes_test(is_teacher)
def create_announcement(request, classroom_id):
    classroom_group = get_object_or_404(ClassroomGroup, id=classroom_id)

    if request.method == 'POST':
        form = ClassroomAnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.user = request.user
            announcement.classroom_group = classroom_group
            announcement.save()
            return redirect('teacherpage')
    else:
        form = ClassroomAnnouncementForm()

    return render(request, 'base/create_announcement.html', {
        'form': form,
        'classroom_group': classroom_group
    })

@login_required
@user_passes_test(is_teacher)
def create_content(request):
    if request.method == 'POST':
        if 'create_course' in request.POST:
            course_form = CourseForm(request.POST)
            if course_form.is_valid():
                course = course_form.save(commit=False)
                course.author = request.user
                course.save()
                return redirect('create_content')
        
        elif 'create_lesson' in request.POST:
            lesson_form = LessonForm(request.POST, user=request.user)
            if lesson_form.is_valid():
                lesson = lesson_form.save(commit=False)
                lesson.author = request.user
                lesson.save()
                return redirect('create_content')
    
    else:
        course_form = CourseForm()
        lesson_form = LessonForm(user=request.user)
    
    courses = Course.objects.filter(author=request.user, is_private=True)
    lessons = Lesson.objects.filter(author=request.user)
    lesson_pages = LessonPage.objects.filter(author=request.user)

    # Add the model name to each item
    def add_model_name(item):
        item.model_name = item.__class__.__name__.lower()
        return item

    recent_updates = sorted(
        [add_model_name(course) for course in courses] +
        [add_model_name(lesson) for lesson in lessons] +
        [add_model_name(lesson_page) for lesson_page in lesson_pages],
        key=lambda x: x.last_updated,
        reverse=True
    )[:5]
    
    context = {
        'course_form': course_form,
        'lesson_form': lesson_form,
        'courses': courses,
        'lessons': lessons,
        'recent_updates': recent_updates,
    }
    return render(request, 'base/create_content.html', context)

@login_required
@user_passes_test(is_teacher)
def course_create_view(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user

            form.save()
            return redirect('teacherpage')
    else:
        form = CourseForm()
    return render(request, 'base/course_form.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def lesson_create_view(request, course_id=None):
    initial = {}
    if course_id:
        initial['course'] = Course.objects.get(pk=course_id)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, initial=initial)
        if form.is_valid():
            lesson = form.save(commit=False)

            lesson.author = request.user

            form.save()
            return redirect('teacherpage')
    else:
        form = LessonForm(initial=initial)
    return render(request, 'base/lesson_form.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def course_lesson_create_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        form = CourseLessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.author = request.user
            lesson.save()
            return redirect('course_view', course_id=course.id)
    else:
        form = CourseLessonForm()
    
    return render(request, 'base/courselessonform.html', {'form': form, 'course': course})

@login_required
@user_passes_test(is_teacher)
def lesson_lesson_page_create_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    content_form = ContentLessonPageForm(prefix='content', initial={'lesson': lesson, 'isContentPage': True})
    non_content_form = NonContentLessonPageForm(prefix='non_content', initial={'lesson': lesson, 'isContentPage': False})

    request.session['previous_page'] = request.GET.get('next', 'teacherpage')

    if request.method == 'POST':
        if 'content_submit' in request.POST:
            form = ContentLessonPageForm(request.POST, request.FILES, prefix='content')
        elif 'non_content_submit' in request.POST:
            form = NonContentLessonPageForm(request.POST, request.FILES, prefix='non_content')
            print("Non-content form submitted")

        else:
            form = None

        if form and form.is_valid():
            lesson_page = form.save(commit=False)
            lesson_page.lesson = lesson
            lesson_page.author = request.user
            
            # Auto-order the lesson page to the end of the lesson
            lesson_page.order = LessonPage.objects.filter(lesson=lesson).count() + 1

            lesson_page.save()

            return redirect(request.session.get('previous_page', 'teacherpage'))
    
    context = {
        'lesson': lesson,
        'content_form': content_form,
        'non_content_form': non_content_form,
    }
    return render(request, 'base/lesson_lesson_page_form.html', context)



from .forms import ContentLessonPageForm, NonContentLessonPageForm
from django.core.exceptions import ValidationError

@login_required
@user_passes_test(is_teacher)
def lesson_page_create_view(request, lesson_id=None):
    content_form = ContentLessonPageForm(prefix='content', initial={'isContentPage': True})
    non_content_form = NonContentLessonPageForm(prefix='non_content', initial={'isContentPage': False})

    if request.method == 'POST':
        if 'content_submit' in request.POST:
            form = ContentLessonPageForm(request.POST, request.FILES, prefix='content')
        elif 'non_content_submit' in request.POST:
            form = NonContentLessonPageForm(request.POST, request.FILES, prefix='non_content')
        else:
            form = None

        if form and form.is_valid():
            lesson_page = form.save(commit=False)
            lesson_page.author = request.user
            lesson_page.save()

            return redirect('teacherpage')
    
    context = {
        'content_form': content_form,
        'non_content_form': non_content_form,
    }
    return render(request, 'base/lesson_page_form.html', context)

def get_next_order(lesson):
    if lesson:
        return LessonPage.objects.filter(lesson=lesson).count() + 1
    else:
        return 1

@login_required
def edit_classroom(request, classroom_id):
    classroom = get_object_or_404(ClassroomGroup, id=classroom_id, created_by=request.user)
    
    if request.method == 'POST':
        form = ClassroomGroupForm(request.POST, request.FILES, instance=classroom)
        if form.is_valid():
            form.save()
            return redirect('teacherclassroomdetail', classroom.id)
    else:
        form = ClassroomGroupForm(instance=classroom)
    
    return render(request, 'base/edit_classroom.html', {'form': form, 'classroom': classroom})

@login_required
@user_passes_test(is_teacher)
def course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id, author=request.user)
    lessons = course.lesson_set.all().order_by('order')
    context = {
        'course': course,
        'lessons': lessons,
    }
    return render(request, 'base/course_view.html', context)

@login_required
@user_passes_test(is_teacher)
def course_lesson_page_view(request, course_id, lesson_page_id):
    return render(request, 'base/course_lesson_page_view.html')

@login_required
@user_passes_test(is_teacher)
def lesson_view(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, author=request.user)
    lesson_pages = lesson.lesson_pages.all().order_by('order')  # Fetch all related lesson pages
    context = {
        'lesson': lesson,
        'lesson_pages': lesson_pages,
    }
    return render(request, 'base/lesson_view.html', context)


@login_required
@user_passes_test(is_teacher)
def lesson_lesson_page_view(request, lesson_id, lesson_page_id):
    return render(request, 'base/lesson_lesson_page_view.html')

@login_required
@user_passes_test(is_teacher)
def lesson_page_view(request, lesson_page_id):
    return render(request, 'base/lesson_page_view.html')

@login_required
@user_passes_test(is_teacher)
def lesson_page_edit(request, lesson_page_id):
    lesson_page = get_object_or_404(LessonPage, id=lesson_page_id)
    
    # Store the current page URL in the session
    request.session['previous_page'] = request.GET.get('next', 'teacherpage')
    
    if request.method == 'POST':
        if lesson_page.isContentPage:
            form = EditContentLessonPageForm(request.POST, request.FILES, instance=lesson_page)
        else:
            form = EditNonContentLessonPageForm(request.POST, request.FILES, instance=lesson_page)
        
        if form.is_valid():
            form.save()
            # Redirect to the stored previous page
            del request.session['previous_page']
            return redirect(request.session.get('previous_page', 'teacherpage'))
        
    else:
        if lesson_page.isContentPage:
            form = EditContentLessonPageForm(instance=lesson_page)
        else:
            form = EditNonContentLessonPageForm(instance=lesson_page)

    context = {
        'form': form,
        'lesson_page': lesson_page,
    }
    return render(request, 'base/lesson_page_edit.html', context)

@login_required
@user_passes_test(is_teacher)
def course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id, author=request.user)
    
    if request.method == 'POST':
        form = EditCourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_view', course.id)
    else:
        form = EditCourseForm(instance=course)
    return render(request, 'base/course_edit.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def lesson_edit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Store the current page URL in the session
    request.session['previous_page'] = request.GET.get('next', 'teacherpage')
    
    if request.method == 'POST':
        form = EditLessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            # Redirect to the stored previous page
            del request.session['previous_page']

            return redirect(request.session.get('previous_page', 'teacherpage'))
    else:
        form = EditLessonForm(instance=lesson)
    return render(request, 'base/lesson_edit.html', {'form': form})







@csrf_protect
@require_POST
@ratelimit(key='user', rate='50/m', block=True)  
@login_required
@user_passes_test(is_teacher)
def update_lesson_order(request):
    try:
        data = json.loads(request.body)
        for item in data:
            lesson = Lesson.objects.get(id=item['id'])
            lesson.order = item['order']
            lesson.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_protect
@require_POST
@ratelimit(key='user', rate='50/m', block=True)  
@login_required
@user_passes_test(is_teacher)
def update_lesson_page_order(request):
    try:
        data = json.loads(request.body)
        for item in data:
            page = LessonPage.objects.get(id=item['id'])
            page.order = item['order']
            page.lesson_id = item['lessonId']
            page.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})







def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    request.session['previous_page'] = request.GET.get('next', 'teacherpage')


    if request.method == 'POST':
        course.delete()

        return redirect(request.session.get('previous_page', 'teacherpage'))

    return render(request, 'base/delete_confirm.html', {'object': course, 'type': 'Course'})

# Delete Lesson
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    request.session['previous_page'] = request.GET.get('next', 'teacherpage')


    if request.method == 'POST':
        lesson.delete()

        return redirect(request.session.get('previous_page', 'teacherpage'))

    return render(request, 'base/delete_confirm.html', {'object': lesson, 'type': 'Lesson'})

# Delete LessonPage
def delete_lessonpage(request, pk):
    lessonpage = get_object_or_404(LessonPage, pk=pk)
    request.session['previous_page'] = request.GET.get('next', 'teacherpage')


    if request.method == 'POST':
        lessonpage.delete()

        return redirect(request.session.get('previous_page', 'teacherpage'))

    return render(request, 'base/delete_confirm.html', {'object': lessonpage, 'type': 'LessonPage'})






@login_required
def delete_project(request, pk):
    project = get_object_or_404(UserProject, pk=pk, user=request.user)

    if request.method == 'POST':
        # Delete the project from the relational database
        project.delete()

        # Remove associated code from MongoDB using the project ID
        code_collection = get_code_collection()
        code_collection.delete_many({'lesson_id': pk})  # Assuming `lesson_id` is used to store the project ID in MongoDB

        messages.success(request, 'Project and associated code successfully deleted.')
        return redirect('dashboard')  # Redirect to wherever appropriate

    return render(request, 'base/delete_project_confirmation.html', {'project': project})




@login_required
def assignment_view(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if the user is a member of the classroom group associated with this assignment
    if not ClassroomMembership.objects.filter(user=request.user, classroom_group=assignment.classroom_group).exists():
        raise PermissionDenied("You do not have access to this assignment.")

    student_assignment, created = StudentAssignment.objects.get_or_create(
        student=request.user,
        assignment=assignment
    )
    student_progress, created = StudentProgress.objects.get_or_create(
        student=request.user,
        assignment=assignment
    )
    if student_progress:
            is_completed = student_progress.is_completed
    else:
            is_completed = False

    context = {
        'assignment': assignment,
        'student_assignment': student_assignment,
        'student_progress': student_progress,
        'is_completed': is_completed,
    }
    #print(assignment.lesson.id)
    return render(request, 'base/assignment_view.html', context)


@login_required
def mark_as_teacher(request):
    if not request.user.is_teacher:
        request.user.is_teacher = True
        request.user.save()
    return redirect(reverse('teacherpage'))


def loaderiotest(request):
    #user = User.objects.get(email='')
    #user.delete()

    return render(request, 'base/loaderio.html')


def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /admin/",
        "Disallow: /private/",
        "Allow: /static/",
        "Allow: /media/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")



def sitemap(request):
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
    
    """
    response = HttpResponse(sitemap_content, content_type='application/xml')
    return response


def privacypolicy(request):
    return render(request, 'base/privacypolicy.html')

def termsofuse(request):
    return render(request, 'base/termsofservice.html')

def donate(request):
    return render(request, 'base/donate.html')