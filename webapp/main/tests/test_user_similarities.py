from django.test import TestCase
from django.contrib.auth.models import User
from main.models import Thread
from main.utility import calculate_user_similarities
import numpy as np

class UserSimilaritiesTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        self.user3 = User.objects.create_user(username='user3', password='12345')
        self.user4 = User.objects.create_user(username='user4', password='12345')  # User with no subscriptions

        self.thread1 = Thread.objects.create(author=self.user1, title='Thread 1', description='Description for Thread 1')
        self.thread2 = Thread.objects.create(author=self.user2, title='Thread 2', description='Description for Thread 2')
        self.thread3 = Thread.objects.create(author=self.user3, title='Thread 3', description='Description for Thread 3')

        # Assign threads to users
        self.thread1.subscribers.add(self.user1, self.user2)
        self.thread2.subscribers.add(self.user1)
        self.thread3.subscribers.add(self.user2)

    def test_calculate_user_similarities(self):
        similarities, users = calculate_user_similarities()

        user1_index = list(users).index(self.user1)
        user2_index = list(users).index(self.user2)
        user3_index = list(users).index(self.user3)
        user4_index = list(users).index(self.user4)

        # Similarity between user1 and user2 (both subscribed to thread1)
        expected_similarity_user1_user2 = 1.0 / np.sqrt(2)  # they share 1 thread out of 2 for user1 and 2 out of 2 for user2
        self.assertAlmostEqual(similarities[user1_index][user2_index], expected_similarity_user1_user2, places=5)

        # Similarity between user1 and user3 (no common threads)
        self.assertEqual(similarities[user1_index][user3_index], 0.0)

        # Similarity between user2 and user3 (no common threads)
        self.assertEqual(similarities[user2_index][user3_index], 0.0)

        # Similarity between user1 and itself should be 0 as it's skipped
        self.assertEqual(similarities[user1_index][user1_index], 0.0)

        # Similarity between user4 (no subscriptions) and any user should be 0
        self.assertEqual(similarities[user1_index][user4_index], 0.0)
        self.assertEqual(similarities[user2_index][user4_index], 0.0)
        self.assertEqual(similarities[user3_index][user4_index], 0.0)

    def test_empty_user_thread_matrix(self):
        # Remove all threads
        Thread.objects.all().delete()

        similarities, users = calculate_user_similarities()

        expected_similarities = np.zeros((4, 4))  # Since we have 4 users but no threads

        np.testing.assert_array_equal(similarities, expected_similarities)
        self.assertEqual(len(users), 4)

    def test_single_user(self):
        # Remove all users except one
        User.objects.exclude(username='user1').delete()

        similarities, users = calculate_user_similarities()

        expected_similarities = np.zeros((1, 1))  # Only one user so the matrix is 1x1 with a 0

        np.testing.assert_array_equal(similarities, expected_similarities)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.user1)

    def test_no_users(self):
        # Remove all users
        User.objects.all().delete()

        similarities, users = calculate_user_similarities()

        expected_similarities = np.zeros((0, 0))  # No users so the matrix is 0x0

        np.testing.assert_array_equal(similarities, expected_similarities)
        self.assertEqual(len(users), 0)
