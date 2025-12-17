from django.core.management.base import BaseCommand
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from attendance.models import AppUser

DEPARTMENT_CHOICES = ['technology','developer','ai engineer','graphic designing']

class Command(BaseCommand):
    help = 'Create the first admin user safely'

    def handle(self,*args,**kwargs):

        try:

            if AppUser.objects.filter(role='admin').exists():
                self.stdout.write(self.style.WARNING("Admin already exists"))
                return
            
            # Email input and Validation
            while True:
                email = input("Enter Admin Email:")
                try:
                    validate_email(email)
                    break
                except ValidationError:
                    self.stdout.write(self.style.ERROR("Invalid email format, Try again!"))
            full_name = input("Enter your Full name:")
            designation = input("Enter your designation:")

            self.stdout.write(self.style.WARNING(f"Available Departments:\n{DEPARTMENT_CHOICES}"))

            while True:
                department = input("Enter your department:")

                if department.lower() in DEPARTMENT_CHOICES:
                    break
                self.stdout.write(self.style.ERROR("Invalid department. choose from the list"))  
            
            # Password input and Validation
            while True:
                password = input("Enter your Password:")
                confirm_password = input("Again Enter your Password to confirm:")

                if password != confirm_password:
                    self.stdout.write(self.style.ERROR("Password does not match, Try again!"))
                else:
                    break
            
        except (KeyboardInterrupt,EOFError):
            self.stdout.write(self.style.ERROR("\nSetup Cancelled, Admin not created"))
            return
        admin = AppUser(
            role = 'admin',
            status = 'active',
            email = email,
            designation = designation,
            department = department,
            full_name = full_name
        )

        admin.set_password(password)
        admin.save()

        self.stdout.write(self.style.SUCCESS("Admin user created successfully."))