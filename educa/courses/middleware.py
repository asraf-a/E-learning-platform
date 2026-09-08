from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from .models import Course


def subdomain_course_middleware(get_response):
    """
    Subdomains for courses (Chapter 14)
    Allows courses to be accessed via subdomain:
    e.g. https://django.educaproject.com -> https://educaproject.com/course/django/
    """
    def middleware(request):
        # Extract host and check for subdomain
        host = request.get_host().split(':')[0]
        host_parts = host.split('.')
        if len(host_parts) > 2 and host_parts[0] != 'www':
            # get course for the given subdomain
            course = get_object_or_404(Course, slug=host_parts[0])
            try:
                course_url = reverse('course_detail', args=[course.slug])
            except Exception:
                # Fallback to course URL pattern if course_detail is not defined yet
                course_url = f'/course/{course.slug}/'
            # redirect current request to the course view
            domain = '.'.join(host_parts[1:])
            url = f'{request.scheme}://{domain}{course_url}'
            return redirect(url)

        response = get_response(request)
        return response

    return middleware
