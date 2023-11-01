# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from posts.models import Post


@login_required
def post_create(request):
    if request.method == "POST":
        text = request.POST["text"]
        Post.objects.create(text=text)
        return redirect(reverse('posts:create'))
    else:
        return render(request, 'posts/create.html')