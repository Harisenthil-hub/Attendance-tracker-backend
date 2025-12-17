from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.hashers import make_password, check_password, identify_hasher
from .utils import generate_user_id
# Create your models here.




class AppUser(models.Model):

    user_id = models.CharField(max_length=15,unique=True,null=False,blank=False)
    role = models.CharField(
        max_length=20,
        choices=[
            ('user','User'),
            ('admin','Admin')
        ],default='user')
    email = models.EmailField(max_length=200,unique=True,null=False,blank=False)
    password = models.CharField(max_length=100)
    designation = models.CharField(max_length=50)
    department = models.CharField(
        max_length=50,
        choices=[
            ('technology','Technology'),
            ('developer','Developer'),
            ('ai engineer','AI Engineer'),
            ('graphic designing','Graphic Designing')
        ]
        ,default='technology')
    full_name = models.CharField(max_length=50)
    status = models.CharField(
        max_length=50,
        choices=[
            ('active','Active'),
            ('suspended','Suspended'),
            ('terminated','Terminated')
        ],
        default='active')
    is_verified = models.BooleanField(default=False)
    date_of_joining = models.DateField(default=date.today)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


    def set_password(self,raw_password):
        self.password = make_password(raw_password)


    def save(self,*args, **kwargs):
        if not self.user_id:
            self.user_id = generate_user_id(self.department,self.date_of_joining)
        if self.email:
            self.email = self.email.lower()
        if self.role:
            self.role = self.role.lower()
        if self.department:
            self.department = self.department.lower()
        if self.status:
            self.status = self.status.lower()
        if self.password:
            try:
               identify_hasher(self.password)
            except Exception:
                self.set_password(self.password)
  
        super().save(*args, **kwargs)

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return f"{self.full_name} ({self.email})"
    

class SystemStats(models.Model):

    total_users = models.PositiveIntegerField(default=0)
    total_active_users = models.PositiveIntegerField(default=0)
    total_admins = models. PositiveIntegerField(default=0)
    total_suspended = models. PositiveIntegerField(default=0)
    total_terminated = models. PositiveIntegerField(default=0)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total Users From SystemStats {self.total_users}"
    

class AttendanceSession(models.Model):

    user = models.ForeignKey(AppUser,on_delete=models.CASCADE,related_name="attendance_session")
    date = models.DateField(blank=False)
    check_in = models.DateTimeField(blank=False)
    check_out = models.DateTimeField(null=True,blank=True)
    duration = models.DurationField(null=True,blank=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.date} - {self.check_in.time()}"


    class Meta:
        ordering = ['-date','-check_in']
    
    

    