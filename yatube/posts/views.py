from core.utils import page
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = page(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_posts.all()
    page_obj = page(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = author.user_posts.all()
    page_obj = page(request, post_list)
    if request.user.is_authenticated:
        if request.user.follower.filter(author=author).exists():
            following = True
        else:
            following = False
        context = {
            'username': author,
            'page_obj': page_obj,
            'following': following,
        }
        return render(request, 'posts/profile.html', context)
    context = {
        'username': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            post_new = form.save(commit=False)
            post_new.author = request.user
            post_new.save()
            return redirect('posts:profile', username=request.user.username)
        return render(request, template, {'form': form})
    return render(request, template, {'form': PostForm()})


def post_edit(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    if request.user == post.author:
        is_edit = 1
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if request.method != 'POST':
            return render(request, 'posts/create_post.html', {
                'form': form,
                'is_edit': is_edit,
                'post_id': post_id,
            })
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        return render(request, template, {
            'post': post,
            'is_edit': is_edit,
        })
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    if request.user.follower.all().exists():
        post_list = Post.objects.filter(author__following__user=request.user)
        page_obj = page(request, post_list)
        context = {
            'page_obj': page_obj,
        }
    else:
        context = {
            'page_obj': [],
        }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    follower_author = request.user.follower.filter(author=author).exists()
    if author != request.user and not follower_author:
        follow = Follow(user=request.user, author=author)
        follow.save()
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
