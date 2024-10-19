from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User, LessonPage, ClassroomGroup, ClassroomMembership, Assignment, ClassroomGroup, Course, Lesson, LessonPage, UserProject, ClassroomAnnouncement
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Course, Lesson, LessonPage
from turnstile.fields import TurnstileField
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class MyUserCreationForm(UserCreationForm):
    turnstile = TurnstileField()

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))
    turnstile = TurnstileField()

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise ValidationError("Invalid email or password.")
        return self.cleaned_data
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'bio', 'avatar']
        
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # Remove the password field from the form
        if 'password' in self.fields:
            del self.fields['password']

class UserPasswordChangeForm(PasswordChangeForm):
    pass

class UserEmailChangeForm(forms.Form):
    new_email = forms.EmailField(label="New Email Address")
    password = forms.CharField(widget=forms.PasswordInput(), label="Current Password")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserEmailChangeForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError("Incorrect password")
        return password

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            raise ValidationError("This email is already in use.")
        return new_email

class UserDeleteForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label="Enter your password to confirm")

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserDeleteForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError("Incorrect password")
        return password
    
class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants'] 

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar','name', 'username', 'email', 'bio']

class LessonPageForm(ModelForm):
    class Meta:
        model = LessonPage
        fields = ['title', 'content', 'google_slide_embed_url', 'python_compiler_embed_url', 'replit_embed_url', 'order']

class ClassroomForm(forms.ModelForm):
    turnstile = TurnstileField()

    class Meta:
        model = ClassroomGroup
        fields = ['name', 'description', 'banner']

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Add any custom save behavior here
        if commit:
            instance.save()
        return instance


class JoinClassroomForm(forms.Form):
    code = forms.CharField(max_length=8)
    turnstile = TurnstileField()

    def join_classroom(self, user):
        code = self.cleaned_data['code']
        try:
            classroom = ClassroomGroup.objects.get(code=code)
            
            # Check if user is already a member
            if ClassroomMembership.objects.filter(user=user, classroom_group=classroom).exists():
                raise forms.ValidationError("You are already a member of this classroom.")
            
            # Check if classroom has more than 50 students
            if ClassroomMembership.objects.filter(classroom_group=classroom).count() >= 60:
                raise forms.ValidationError("This classroom has reached its maximum capacity of 50 students.")
            
            ClassroomMembership.objects.create(user=user, classroom_group=classroom)
            return True
        except ClassroomGroup.DoesNotExist:
            self.add_error('code', 'Invalid classroom code.')
            return False
        except forms.ValidationError as e:
            self.add_error('code', str(e))
            return False


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(LessonForm, self).__init__(*args, **kwargs)

class CourseLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }  

# class LessonPageForm(forms.ModelForm):
#     class Meta:
#         model = LessonPage
#         fields = ['title', 'lesson', 'isContentPage', 'content', 'canvaEmbedUrl', 'google_slide_embed_url', 'python_compiler_embed_url', 'support_video_embed_url', 'tips', 'replit_embed_url', 'svg_file', 'order']

class ContentLessonPageForm(forms.ModelForm):
    class Meta:
        model = LessonPage
        fields = ['lesson', 'title', 'svg_file', 'order', 'isContentPage']
        widgets = {
            'order': forms.NumberInput(attrs={'placeholder': 'Leave blank for automatic ordering'}),
        }

    def __init__(self, *args, **kwargs):
        super(ContentLessonPageForm, self).__init__(*args, **kwargs)
        self.fields['isContentPage'].initial = True
        self.fields['lesson'] = forms.ModelChoiceField(
            queryset=Lesson.objects.all(),
            required=False,
            empty_label="-- Select a Lesson (Optional) --",
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
        self.fields['lesson'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return f"{obj.title} - Course: {obj.course.title if obj.course else 'N/A'}"
    
class NonContentLessonPageForm(forms.ModelForm):
    class Meta:
        model = LessonPage
        fields = ['lesson', 'title', 'content', 'order', 'isContentPage']
        widgets = {
            'order': forms.NumberInput(attrs={'placeholder': 'Leave blank for automatic ordering'}),
            "content": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}
              )
        }

    def __init__(self, *args, **kwargs):
        super(NonContentLessonPageForm, self).__init__(*args, **kwargs)
        self.fields['isContentPage'].initial = False
        self.fields['lesson'] = forms.ModelChoiceField(
            queryset=Lesson.objects.all(),
            required=False,
            empty_label="-- Select a Lesson (Optional) --",
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
        self.fields['lesson'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return f"{obj.title} - Course: {obj.course.title if obj.course else 'N/A'}"

class AssignmentForm(forms.ModelForm):
    turnstile = TurnstileField()

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'assignment_type', 'points_worth', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'] = forms.ModelChoiceField(
            queryset=Course.objects.all(),
            required=False
        )
        self.fields['lesson'] = forms.ModelChoiceField(
            queryset=Lesson.objects.all(),
            required=False
        )
        self.fields['lesson_page'] = forms.ModelChoiceField(
            queryset=LessonPage.objects.all(),
            required=False
        )

    def clean(self):
        cleaned_data = super().clean()
        assignment_type = cleaned_data.get('assignment_type')
        course = cleaned_data.get('course')
        lesson = cleaned_data.get('lesson')
        lesson_page = cleaned_data.get('lesson_page')

        if assignment_type == 'course' and not course:
            raise forms.ValidationError("Please select a course for course assignment.")
        elif assignment_type == 'lesson' and not lesson:
            raise forms.ValidationError("Please select a lesson for lesson assignment.")
        elif assignment_type == 'lesson_page' and not lesson_page:
            raise forms.ValidationError("Please select a lesson page for lesson page assignment.")

        return cleaned_data
    
class ProjectForm(forms.ModelForm):
    turnstile = TurnstileField()
    class Meta:
        model = UserProject
        fields = ['title', 'description']

class ClassroomAnnouncementForm(forms.ModelForm):
    class Meta:
        model = ClassroomAnnouncement
        fields = ['title', 'announcement_content']


class ClassroomGroupForm(forms.ModelForm):
    class Meta:
        model = ClassroomGroup
        fields = ['name', 'description', 'banner']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }



#----------------------------- New Forms -------------------------------- #


class EditContentLessonPageForm(forms.ModelForm):
    class Meta:
        model = LessonPage
        fields = ['title', 'svg_file']

class EditNonContentLessonPageForm(forms.ModelForm):
    class Meta:
        model = LessonPage
        fields = ['title', 'content']
        widgets = {
            "content": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}
              )
        }

class EditCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'image']

class EditLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title']
