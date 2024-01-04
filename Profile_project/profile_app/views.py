from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import CustomUser, Book, Cart, Address, Order, Wishlist, Review    
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AddressForm, OTPVerificationForm, ReviewForm, CustomPasswordResetForm, UserProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.db.models import Q, Avg, Count
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
import random

def home(request):
    books = Book.objects.all()[:5]
    return render(request, 'profile_app/index.html', {'books': books})

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Enable the user immediately without OTP verification
            user.save()
            # login(request, user)  # Automatically log in the user after registration
            # messages.success(request, 'Your account has been created.')

            # Generate and send OTP
            otp = generate_otp()  # Function to generate a 6-digit OTP
            send_otp_email(user.email, otp)  # Function to send OTP to the user's email

            # Store the OTP in the session for verification
            request.session['otp'] = otp

            return redirect('verify_otp')  # Redirect to the OTP verification page
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
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  # Redirect to the user profile page after saving the form
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'profile_app/user_profile.html', {'form': form})

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
    wishlist = Wishlist.objects.filter(user=request.user)

    return render(request, 'profile_app/book_list.html', {'books': books , 'wishlist': wishlist})

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

# @login_required
# def remove_from_cart(request, cart_item_id):
#     # print(type(cart_item_id))
#     cart_item = Book.objects.get(id = cart_item_id)
#     cart = Cart.objects.filter(user = request.user, book = cart_item)
#     # cart.first().delete()
    

#     if cart.quantity > 1:
#         # If the quantity is greater than 1, decrease it by 1
#         cart.quantity -= 1
#         cart.save()
#     elif cart_item.quantity == 1:
#         # If the quantity is 1, remove the item from the cart
#         cart_item.delete()
#     else:
#         # If the quantity is already less than 1, return a bad request response
#         return HttpResponseBadRequest("Invalid quantity in cart")

#     return redirect('view_cart')

@login_required
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = Book.objects.get(id=cart_item_id)  # Retrieve the book from the cart
        cart = Cart.objects.get(user=request.user, book=cart_item)  # Retrieve the cart item for the user and book
    except (Book.DoesNotExist, Cart.DoesNotExist) as e:
        # Handle the case where either the book or the cart item does not exist
        return HttpResponseBadRequest("Invalid book or cart item")

    if cart.quantity > 1:
        # If the quantity is greater than 1, decrease it by 1
        cart.quantity -= 1
        cart.save()
    else:
        # If the quantity is 1 or less, remove the item from the cart
        cart.delete()

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
            user_order_count = CustomUser.objects.filter(pk=request.user.pk).annotate(order_count=Count('order')).values_list('order_count', flat=True).first()
            if user_order_count is not None and user_order_count > 5:
                discount = 0.25  # 25% discount for users with more than 5 orders
            else:
                discount = 0.0  # No discount if the user has 5 or fewer orders
            cart_items = Cart.objects.filter(user=request.user)
            total = sum(item.book.price * item.quantity for item in cart_items)
            discounted_total = total - (total * discount)
            order = Order.objects.create(user=request.user, address=address, total=discounted_total)
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
    return render(request, 'profile_app/order_confirmation.html', {'order': order})

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = 'Your OTP for User Registration'
    message = f'Your OTP for user registration is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


def verify_otp(request):
    if request.method == 'POST':
        user_entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')

        if user_entered_otp == stored_otp:
            del request.session['otp']  # Remove the OTP from the session
            messages.success(request, 'OTP verification successful.')
            return redirect('login')  # Redirect to the login page after successful verification
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'profile_app/verify_otp.html')

@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'profile_app/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, book=book)
    if created:
        messages.success(request, f"{book.title} has been added to your wishlist.")
    else:
        messages.info(request, f"{book.title} is already in your wishlist.")
    return redirect('book_list')

@login_required
def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, pk=wishlist_item_id, user=request.user)
    book_title = wishlist_item.book.title
    wishlist_item.delete()
    messages.success(request, f"{book_title} has been removed from your wishlist.")
    return redirect('book_list')

@login_required
def add_review(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            comment = form.cleaned_data['comment']
            review, created = Review.objects.get_or_create(user=request.user, book=book, defaults={'rating': rating, 'comment': comment})
            if not created:
                review.rating = rating
                review.comment = comment
                review.save()
            messages.success(request, 'Your review has been saved.')
            return redirect('book_detail', book_id=book_id)
    else:
        form = ReviewForm()
    return render(request, 'profile_app/add_review.html', {'form': form, 'book': book})

def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = Review.objects.filter(book=book)
    user_has_purchased = True
    # Calculate average rating
    if reviews.exists():
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    else:
        average_rating = None
    return render(request, 'profile_app/book_detail.html', {'book': book, 'reviews': reviews, 'average_rating': average_rating, 'book': book, 'user_has_purchased': user_has_purchased})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'profile_app/password_reset.html'
    email_template_name = 'profile_app/password_reset_email.html'
    subject_template_name = 'profile_app/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    from_email = 'sandeshstone13@gmail.com'
    
    
@login_required
def subscribe_to_notifications(request):
    user = request.user
    if request.method == 'POST':
        subscribe = request.POST.get('subscribe')
        if subscribe:
            user.subscribe_to_notifications = True
        else:
            user.subscribe_to_notifications = False
        user.save()
    return redirect('user_profile')
    
