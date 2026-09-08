import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educa.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from courses.models import Subject, Course, Module, Content, Text, Video

def setup():
    # 1. Create Instructors Group
    instructors_group, created = Group.objects.get_or_create(name='Instructors')
    
    # Add all permissions of the courses application, except Subject
    course_content_types = ContentType.objects.filter(app_label='courses').exclude(model='subject')
    permissions = Permission.objects.filter(content_type__in=course_content_types)
    instructors_group.permissions.set(permissions)
    print(f"Set {permissions.count()} permissions for 'Instructors' group.")

    # 2. Create Superuser 'admin'
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created superuser 'admin' / 'admin123'.")
    else:
        print("Superuser 'admin' already exists.")

    # 3. Create Instructor 'instructor'
    instructor, created = User.objects.get_or_create(
        username='instructor',
        defaults={'email': 'instructor@example.com', 'first_name': 'Jane', 'last_name': 'Doe'}
    )
    if created:
        instructor.set_password('password123')
        instructor.save()
        print("Created instructor user 'instructor' / 'password123'.")
    instructor.groups.add(instructors_group)
    print("Added 'instructor' to 'Instructors' group.")

    # 4. Create sample Course, Modules, and Contents
    prog_subject = Subject.objects.filter(slug='programming').first()
    if not prog_subject:
        prog_subject = Subject.objects.create(title='Programming', slug='programming')

    course, created = Course.objects.get_or_create(
        owner=instructor,
        slug='python-for-beginners',
        defaults={
            'subject': prog_subject,
            'title': 'Python for Beginners',
            'overview': 'Learn Python programming from scratch with hands-on examples and projects.'
        }
    )
    if created:
        print(f"Created sample course '{course.title}'.")
        # Modules
        m1 = Module.objects.create(course=course, title='Introduction to Python', description='Basics and setup')
        m2 = Module.objects.create(course=course, title='Data Structures', description='Lists, Tuples, Dictionaries')
        m3 = Module.objects.create(course=course, title='Functions and Modules', description='Writing reusable code')
        
        # Contents for Module 1
        t1 = Text.objects.create(owner=instructor, title='Welcome to Python', content='Python is a high-level, interpreted programming language.')
        Content.objects.create(module=m1, item=t1)

        v1 = Video.objects.create(owner=instructor, title='Python Installation Guide', url='https://www.youtube.com/watch?v=kqtD5dpn9C8')
        Content.objects.create(module=m1, item=v1)

        t2 = Text.objects.create(owner=instructor, title='Variables and Data Types', content='In Python, you do not need to declare variable types explicitly.')
        Content.objects.create(module=m1, item=t2)
        print("Created sample modules and content.")

    # 5. Create sample Student 'student'
    student, created = User.objects.get_or_create(
        username='student',
        defaults={'email': 'student@example.com', 'first_name': 'John', 'last_name': 'Smith'}
    )
    if created:
        student.set_password('password123')
        student.save()
        print("Created student user 'student' / 'password123'.")
    course.students.add(student)
    print("Enrolled 'student' in 'Python for Beginners'.")

if __name__ == '__main__':
    setup()

