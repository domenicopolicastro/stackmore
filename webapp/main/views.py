from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.decorators import login_required, permission_required
from .forms import RegisterForm, ThreadForm, PostForm, CommentForm
from django.contrib.auth.models import User, Group
from django.db.models import Count, Value, CharField, Q
from .models import Thread, Post, Vote, Follow
from django.urls import reverse
from .utility import calculate_user_similarities
import numpy as np

@login_required(login_url="/login")
def feed_view(request):
    # Recupera i thread a cui l'utente è iscritto
    subscribed_threads = request.user.subscribed_threads.all()
    # Recupera gli utenti che l'utente sta seguendo
    followed_users = request.user.following.all().values_list('following', flat=True)
    # Recupera i post dei thread a cui l'utente è iscritto
    posts_from_subscribed_threads = Post.objects.filter(
        thread__in=subscribed_threads
    ).annotate(source=Value('thread', CharField()))
    # Recupera i post degli utenti seguiti in tutti i thread
    posts_from_followed_users = Post.objects.filter(
        Q(author__in=followed_users) & ~Q(thread__in=subscribed_threads)
    ).annotate(source=Value('user', CharField()))
    # Unione dei due queryset
    posts = posts_from_subscribed_threads.union(posts_from_followed_users).order_by('-created_at')
    context = {
        'posts': posts,
    }
    return render(request, 'main/feed.html', context)


@login_required(login_url="/login")
def friends_page(request):
    users = User.objects.exclude(id=request.user.id).annotate(followers_count=Count('followers'))  # Annotazione corretta per il conteggio dei follower
    following = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)  # Ottieni gli ID degli utenti seguiti
    context = {
        'users': users,
        'following': following,
    }
    return render(request, 'main/friends.html', context)

@login_required(login_url="/login")
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    next_page = request.GET.get('next', 'profile')
    print(request.user)
    if next_page == 'profile':
        return redirect(reverse('profile', args=[username])) 
    elif next_page == 'friends':
        return redirect(reverse('friends_page'))
    return redirect(reverse('friends_page'))

@login_required(login_url="/login")
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    next_page = request.GET.get('next', 'profile')
    if next_page == 'profile':
        return redirect(reverse('profile', args=[username])) 
    elif next_page == 'friends':
        return redirect(reverse('friends_page'))
    return redirect(reverse('friends_page'))

@login_required(login_url="/login")
def thread_view(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    posts = Post.objects.filter(thread=thread).order_by('-total_votes')
    is_subscribed = request.user.is_authenticated and thread.subscribers.filter(id=request.user.id).exists()
    subscriber_count = thread.subscribers.count()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            post_id = request.POST.get('post_id')
            comment.post = Post.objects.get(id=post_id)
            comment.save()
            return redirect('enter_thread', thread_id=thread.id)
    else:
        comment_form = CommentForm()
    context = {
        'thread': thread,
        'posts': posts,
        'is_subscribed': is_subscribed,
        'subscriber_count': subscriber_count,
        'comment_form': comment_form,
    }
    return render(request, 'main/thread.html', context)

@login_required(login_url="/login")
@permission_required("main.add_post", login_url="/login", raise_exception=True)
def create_post(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.thread = thread
            post.save()
            return redirect('enter_thread', thread_id=thread.id)
    else:
        form = PostForm()
    return render(request, 'main/create_post.html', {'form': form, 'thread': thread})

@login_required(login_url="/login")
def subscribe_to_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    thread.subscribers.add(request.user)
    return redirect('enter_thread', thread_id=thread_id)

@login_required(login_url="/login")
def unsubscribe_from_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    thread.subscribers.remove(request.user)
    return redirect('enter_thread', thread_id=thread_id)

@login_required(login_url="/login")
def home(request):
    threads = Thread.objects.all()
    return render(request, 'main/home.html', {"threads": threads})


@login_required(login_url="/login")
@permission_required("main.add_thread", login_url="/login", raise_exception=True)
def create_thread(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.save()
            return redirect("/home")
    else:
        form = ThreadForm()

    return render(request, 'main/create_thread.html', {"form": form})

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})

@login_required(login_url="/login")
def vote_post(request, post_id, value):
    try:
        post = get_object_or_404(Post, id=post_id)
        value = int(value)
        vote, created = Vote.objects.get_or_create(user=request.user, post=post, defaults={'value': value})
        if not created and vote.value == value:
            vote.delete()
            post.total_votes -= value
        else:
            if not created:
                post.total_votes -= vote.value 
            vote.value = value
            vote.save()
            post.total_votes += value
        post.save()
        return redirect('enter_thread', thread_id=post.thread.id)
    except Exception as e:
        return redirect('enter_thread', thread_id=post.thread.id)

@login_required(login_url="/login")
def profile(request, username):
    # Recupera l'utente il cui profilo verrà visualizzato
    user = get_object_or_404(User, username=username)
    # Recupera i followers e following dell'utente
    followers = user.followers.all()
    following = user.following.all()
    # Recupera i thread creati dall'utente
    created_threads = Thread.objects.filter(author=user)
    # Recupera i thread seguiti dall'utente
    followed_threads = user.subscribed_threads.all()
    user_posts = Post.objects.filter(author=user)
    following_user = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    context = {
        'profile_user': user,
        'followers': followers,
        'following': following,
        'followed_threads': followed_threads,
        'created_threads': created_threads,
        'user_posts': user_posts,
        'following_user': following_user
        
    }
    return render(request, 'main/profile.html', context)

@login_required(login_url="/login")
def recommended_content(request):
    similarities, users = calculate_user_similarities()
    user_index = list(users).index(request.user)
    similar_users_indices = np.argsort(-similarities[user_index])[1:]  # Ordina per similarità decrescente, escludendo se stesso
    similar_users_indices = [int(idx) for idx in similar_users_indices]  # Converti indici int64 a int
    similar_users = [users[idx] for idx in similar_users_indices if similarities[user_index][idx] > 0]
    # Recupera i thread seguiti dagli utenti simili ma non dall'utente corrente
    recommended_threads = Thread.objects.filter(
        subscribers__in=similar_users
    ).exclude(
        subscribers=request.user
    ).distinct()
    # Recupera gli utenti seguiti dagli utenti simili ma non dall'utente corrente
    recommended_users = User.objects.filter(
        followers__follower__in=similar_users
    ).exclude(
        id=request.user.id
    ).distinct()

    return render(request, 'main/recommended_content.html', {'threads': recommended_threads, 'users': recommended_users})


@login_required
def ban_user(request, username):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, "Non sei autorizzato a effettuare questa azione.")
        return redirect('friends_page')  
    user_to_ban = get_object_or_404(User, username=username)
    group = Group.objects.get(name='default') 
    if user_to_ban in group.user_set.all():
        group.user_set.remove(user_to_ban)
        messages.success(request, f"L'utente {user_to_ban.username} è stato rimosso dal gruppo.")
    else:
        messages.info(request, f"L'utente {user_to_ban.username} non è nel gruppo.")

    return redirect('friends_page')