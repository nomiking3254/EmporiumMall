from django.db import models
from django.contrib.auth.models import AbstractUser
from auths.manager import UserManager
import uuid
from django.core.files.uploadedfile import InMemoryUploadedFile
from auths.image_processing import generate_thumbnail
import sys

class User(AbstractUser):
    
    class Meta:
        db_table = 'User'
        verbose_name_plural = 'Users'
        managed = True
        ordering = ['date_joined']        
    
    username = models.CharField(max_length=150 ,blank=True, null=True, unique=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    image = models.ImageField(upload_to="user_images/", blank=True, null=True)
    phone_number = models.PositiveBigIntegerField(blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    refer_code = models.UUIDField(default=uuid.uuid4)
    refer_parent = models.ForeignKey('self',null=True,blank=True, on_delete=models.CASCADE,  related_name='reference_parent')
    forget_password = models.CharField(max_length=100, default=uuid.uuid4, null=True, blank=True)
    objects = UserManager()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['password']

    def delete(self, using=None, keep_parents=False):
        self.image.storage.delete(self.image.name)
        super().delete()

    def save(self, *args, **kwargs):
        if not self.username and not self.id:
            user_name = 'username' + str(self.phone_number)
            self.username = user_name
            super().save(*args, **kwargs)
        elif self.id and self.image:
            output = generate_thumbnail(self.image, 1024, 768)
            name = "%s.jpg" % str(uuid.uuid4())
            self.image = InMemoryUploadedFile(
                output, "ImageField", name, "image/jpeg", sys.getsizeof(output), None
            )
        super().save(*args, **kwargs)

    def create_user(phone, password, reference, email, **extra_fields):
            add_user = User( 
                     phone_number=phone,
                     password=password, 
                     refer_parent=reference,
                     email=email,
                     **extra_fields
                     )
            password = add_user.set_password(password)
            add_user.save()
            return add_user
    
    def __str__(self):
        return self.username
