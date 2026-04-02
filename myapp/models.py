from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    USER = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=250)
    place = models.CharField(max_length=250)  # HTML uses 'city', we map it here
    user_type_interest = models.CharField(max_length=250) # HTML uses 'user_type'


# Used for Admin management (admin.html: "Manage Category")
class Category(models.Model):
    category_name = models.CharField(max_length=250)


class Shop(models.Model):
    USER = models.OneToOneField(User, on_delete=models.CASCADE)
    CATEGORY = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    # Basic Info
    shop_name = models.CharField(max_length=250)
    owner_name = models.CharField(max_length=250)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=250)
    place = models.CharField(max_length=250)

    # Capabilities
    shop_type = models.CharField(max_length=250, default="General")
    equipment = models.CharField(max_length=250)
    materials = models.CharField(max_length=250)
    turnaround_time = models.CharField(max_length=250) # HTML input is 'turnaround'

    # Verification
    proof_type = models.CharField(max_length=250)
    proof_file = models.FileField(upload_to='shop_proofs/')

    # Status (Default 'pending' for Admin approval workflow in admin.html)
    status = models.CharField(max_length=250, default='pending')

class Request(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Paid', 'Paid'),
        ('Printing', 'Printing'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
    ]

    USER = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    SHOP = models.ForeignKey(Shop, on_delete=models.CASCADE)

    model_file = models.FileField(upload_to='request_files/')
    description = models.TextField() # Used for 'Request Type' or notes
    delivery_address = models.TextField(help_text="Visible to Shop only for delivery")
    status = models.CharField(max_length=250, choices=STATUS_CHOICES, default='Pending')
    amount = models.CharField(max_length=250, default="0.00")
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    REQUEST = models.ForeignKey(Request, on_delete=models.CASCADE)
    amount = models.CharField(max_length=250)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=250, default='Success')

class Complaint(models.Model):
    USER = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    SHOP = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    reply = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=250, default='Pending')
    date = models.DateTimeField(auto_now_add=True)
    TYPE_CHOICES = [('Platform', 'Platform'), ('Shop', 'Shop')]
    complaint_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Platform')

class Feedback(models.Model):
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    SHOP = models.ForeignKey(Shop, on_delete=models.CASCADE,null=True, blank=True)
    description = models.TextField()
    rating = models.CharField(max_length=250, default="5")
    date = models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    REQUEST = models.ForeignKey(Request, on_delete=models.CASCADE)
    rating = models.CharField(max_length=50)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

