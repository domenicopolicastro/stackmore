import numpy as np
from django.contrib.auth.models import User
from .models import Thread

def get_user_thread_matrix():
    users = User.objects.all()
    threads = Thread.objects.all()
    user_thread_matrix = np.zeros((users.count(), threads.count()))

    for i, user in enumerate(users):
        for j, thread in enumerate(threads):
            if thread.subscribers.filter(id=user.id).exists():
                user_thread_matrix[i][j] = 1
    
    return user_thread_matrix, users, threads

def cosine_similarity_manual(A, B):
    dot_product = np.dot(A, B)
    norm_a = np.linalg.norm(A)
    norm_b = np.linalg.norm(B)
    if norm_a == 0 or norm_b == 0:  # handle the case where one of the vectors is zero
        return 0.0
    return dot_product / (norm_a * norm_b)

def calculate_user_similarities():
    user_thread_matrix, users, _ = get_user_thread_matrix()
    num_users = user_thread_matrix.shape[0]
    similarities = np.zeros((num_users, num_users))
    
    for i in range(num_users):
        for j in range(num_users):
            if i != j:  # don't calculate similarity with itself
                similarities[i][j] = cosine_similarity_manual(user_thread_matrix[i], user_thread_matrix[j])
    
    return similarities, users
