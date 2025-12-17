from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from .models import AppUser,AttendanceSession,SystemStats



class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppUser
        fields = ['password','role','department','designation','full_name','email','date_of_joining']

    def validate_email(self,value):
        if AppUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationErrors("This Email is already Registered.")
        return value

class LoginSerializer(serializers.Serializer):

    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)


    def validate(self,attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        try:
            user = AppUser.objects.get(email=identifier)
        except AppUser.DoesNotExist:
            try: 
                user = AppUser.objects.get(user_id = identifier)
            except AppUser.DoesNotExist:
                raise serializers.ValidationError("Invaild Email / UserId or Password")

        if not check_password(password,user.password):
            raise serializers.ValidationError("Invaild Email / UserId or Password")

        if user.status == 'suspended':
            raise serializers.ValidationError('Your account has been Suspended, Contact admin')
        
        if user.status == 'terminated':
            raise serializers.ValidationError('You have been terminated, Login disabled.')
   
        attrs['user']= user
        return attrs
            
class AttedanceSessionSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.user_id',read_only=True)
    class Meta:
        model = AttendanceSession
        fields = ['id','date','check_in','check_out','duration','user_id']

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppUser
        fields = ['user_id','email','designation','department','full_name','date_of_joining']
        read_only_fields =['user_id','email','designation','department','date_of_joining','full_name']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self,data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {
                    'confirm_password': "Passwords does not match."
                }
            )
        return data

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['user_id','full_name','status']

class AdminUpdateUserDetailsSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=False)

    dept_map = {
        'technology': 'tec',
        'developer': 'dev',
        'ai engineer': 'aie',
        'graphic designing': 'grd'
    }

    class Meta:
        model = AppUser
        fields = ['user_id','role','email','designation','department',
            'full_name','status','date_of_joining','password'
        ]
        read_only_fields = ['user_id']

   
    def validate_department(self,value):
        if value.lower() not in self.dept_map.keys():
            raise ValidationError({ 'message': "Department does not exists." })
        return value

    def update(self,instance,validated_data):
        password = validated_data.pop('password',None)
        new_department = validated_data.get('department')

        

        if new_department and new_department != instance.department:
            short_code = self.dept_map.get(new_department.lower())

            parts = instance.user_id.split('.')
            prefix,suffix = parts[0],parts[1]

            serial_number = ''.join(filter(str.isdigit,suffix))
            new_suffix = short_code+serial_number

            new_user_id = prefix + '.' + new_suffix

            instance.user_id = new_user_id
        
           
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
        
class AdminAttendanceCorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = '__all__'
        read_only = ['id','user_id','duration','date']

    def update(self,instance,validated_data):

        check_in = validated_data.get('check_in',instance.check_in)
        check_out = validated_data.get('check_out',instance.check_out)

        instance.check_in = check_in
        instance.check_out = check_out

        if instance.check_in and instance.check_out:
            if instance.check_in > instance.check_out:
                raise ValidationError({'message': 'Check-out time cannot earlier than Check-in.'})
            
            instance.duration = instance.check_out - instance.check_in
        
        instance.save()
        return instance

class SystemStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemStats
        fields = '__all__'
        read_only = ['id']

