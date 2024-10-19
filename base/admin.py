from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Lesson)
admin.site.register(LessonPage)
admin.site.register(ClassroomGroup)
admin.site.register(ClassroomMembership)
admin.site.register(UserLessonProgress)
admin.site.register(UserProgress)
admin.site.register(Course)
admin.site.register(UserCourseProgress)
admin.site.register(Assignment)
admin.site.register(StudentProgress)
admin.site.register(StudentAssignment)
admin.site.register(UserProject)
admin.site.register(ClassroomAnnouncement)