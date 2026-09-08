from django.urls import reverse
from django.shortcuts import redirect
from .models import Course


def subdomain_course_middleware(get_response):
    """
    Subdomains for courses (Chapter 14)
    Allows courses to be accessed via subdomain:
    e.g. https://django.educaproject.com -> https://educaproject.com/course/django/
    """
    def middleware(request):
        host = request.get_host().split(':')[0]
        host_parts = host.split('.')

        # If hosted on onrender.com (e.g. educa-platform.onrender.com),
        # the base domain already has 3 parts: [<app_name>, 'onrender', 'com'].
        # A course subdomain would have > 3 parts (e.g. course.educa-platform.onrender.com).
        is_onrender = host.endswith('.onrender.com')
        min_parts = 3 if is_onrender else 2

        # Do not redirect admin or media/static requests
        if not request.path.startswith(('/admin/', '/static/', '/media/')):
            if len(host_parts) > min_parts and host_parts[0] != 'www':
                course = Course.objects.filter(slug=host_parts[0]).first()
                if course:
                    try:
                        course_url = reverse('course_detail', args=[course.slug])
                    except Exception:
                        course_url = f'/course/{course.slug}/'
                    domain = '.'.join(host_parts[1:])
                    url = f'{request.scheme}://{domain}{course_url}'
                    return redirect(url)

        response = get_response(request)
        return response

    return middleware
