# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, blank=True, null=True)  

    def __str__(self):
        return self.user.username

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"

class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Resolved', 'Resolved')
        ],
        default='Pending'
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

class Event(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return self.title   
    
class EventPayment(models.Model):
    STATUS_CHOICES = (
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"  # <-- name -> title
    
class Maintenance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=50)
    amount = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')],
        default='Unpaid'
    )

    def __str__(self):
        return f"{self.user.username} - {self.month}"
    
class Flat(models.Model):
    flat_no = models.CharField(max_length=10)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.flat_no

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Track if admin has read it

    def __str__(self):
        return f"{self.name} - {self.email}"
