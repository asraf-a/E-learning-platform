from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from courses.models import Subject, Course, Module, Content, Text


class StudentAppTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.instructor = User.objects.create_user(username='prof', password='password123')
        self.subject = Subject.objects.create(title='Science', slug='science')
        self.course = Course.objects.create(
            owner=self.instructor,
            subject=self.subject,
            title='Astrophysics',
            slug='astrophysics',
            overview='Cosmos study'
        )
        self.module = Module.objects.create(course=self.course, title='Stars and Galaxies')
        self.text = Text.objects.create(owner=self.instructor, title='Intro to Stars', content='Stars are luminous spheres.')
        self.content = Content.objects.create(module=self.module, item=self.text)

        self.student = User.objects.create_user(username='alice', password='password123')
        self.client = Client()

    def tearDown(self):
        cache.clear()


    def test_student_registration(self):
        response = self.client.post(reverse('student_registration'), {
            'username': 'bob',
            'password1': 'StrongP@ss123!',
            'password2': 'StrongP@ss123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='bob').exists())

    def test_course_enrollment(self):
        self.client.login(username='alice', password='password123')
        
        # Enroll in course
        response = self.client.post(reverse('student_enroll_course'), {
            'course': self.course.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.course.students.filter(username='alice').exists())

        # View enrolled courses
        response = self.client.get(reverse('student_course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Astrophysics')

        # View course detail & module content
        detail_url = reverse('student_course_detail', kwargs={'pk': self.course.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stars and Galaxies')
        self.assertContains(response, 'Intro to Stars')
        self.assertContains(response, 'Stars are luminous spheres.')

    def test_non_enrolled_student_cannot_access_contents(self):
        self.client.login(username='alice', password='password123')
        detail_url = reverse('student_course_detail', kwargs={'pk': self.course.id})
        response = self.client.get(detail_url)
        # Should return 404 because alice is not enrolled
        self.assertEqual(response.status_code, 404)
