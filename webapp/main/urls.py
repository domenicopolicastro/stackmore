
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('create-thread', views.create_thread, name='create_thread'),
    path('thread/<int:thread_id>/', views.thread_view, name='enter_thread'),
    path('thread/<int:thread_id>/subscribe/', views.subscribe_to_thread, name='subscribe_to_thread'),
    path('thread/<int:thread_id>/unsubscribe/', views.unsubscribe_from_thread, name='unsubscribe_from_thread'),
    path('thread/<int:thread_id>/create_post/', views.create_post, name='create_post'),
    path('post/<int:post_id>/vote/<str:value>/', views.vote_post, name='vote_post'),
    path('feed/', views.feed_view, name='feed'),
    path('friends/', views.friends_page, name='friends_page'),
    
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    
    path('profile/<str:username>/', views.profile, name='profile'),
    
    path('recommended/', views.recommended_content, name='recommended_content'),

    path('ban_user/<str:username>/', views.ban_user, name='ban_user'),
]