from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from courses.models import Course


@login_required
def course_chat_room(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # allow enrolled students, course instructors, and staff/superusers
    if not (request.user.courses_joined.filter(id=course_id).exists() or course.owner == request.user or request.user.is_staff):
        return HttpResponseForbidden()
    return render(request, 'chat/room.html', {'course': course})

