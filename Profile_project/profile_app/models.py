from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count

class CustomUser(AbstractUser):
    is_regular_user = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Specify unique related_name attributes for groups and user_permissions
        permissions = [
            ('can_view_customuser', 'Can view custom users'),
        ]
        
    def get_order_count(self):
        return Order.objects.filter(user=self).count()
    subscribe_to_notifications = models.BooleanField(default=False)

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    price = models.IntegerField()
    desc = models.TextField()
    image = models.ImageField(upload_to="books/images", default="")
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True)

    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    total = models.IntegerField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.IntegerField()

    def __str__(self):
        return self.user.username

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    total = models.IntegerField()
    status = models.CharField(max_length=100, default="pending")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"
    
class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'book'] 
