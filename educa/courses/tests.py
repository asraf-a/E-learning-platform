import json
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Subject, Course, Module, Content, Text, Video


class OrderFieldTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password')
        self.subject = Subject.objects.create(title='Math', slug='math')
        self.course1 = Course.objects.create(owner=self.user, subject=self.subject, title='Course 1', slug='c1')
        self.course2 = Course.objects.create(owner=self.user, subject=self.subject, title='Course 2', slug='c2')

    def test_module_ordering(self):
        m1 = Module.objects.create(course=self.course1, title='M1')
        self.assertEqual(m1.order, 0)

        m2 = Module.objects.create(course=self.course1, title='M2')
        self.assertEqual(m2.order, 1)

        # Explicit order override
        m3 = Module.objects.create(course=self.course1, title='M3', order=5)
        self.assertEqual(m3.order, 5)

        m4 = Module.objects.create(course=self.course1, title='M4')
        self.assertEqual(m4.order, 6)

        # Scoped to course: course2 first module gets order 0
        m5 = Module.objects.create(course=self.course2, title='M5')
        self.assertEqual(m5.order, 0)


class CourseCMSTestCase(TestCase):
    def setUp(self):
        # Create group and permissions
        self.group = Group.objects.create(name='Instructors')
        types = ContentType.objects.filter(app_label='courses').exclude(model='subject')
        perms = Permission.objects.filter(content_type__in=types)
        self.group.permissions.set(perms)

        # Instructor user
        self.instructor = User.objects.create_user(username='inst', password='password')
        self.instructor.groups.add(self.group)

        # Regular user
        self.student = User.objects.create_user(username='stud', password='password')

        self.subject = Subject.objects.create(title='Programming', slug='programming')
        self.course = Course.objects.create(
            owner=self.instructor,
            subject=self.subject,
            title='Python 101',
            slug='python-101',
            overview='Intro to python'
        )

        self.client = Client()

    def test_anonymous_access_redirects(self):
        response = self.client.get(reverse('manage_course_list'))
        self.assertEqual(response.status_code, 302)

    def test_regular_user_permission_denied(self):
        self.client.login(username='stud', password='password')
        response = self.client.get(reverse('manage_course_list'))
        self.assertEqual(response.status_code, 403)

    def test_instructor_can_list_and_create_courses(self):
        self.client.login(username='inst', password='password')
        response = self.client.get(reverse('manage_course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python 101')

        # Create new course
        response = self.client.post(reverse('course_create'), {
            'subject': self.subject.id,
            'title': 'Django Advanced',
            'slug': 'django-advanced',
            'overview': 'Building web apps'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(slug='django-advanced', owner=self.instructor).exists())

    def test_module_formset_management(self):
        self.client.login(username='inst', password='password')
        url = reverse('course_module_update', kwargs={'pk': self.course.id})
        
        data = {
            'modules-TOTAL_FORMS': '2',
            'modules-INITIAL_FORMS': '0',
            'modules-MIN_NUM_FORMS': '0',
            'modules-MAX_NUM_FORMS': '1000',
            'modules-0-title': 'Module A',
            'modules-0-description': 'Desc A',
            'modules-1-title': 'Module B',
            'modules-1-description': 'Desc B',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.course.modules.count(), 2)

    def test_content_create_and_delete(self):
        self.client.login(username='inst', password='password')
        module = Module.objects.create(course=self.course, title='Mod 1')
        
        # Create text content
        create_url = reverse('module_content_create', kwargs={'module_id': module.id, 'model_name': 'text'})
        response = self.client.post(create_url, {
            'title': 'First Text Content',
            'content': 'Hello world content'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(module.contents.count(), 1)
        content = module.contents.first()
        self.assertEqual(content.item.title, 'First Text Content')

        # Delete content
        delete_url = reverse('module_content_delete', kwargs={'id': content.id})
        del_resp = self.client.post(delete_url)
        self.assertEqual(del_resp.status_code, 302)
        self.assertEqual(module.contents.count(), 0)

    def test_ajax_module_and_content_reordering(self):
        self.client.login(username='inst', password='password')
        m1 = Module.objects.create(course=self.course, title='M1')
        m2 = Module.objects.create(course=self.course, title='M2')

        # Send reordered IDs
        order_data = {str(m1.id): 1, str(m2.id): 0}
        response = self.client.post(
            reverse('module_order'),
            data=json.dumps(order_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        m1.refresh_from_db()
        m2.refresh_from_db()
        self.assertEqual(m1.order, 1)
        self.assertEqual(m2.order, 0)


class PublicCourseViewsTestCase(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='teacher', password='password')
        self.subject_prog = Subject.objects.create(title='Programming', slug='programming')
        self.subject_math = Subject.objects.create(title='Mathematics', slug='math')
        self.course1 = Course.objects.create(
            owner=self.instructor,
            subject=self.subject_prog,
            title='Python Programming',
            slug='python-programming',
            overview='All about python'
        )
        self.course2 = Course.objects.create(
            owner=self.instructor,
            subject=self.subject_math,
            title='Linear Algebra',
            slug='linear-algebra',
            overview='All about matrices'
        )
        self.client = Client()

    def test_course_catalog_and_filtering(self):
        # All courses
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Programming')
        self.assertContains(response, 'Linear Algebra')

        # Filter by Programming
        response = self.client.get(reverse('course_list_subject', kwargs={'subject': 'programming'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Programming')
        self.assertNotContains(response, 'Linear Algebra')

    def test_course_detail_view(self):
        response = self.client.get(reverse('course_detail', kwargs={'slug': 'python-programming'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Programming')
        self.assertContains(response, 'Register to enroll')

    def test_content_polymorphic_rendering(self):
        # Text rendering
        text_item = Text.objects.create(owner=self.instructor, title='My Text', content='Line 1\nLine 2')
        rendered_text = text_item.render()
        self.assertIn('<p>Line 1<br>Line 2</p>', rendered_text)


import base64

class CoursesAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', password='password123')
        self.auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'student1:password123').decode('ascii')
        }
        self.subject = Subject.objects.create(title='Computer Science', slug='cs')
        self.course = Course.objects.create(
            owner=self.user,
            subject=self.subject,
            title='Data Structures & Algorithms',
            slug='dsa',
            overview='Algorithmic foundations'
        )
        self.module = Module.objects.create(course=self.course, title='Arrays and Linked Lists')
        self.text = Text.objects.create(owner=self.user, title='Array Basics', content='Arrays are contiguous blocks of memory.')
        self.content = Content.objects.create(module=self.module, item=self.text)
        self.client = Client()

    def test_subjects_api(self):
        response = self.client.get(reverse('api:subject_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(any(s['slug'] == 'cs' for s in data))

        detail_response = self.client.get(reverse('api:subject_detail', kwargs={'pk': self.subject.id}))
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()['title'], 'Computer Science')

    def test_courses_list_api(self):
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) >= 1)
        # Check nested modules
        course_data = next(c for c in data if c['slug'] == 'dsa')
        self.assertEqual(course_data['modules'][0]['title'], 'Arrays and Linked Lists')

    def test_course_enroll_and_contents_api(self):
        enroll_url = f'/api/courses/{self.course.id}/enroll/'
        contents_url = f'/api/courses/{self.course.id}/contents/'

        # 1. Unauthenticated enroll attempt -> 401
        response = self.client.post(enroll_url)
        self.assertEqual(response.status_code, 401)

        # 2. Access contents before enrolling -> 403 Forbidden
        response = self.client.get(contents_url, **self.auth_headers)
        self.assertEqual(response.status_code, 403)

        # 3. Authenticated enroll -> 200 OK
        response = self.client.post(enroll_url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'enrolled': True})
        self.assertTrue(self.course.students.filter(id=self.user.id).exists())

        # 4. Access contents after enrollment -> 200 OK with rendered content
        response = self.client.get(contents_url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        contents_data = response.json()
        self.assertEqual(contents_data['title'], 'Data Structures & Algorithms')
        module_contents = contents_data['modules'][0]['contents']
        self.assertTrue(len(module_contents) > 0)
        self.assertIn('Arrays are contiguous blocks of memory.', module_contents[0]['item'])


