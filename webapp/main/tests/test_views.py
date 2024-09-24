from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from main.models import Thread, Post
from main.forms import PostForm
from django.shortcuts import get_object_or_404

class CreatePostViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        
        content_type = ContentType.objects.get_for_model(Post)
        permission = Permission.objects.get(codename='add_post', content_type=content_type)
        self.user1.user_permissions.add(permission)

        self.thread = Thread.objects.create(author=self.user1, title='Test Thread', description='Test Description')

    def test_create_post_view_access_denied_for_unauthenticated_users(self):
        response = self.client.get(reverse('create_post', kwargs={'thread_id': self.thread.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/login/?next=/create_post/{self.thread.id}/', fetch_redirect_response=False)

    def test_create_post_view_access_denied_for_users_without_permission(self):
        self.client.login(username='user2', password='12345')
        response = self.client.get(reverse('create_post', kwargs={'thread_id': self.thread.id}))
        self.assertEqual(response.status_code, 403)

    def test_create_post_view_access_granted_for_users_with_permission_get(self):
        self.client.login(username='user1', password='12345')
        response = self.client.get(reverse('create_post', kwargs={'thread_id': self.thread.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/create_post.html')
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertEqual(response.context['thread'], self.thread)

    def test_create_post_view_access_granted_for_users_with_permission_post_valid(self):
        self.client.login(username='user1', password='12345')
        form_data = {
            'title': 'Test Post',
            'description': 'Test Post Description'
        }
        response = self.client.post(reverse('create_post', kwargs={'thread_id': self.thread.id}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='Test Post').exists())

    def test_create_post_view_access_granted_for_users_with_permission_post_invalid(self):
        self.client.login(username='user1', password='12345')
        form_data = {
            'title': '',  # Title is required, so this is invalid
            'description': 'Test Post Description'
        }
        response = self.client.post(reverse('create_post', kwargs={'thread_id': self.thread.id}), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/create_post.html')
        self.assertFalse(Post.objects.filter(description='Test Post Description').exists())
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertTrue(response.context['form'].errors)
