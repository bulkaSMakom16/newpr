from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.urls import reverse

from cart.forms import OrderCreateForm, PaymentForm

from .models import Post, Category, Comment, PostPhoto, SubscribedUsers, UserProfile
from cart.models import Cart, CartItem, Order, OrderItem, Product
from .forms import MultiplePhotoForm, PostForm, CommentForm, PostPhotoForm, SubscriptionForm, UserProfileForm, CustomUserCreationForm, ProductForm
from django.db.models import Q

from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
# Create your views here.

@login_required
def order_create(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )
            cart.items.all().delete()  # Очищаем корзину после создания заказа
            return redirect('order_detail', order_id=order.id)  # Здесь должно быть имя маршрута
    else:
        form = OrderCreateForm()

    # Вычисляем общую стоимость
    total_cost = sum(item.get_total_price() for item in cart.items.all())

    return render(request, 'blog/order_create.html', {'form': form, 'cart': cart, 'total_cost': total_cost})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'blog/order_detail.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'blog/order_history.html', {'orders': orders})

@login_required
def pay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            order.paid = True
            order.save()
            return redirect('order_detail', order_id=order.id)
    else:
        form = PaymentForm()
    return render(request, 'blog/pay_order.html', {'form': form, 'order': order})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect(reverse('cart:cart_detail'))

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'blog/add_product.html', {'form': form})

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'blog/product_list.html', {'products': products})

def blog_logout(request):
    if request.method == 'POST':
        return redirect('index')
    return render(request, 'registration/logged_out.html')

def blog_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'registration/login.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'blog/registration_user.html', {'form': form})

@login_required
def update_profile(request):
    user = request.user
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
        
    return render(request, 'blog/update_profile.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    
    try:
        user_profile = UserProfile.objects.get(user=user)
        avatar_url = user_profile.avatar.url if user_profile.avatar else 'http://placehold.it/64x64'
    except UserProfile.DoesNotExist:
        avatar_url = 'http://placehold.it/64x64'

    context = {
        'user': user,
        'avatar_url': avatar_url
    }
    return render(request, 'blog/profile.html', context)

def send_post_creation_email(post):
    subject = f'Новый пост создан: {post.title}'
    message = f'Здравствуйте!\n\nНовый пост был создан на вашем блоге.\n\nЗаголовок: {post.title}\nСодержание: {post.content}\n\nС уважением,\nВаша команда'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [settings.DEFAULT_FROM_EMAIL]

    send_mail(subject, message, email_from, recipient_list)

def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not SubscribedUsers.objects.filter(email=email).exists():
                form.save()
                messages.success(request, f"{email} has been successfully registered.")
                return redirect('index') 
            else:
                messages.error(request, 'This email is already subscribed.')
    else:
        form = SubscriptionForm()
    context = {'form': form}
    context.update(getCategories())
    return render(request, 'blog/subscribe.html', context)

def create(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        photo_form = MultiplePhotoForm(request.POST, request.FILES)

        if post_form.is_valid():
            try:
                post = post_form.save(commit=False)
                post.user = request.user
                post.save()

                # Save multiple photos
                images = request.FILES.getlist('images')
                for image in images:
                    PostPhoto.objects.create(post=post, image=image)

                # Send email notifications to subscribers
                send_mail(
                    'New Post Published',
                    f'A new post titled "{post.title}" has been published on our blog.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email for user in SubscribedUsers.objects.all()],
                    fail_silently=False,
                )

                messages.success(request, 'Post created successfully with photos and notification sent!')
                return redirect('index')
            except IntegrityError:
                messages.error(request, 'A post with this title already exists.')
        else:
            messages.error(request, 'There was an error with your submission.')
    else:
        post_form = PostForm()
        photo_form = MultiplePhotoForm()

    context = {'post_form': post_form, 'photo_form': photo_form}
    context.update(getCategories())
    return render(request, 'blog/create.html', context)

def search(request):
    query = request.GET.get('query')
    posts = Post.objects.filter(Q(content__icontains=query)| Q(title__icontains=query))
    context = {'posts':posts}
    context.update(getCategories())
    return render(request, 'blog/index.html', context)

def category(request, c=None):
    cObj = get_object_or_404(Category, name=c)
    posts = Post.objects.filter(category=cObj).order_by("-publishedDate")
    context = {'posts':posts}
    context.update(getCategories())
    return render(request, 'blog/index.html', context)

def getCategories():
    all = Category.objects.all()
    count = all.count()
    half = count // 2
    firstHalf = all[:half]
    secondHalf = all[half:]
    return{'cats1':firstHalf, 'cats2':secondHalf}


def index(request):
    posts = Post.objects.all().order_by('-publishedDate')
    context = {'posts':posts}
    context.update(getCategories())
    return render(request, 'blog/index.html', context)

def post(request, name=None):
    posts = Post.objects.filter(title=name)
    if not posts.exists():
        raise Http404("Post does not exist")
    post = posts.first()
    post = get_object_or_404(Post, title=name)
    comments = Comment.objects.filter(post=post).order_by('-id')

    # Get user profiles and their avatars
    comments_with_avatars = []
    for comment in comments:
        try:
            user_profile = UserProfile.objects.get(user=comment.author)
            avatar_url = user_profile.avatar.url if user_profile.avatar else 'http://placehold.it/64x64'
        except UserProfile.DoesNotExist:
            avatar_url = 'http://placehold.it/64x64'
        
        comments_with_avatars.append((comment, avatar_url))

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            content = request.POST.get('content')
            comment = Comment.objects.create(post=post, content=content, author=request.user)
            comment.save()
            return redirect('post', name=name)
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments_with_avatars': comments_with_avatars,
        'comment_form': comment_form
    }
    context.update(getCategories())
    return render(request, 'blog/post.html', context)

def contact(request):
    return render(request, 'blog/contact.html')

def about(request):
    return render(request, 'blog/about.html')

def services(request):
    return render(request, 'blog/services.html')