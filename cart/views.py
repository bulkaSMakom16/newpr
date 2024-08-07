from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import ProductForm
from .models import Cart, CartItem, Order, Product


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

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart:cart_detail')

@login_required
def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect(reverse('cart:cart_detail'))

@login_required
def update_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, cart__user=request.user, product_id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    return redirect(reverse('cart:cart_detail'))

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'orders': orders})
