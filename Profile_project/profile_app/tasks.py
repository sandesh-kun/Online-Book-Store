from celery import shared_task
from django.core.mail import send_mail
from .models import Book, CustomUser
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg

@shared_task
def send_daily_highlighted_book_notification():
    # Get the date for yesterday
    yesterday = timezone.now() - timedelta(days=1)
    
    # Get books with the highest average rating added yesterday
    top_rated_books = (
        Book.objects
        .annotate(avg_rating=Avg('review__rating'))
        .filter(review__date_added__date=yesterday)
        .order_by('-avg_rating')[:1]
    )

    if top_rated_books:
        highlighted_book = top_rated_books[0]

        # Get a list of users who should receive notifications (assuming they have valid email addresses)
        users_to_notify = CustomUser.objects.filter(subscribe_to_notifications=True)

        # Send notifications to users
        for user in users_to_notify:
            subject = f'Check out our highlighted book of the day, {user.first_name}!'
            message = f'The highlighted book of the day based on user ratings is {highlighted_book.title}. Check it out on our website!'
            send_mail(subject, message, 'sandeshstone13@gmail.com', [user.email])
