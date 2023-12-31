from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import Book, Cart, Address, Order
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AddressForm
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Exists, OuterRef
from django.http import HttpResponseBadRequest
from django.db.models import Q

def home(request):
    books = Book.objects.all()[:5]
    return render(request, 'profile_app/index.html', {'books': books})

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'profile_app/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('book_list')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'profile_app/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

def book_list(request):
    query = request.GET.get('q')
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    return render(request, 'profile_app/book_list.html', {'books': books, 'query': query})

@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    # Assuming the price is stored in the Book model
    price = book.price
    
    # Create a new Cart object with the specified price and total
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        book=book,
        defaults={'price': price, 'total': price}  # Set the default total to the price
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('view_cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, pk=cart_item_id, user=request.user)
    
    if cart_item.quantity > 1:
        # If the quantity is greater than 1, decrease it by 1
        cart_item.quantity -= 1
        cart_item.save()
    elif cart_item.quantity == 1:
        # If the quantity is 1, remove the item from the cart
        cart_item.delete()
    else:
        # If the quantity is already less than 1, return a bad request response
        return HttpResponseBadRequest("Invalid quantity in cart")

    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    return render(request, 'profile_app/cart.html', {'cart_items': cart_items})

@login_required
def checkout(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            cart_items = Cart.objects.filter(user=request.user)
            total = sum(item.book.price * item.quantity for item in cart_items)
            order = Order.objects.create(user=request.user, address=address, total=total)
            for item in cart_items:
                item.ordered = True
                item.save()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = AddressForm()
    return render(request, 'profile_app/checkout.html', {'form': form})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'profile_app/order_history.html', {'orders': orders})

def order_confirmation(request, order_id):
    order = Order.objects.get(pk=order_id)
    return render(request, 'profile_app/order_conformation.html', {'order': order})
