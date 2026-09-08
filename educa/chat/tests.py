from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from channels.testing import WebsocketCommunicator
from courses.models import Subject, Course
from educa.asgi import application


class ChatViewsTestCase(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='prof_chat', password='password123')
        self.student = User.objects.create_user(username='alice_chat', password='password123')
        self.other_user = User.objects.create_user(username='stranger_chat', password='password123')

        self.subject = Subject.objects.create(title='Language', slug='lang')
        self.course = Course.objects.create(
            owner=self.instructor,
            subject=self.subject,
            title='English Literature',
            slug='eng-lit',
            overview='Classic literature'
        )
        self.course.students.add(self.student)
        self.client = Client()

    def test_anonymous_access_redirects(self):
        response = self.client.get(reverse('chat:course_chat_room', kwargs={'course_id': self.course.id}))
        self.assertEqual(response.status_code, 302)

    def test_non_enrolled_user_forbidden(self):
        self.client.login(username='stranger_chat', password='password123')
        response = self.client.get(reverse('chat:course_chat_room', kwargs={'course_id': self.course.id}))
        self.assertEqual(response.status_code, 403)

    def test_enrolled_student_access(self):
        self.client.login(username='alice_chat', password='password123')
        response = self.client.get(reverse('chat:course_chat_room', kwargs={'course_id': self.course.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chat room for "English Literature"')
        self.assertContains(response, 'chat-message-input')


class ChatWebSocketTestCase(TestCase):
    async def test_websocket_chat_consumer(self):
        student = await User.objects.acreate(username='ws_student', password='password123')
        subject = await Subject.objects.acreate(title='Math', slug='math_ws')
        course = await Course.objects.acreate(
            owner=student,
            subject=subject,
            title='Calculus',
            slug='calc',
            overview='Limits and derivatives'
        )

        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/room/{course.id}/'
        )
        communicator.scope['user'] = student

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Send a message
        await communicator.send_json_to({'message': 'Hello from async WebSocket!'})

        # Receive the broadcast message
        response = await communicator.receive_json_from()
        self.assertEqual(response['message'], 'Hello from async WebSocket!')
        self.assertEqual(response['user'], 'ws_student')
        self.assertIn('datetime', response)

        # Close
        await communicator.disconnect()
