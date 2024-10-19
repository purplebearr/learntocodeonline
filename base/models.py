from django.db import models
from django.contrib.auth.models import AbstractUser
from django.views.generic.detail import DetailView
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field

import os
import uuid
import string
import random


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique = True, null=True)
    bio = models.TextField(max_length=200, null=True)

    avatar = models.ImageField(null=False, default='avatar.svg')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    is_teacher = models.BooleanField(default=False)
    is_super_teacher = models.BooleanField(default=False)



    def save(self, *args, **kwargs):
        try:
            # Get the existing instance of the user
            existing_user = User.objects.get(id=self.id)

            # Check if the avatar has been updated
            if existing_user.avatar != self.avatar:
                # Delete the old avatar
                existing_user.avatar.delete(save=False)
        except User.DoesNotExist:
            pass

        super(User, self).save(*args, **kwargs)



class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True, max_length=200)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]

#----------------------------------------- Course Models ----------------------------------------------#

#class LessonContainer(models.Model):
#    title = models.CharField(max_length=200)
#    Lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='lesson_pages')


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(default="Default Description", max_length=400)
    image = models.ImageField(null=False, default='avatar.svg')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    is_private = models.BooleanField(default=True)
    category = models.TextField(default="default")
    is_trending = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_private = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)
    category = models.TextField(default="default")
    is_trending = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)



    #is_completed = models.BooleanField(default=False)

    def __str__(self):
        if self.course:
            return f"{self.title} - Course: {self.course.title}"
        return self.title

class LessonPage(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE,null=True, blank=True, related_name='lesson_pages')
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    canvaEmbedUrl = models.URLField(blank=True, null=True)

    isContentPage = models.BooleanField(default=False)
    content = CKEditor5Field()
    google_slide_embed_url = models.URLField(blank=True, null=True)
    python_compiler_embed_url = models.URLField(blank=True, null=True)
    support_video_embed_url = models.URLField(blank=True, null=True)
    replit_embed_url = models.URLField(blank=True, null=True)

    tips = models.TextField(default="Default lesson content")


    svg_file = models.FileField(null=True, blank=True, default=None)


    order = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    category = models.TextField(default="default")
    is_trending = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)



    def __str__(self):
        result = self.title
        if self.lesson:
            result += f" - Lesson: {self.lesson.title}"
            if self.lesson.course:
                result += f" - Course: {self.lesson.course.title}"
        return result

class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    entered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.course.title}"
        return f"Anonymous - {self.lesson_page.title}"

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    lesson_page = models.ForeignKey(LessonPage, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    entered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson_page')

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.lesson_page.title}"
        return f"Anonymous - {self.lesson_page.title}"

class UserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    entered_at = models.DateTimeField(auto_now_add=True)
    saved_compiler_code = models.TextField(null=True, blank=True)



    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.lesson.title}"
        return f"Anonymous - {self.lesson.title}"
    

class UserProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(null=True, blank=True, max_length=200)
    description = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

#------------------- Classroom Models---------------------------------------

def generate_unique_code():
    while True:
        unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not ClassroomGroup.objects.filter(code=unique_code).exists():
            return unique_code
        
class ClassroomGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_classroom_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(default=generate_unique_code, editable=False, unique=True, max_length=8)
    banner = models.ImageField(null=False, default='avatar.svg')


    def __str__(self):
        return f"{self.name}"



class ClassroomMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom_group = models.ForeignKey(ClassroomGroup, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'classroom_group')

class Assignment(models.Model):
    ASSIGNMENT_TYPES = (
        ('course', 'Course'),
        ('lesson', 'Lesson'),
        ('lesson_page', 'Lesson Page'),
    )
    
    classroom_group = models.ForeignKey(ClassroomGroup, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES)
    points_worth = models.IntegerField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    lesson_page = models.ForeignKey(LessonPage, on_delete=models.CASCADE, null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_assignment_type_display()}"
    
class StudentAssignment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_assignments')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='student_assignments')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'assignment')
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='student_progress')
    course_progress = models.ForeignKey('UserCourseProgress', on_delete=models.CASCADE, null=True, blank=True)
    lesson_progress = models.ForeignKey('UserLessonProgress', on_delete=models.CASCADE, null=True, blank=True)
    lesson_page_progress = models.ForeignKey('UserProgress', on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('student', 'assignment')
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} Progress"
    
class ClassroomAnnouncement(models.Model):
    title =  models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom_group = models.ForeignKey(ClassroomGroup, on_delete=models.CASCADE)
    posted_time = models.DateTimeField(auto_now_add=True)
    announcement_content = models.TextField(null=True)




#------------------------ Wagtail models-------------------------------------------------------#
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from wagtail.search import index
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


