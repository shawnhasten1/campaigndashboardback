from django.db import models
import uuid

# Create your models here.
class Organization(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    cover_photo = models.ImageField(upload_to='organization/cover_photos', blank=True, null=True)

    address_line_1 = models.CharField(max_length=50, blank=True, null=True)
    address_line_2 = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    post_code = models.CharField(max_length=6, blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name_first = models.CharField(max_length=50)
    name_last = models.CharField(max_length=50)

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=200)

    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

class Campaign(models.Model):
    LIVE = 1
    STOPPED = 2
    PAUSED = 3
    ARCHIVED = 4

    STATUS_CHOICE = (
        (LIVE, 'Live'),
        (STOPPED, 'Stopped'),
        (PAUSED, 'Paused'),
        (ARCHIVED, 'Archived'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICE, blank=True, null=True)
    
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE)
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    unique_id = models.CharField(max_length=50, default=uuid.uuid4, unique=True)
    name_first = models.CharField(max_length=50)
    name_last = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12, blank=True)

    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)

class Journey(models.Model):
    id = models.AutoField(primary_key=True)

    campaign_id = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    contact_id = models.ForeignKey(Contact, on_delete=models.CASCADE)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)