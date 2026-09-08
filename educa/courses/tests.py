import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Course, Module, Subject, Content, Text

class CourseFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser', password='password123')
        self.subject = Subject.objects.create(title='Test Subject', slug='test-subject')
        self.client = Client()
        self.client.login(username='testuser', password='password123')

    def test_root_redirect(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('manage_course_list'), response.url)

    def test_course_crud_and_buttons(self):
        # Create course
        create_resp = self.client.post(reverse('course_create'), {
            'subject': self.subject.id,
            'title': 'Django Testing Course',
            'slug': 'django-testing-course',
            'overview': 'Overview'
        }, follow=True)
        self.assertEqual(create_resp.status_code, 200)
        course = Course.objects.get(slug='django-testing-course')

        # Edit course
        edit_resp = self.client.post(reverse('course_edit', args=[course.id]), {
            'subject': self.subject.id,
            'title': 'Django Testing Course Updated',
            'slug': 'django-testing-course',
            'overview': 'Updated Overview'
        }, follow=True)
        self.assertEqual(edit_resp.status_code, 200)
        course.refresh_from_db()
        self.assertEqual(course.title, 'Django Testing Course Updated')

        # Update modules
        mod_resp = self.client.post(reverse('course_module_update', args=[course.id]), {
            'modules-TOTAL_FORMS': '1',
            'modules-INITIAL_FORMS': '0',
            'modules-MIN_NUM_FORMS': '0',
            'modules-MAX_NUM_FORMS': '1000',
            'modules-0-title': 'Module One',
            'modules-0-description': 'Module One Description',
        }, follow=True)
        self.assertEqual(mod_resp.status_code, 200)
        module = course.modules.first()
        self.assertIsNotNone(module)

        # Create content
        content_resp = self.client.post(
            reverse('module_content_create', args=[module.id, 'text']),
            {'title': 'Text Content', 'content': 'Sample content text'},
            follow=True
        )
        self.assertEqual(content_resp.status_code, 200)
        content = module.contents.first()
        self.assertIsNotNone(content)

        # Delete content
        del_content_resp = self.client.post(reverse('module_content_delete', args=[content.id]), follow=True)
        self.assertEqual(del_content_resp.status_code, 200)
        self.assertEqual(module.contents.count(), 0)

        # Delete course
        del_course_resp = self.client.post(reverse('course_delete', args=[course.id]), follow=True)
        self.assertEqual(del_course_resp.status_code, 200)
        self.assertFalse(Course.objects.filter(id=course.id).exists())