@register_snippet
class QuickLink(models.Model):
    title = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50, help_text="Font Awesome class without 'fa-' prefix. E.g., 'user' for 'fa-user'")
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('icon_class'),
        FieldPanel('link_page'),
    ]

    def __str__(self):
        return self.title
    
    @property
    def full_icon_class(self):
        return f"fas fa-{self.icon_class}"

    @property
    def url(self):
        return self.link_page.url if self.link_page else '#'

class HomePage(Page):
    hero_title = models.CharField(max_length=100)
    search_placeholder = models.CharField(max_length=100, default="Search for help...")
    people_searching_text = models.CharField(max_length=100, default="People are searching:")

    featured_section_1_title = models.CharField(max_length=100, default="Featured Section 1")
    featured_section_1_text = RichTextField(default="Text")
    featured_section_1_button_text = models.CharField(max_length=50, default="Learn More")

    featured_section_2_title = models.CharField(max_length=100, default="Featured Section 2")
    featured_section_2_text = RichTextField(default="Text")
    featured_section_2_button_text = models.CharField(max_length=50, default="Explore")

    content_panels = Page.content_panels + [
        FieldPanel('hero_title'),
        FieldPanel('search_placeholder'),
        FieldPanel('people_searching_text'),
        InlinePanel('search_terms', label="Search Terms"),
        InlinePanel('quick_links', label="Quick Links"),
        FieldPanel('featured_section_1_title'),
        FieldPanel('featured_section_1_text'),
        FieldPanel('featured_section_1_button_text'),
        FieldPanel('featured_section_2_title'),
        FieldPanel('featured_section_2_text'),
        FieldPanel('featured_section_2_button_text'),
    ]


class SearchTerm(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='search_terms')
    term = models.CharField(max_length=100)
    url = models.URLField()

    panels = [
        FieldPanel('term'),
        FieldPanel('url'),
    ]

class HomePageQuickLink(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='quick_links')
    quick_link = models.ForeignKey(QuickLink, on_delete=models.CASCADE, related_name='+')

    panels = [
        FieldPanel('quick_link'),
    ]


class CodeBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(choices=[
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('html', 'HTML'),
        ('css', 'CSS'),
    ], default='python')
    code = blocks.TextBlock()

    class Meta:
        template = 'blocks/code_block.html'
        icon = 'code'

class TutorialHomePage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['tutorials'] = TutorialPage.objects.live().order_by('title')
        return context

    class Meta:
        verbose_name = "Tutorial Homepage"

class TutorialPage(Page):
    introduction = RichTextField(blank=True)
    
    content = StreamField([
        ('text', blocks.RichTextBlock()),
        ('code', CodeBlock()),
        ('image', ImageChooserBlock()),
    ], use_json_field=True, blank=True)  # Note the added 'blank=True'

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('content'),
    ]

class CodeSnippetPage(Page):
    description = RichTextField(blank=True)
    code_snippet = models.TextField()
    language = models.CharField(max_length=50)

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('code_snippet'),
        FieldPanel('language'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.SearchField('code_snippet'),
    ]

class CodeSnippetHomePage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['snippet_pages'] = CodeSnippetPage.objects.live().order_by('title')
        return context
    
class FAQItem(blocks.StructBlock):
    question = blocks.CharBlock(required=True, help_text="Add the question here")
    answer = blocks.RichTextBlock(required=True, help_text="Add the answer here")

    class Meta:
        template = 'blocks/faq_item.html'
        icon = 'help'

class FAQPage(Page):
    intro = RichTextField(blank=True, help_text="Optional introduction text for the FAQ page")
    
    faqs = StreamField([
        ('faq_item', FAQItem()),
    ], use_json_field=True, min_num=1, help_text="Add FAQ items")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('faqs'),
    ]

    class Meta:
        verbose_name = "FAQ Page"


#----------- Deprecated models------------------#
class ClassroomLesson(models.Model):
    title = models.CharField(max_length=200)
    classroom_group = models.ForeignKey(ClassroomGroup, on_delete=models.CASCADE, related_name='lessons', null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_classroom_lessons', null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    randomfield = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class ClassroomLessonPage(models.Model):
    lesson = models.ForeignKey(ClassroomLesson, on_delete=models.CASCADE, related_name='lesson_pages')
    title = models.CharField(max_length=200)
    content = models.TextField(default="Default lesson content")
    google_slide_embed_url = models.URLField(blank=True, null=True)
    python_compiler_embed_url = models.URLField(blank=True, null=True)
    support_video_embed_url = models.URLField(blank=True, null=True)
    tips = models.TextField(default="Default lesson content")
    replit_embed_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class ClassroomUserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    lesson_page = models.ForeignKey(ClassroomLessonPage, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    entered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson_page')

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.lesson_page.title}"
        return f"Anonymous - {self.lesson_page.title}"

class ClassroomUserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(ClassroomLesson, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    entered_at = models.DateTimeField(auto_now_add=True)
    saved_compiler_code = models.TextField(default="", null=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.lesson.title}"
        return f"Anonymous - {self.lesson.title}"
    


