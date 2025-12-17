from django.shortcuts import render
from .models import AppUser, AttendanceSession, SystemStats
from .utils import get_token_for_app_user
from .permissions import IsAdmin,IsUser
from .serializers import RegisterSerializer, LoginSerializer, AttedanceSessionSerializer, AdminAttendanceCorrectionSerializer
from .serializers import ProfileSerializer, ChangePasswordSerializer, UserListSerializer, AdminUpdateUserDetailsSerializer
from .serializers import SystemStatsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404

# Create your views here.

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_token_for_app_user(user)

            return Response({
                'message': 'Login Successfully',
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': {
                    'user_id': user.user_id,
                    'full_name': user.full_name,
                    'email': user.email,
                    'role': user.role,
                }
                
            },status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {"detail": "Refresh Token is Required"},status=status.HTTP_400_BAD_REQUEST
            )

        
        try:
            print(1234567890)
            refresh = RefreshToken(refresh_token)
            new_access = refresh.access_token

            return Response(
                {
                    'access': str(new_access)
                },
                status=status.HTTP_200_OK
            )
        except TokenError:
            raise AuthenticationFailed("Invalid or Expired refresh Token")

class RegisterView(APIView):
    permission_classes =[IsAuthenticated,IsAdmin]
    def post(self,request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
   
   def delete(self,request,id):
    try:
        user = AppUser.objects.filter(user_id =id)
        print(user.data)
        return Response({ "message": "User Deleted Successfully" }, status=status.HTTP_200_OK)
    except:
        return Response({ "message": "User Id Not Found" },status=status.HTTP_404_NOT_FOUND)

class CheckInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user = request.user
        print(user,1234567)

        opened_session = AttendanceSession.objects.filter(
            user=user,
            check_out__isnull = True
        ).first()

        if opened_session:
            return Response(
                {
                    "detail": "You already Checked in. Please Check out first." 
                },
                status = status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()
        today = timezone.localdate()

        session = AttendanceSession.objects.create(
            user = user,
            date = today,
            check_in = now,
            check_out =None,
            duration = None,
        )


        serializer = AttedanceSessionSerializer(session)

        return Response(
            {
                "message": "Check-in Successfull",
                "session": serializer.data
            },
            status = status.HTTP_201_CREATED
        )

class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self,request):
        user = request.user

        opened_session = AttendanceSession.objects.filter(
            user=user,
            check_out__isnull=True
        ).order_by('-check_in').first()


        if not opened_session:
            return Response(
                {
                    "details": "No active session found. You're not checked in. "
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        now = timezone.now()
        opened_session.check_out = now
        opened_session.duration = now - opened_session.check_in
        opened_session.save()

        serializer = AttedanceSessionSerializer(opened_session)

        return Response(
            {
                "message": "Check-out Successful",
                "Session": serializer.data
            },
            status=status.HTTP_200_OK
        )

class AttendanceHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        today = timezone.localdate()

       
        date_param = request.query_params.get('date')
        start_date_param = request.query_params.get('start')
        end_date_param = request.query_params.get('end')

        sessions = AttendanceSession.objects.filter(user=user,check_out__isnull=False)

        if 'today' in request.query_params:
            sessions = sessions.filter(date=today)
        elif date_param:
            sessions = sessions.filter(date=date_param)
        elif start_date_param and end_date_param:
            sessions = sessions.filter(date__range=[start_date_param,end_date_param])


        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(sessions,request)
        serializer = AttedanceSessionSerializer(result_page,many=True)

        total_duration = timedelta()
        for session in sessions:
            if session.duration:
                total_duration += session.duration

        total_seconds = int(total_duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        return paginator.get_paginated_response(
            {
                "total_working_hours": f"{hours}h {minutes}m",
                "sessions": serializer.data
            }
        )

class UserProfileView(APIView):
    permission_classes =[IsAuthenticated]

    def get(self,request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes=[IsAuthenticated]

    def put(self,request):
        
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not check_password(old_password,user.password):
                return Response({
                    'error': 'Old Password is incorrect'
                },status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response({
                "message": "Password Updated Successfully"
            },status=status.HTTP_200_OK)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class AdminAttendanceView(APIView):
    permission_classes = [IsAdmin]

    def get(self,request):
        sessions = AttendanceSession.objects.all()

        today = timezone.localdate()

        
        user_id_param = request.query_params.get('user')
        date_param = request.query_params.get('date')
        start_date_param = request.query_params.get('start')
        end_date_param = request.query_params.get('end')
        
        
        if user_id_param:
            sessions = sessions.filter(user__user_id=user_id_param)
        if 'today' in request.query_params:
            sessions = sessions.filter(date=today)
        if date_param:
            sessions = sessions.filter(date=date_param)
        if start_date_param and end_date_param:
            sessions = sessions.filter(date__range=[start_date_param,end_date_param])

        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(sessions,request)
        serializer = AttedanceSessionSerializer(result_page,many=True)

        return paginator.get_paginated_response(
            {
                "session": serializer.data
            }
        )

class UserListView(APIView):
    permission_classes=[IsAdmin]

    def get(self,request):
        users = AppUser.objects.all().order_by('full_name')
        serializer = UserListSerializer(users,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class AdminUpdateUserDetailsView(APIView):
    permission_classes =  [IsAdmin]

    def get(self,request,user_id):

        user = get_object_or_404(AppUser,user_id=user_id)
        serializer = AdminUpdateUserDetailsSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def patch(self,request,user_id):
        admin = request.user
        admin_password = request.data.get('admin_password')

        if not admin_password or not check_password(admin_password,admin.password):
            return Response(
                {'message': 'Admin Password verification failed.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user = get_object_or_404(AppUser,user_id=user_id)
        serializer = AdminUpdateUserDetailsSerializer(user,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'User details updated Successfully','data':serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,user_id):
        admin = request.user
        admin_password = request.data.get('admin_password')

        if not admin_password or not check_password(admin_password,admin.password):
            return Response(
                { 'message': 'Admin password verification failed.' },
                status=status.HTTP_403_FORBIDDEN
            )

        user = get_object_or_404(AppUser,user_id=user_id)
        user.delete()

        return Response(
            { 'message': 'User deleted successfully.' },
            status=status.HTTP_200_OK
        )

class AdminAttendanceCorrectionView(APIView):
    permission_classes = [IsAdmin]

    def patch(self,request,session_id):
        admin = request.user
        admin_password = request.data.get('admin_password')


        if not admin_password or not check_password(admin_password,admin.password):
            return Response(
                {
                    "message": "Admin password verification failed."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        session = get_object_or_404(AttendanceSession,id=session_id)
        serializer = AdminAttendanceCorrectionSerializer(session,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'message': 'Attendance session corrected successfully.',
                    'data': serializer.data
                }
            )

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,session_id):
        admin = request.user
        admin_password = request.data.get('admin_password')

        if not admin_password or not check_password(admin_password,admin.password):
            return Response(
                {
                    'message': 'Admin password verification failed.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        session = get_object_or_404(AttendanceSession,id=session_id)

        session.delete()

        return Response(
            {
                'message': 'Attendance session deleted successfully.'
            },
            status=status.HTTP_200_OK
        )

class SystemStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self,request):
        
        stats = get_object_or_404(SystemStats,id=1)
        serializer = SystemStatsSerializer(stats)

        return Response(
            {
                'message': 'System Statistics fetched successfully.',
                'data' : serializer.data
            },
            status=status.HTTP_200_OK
        )

class ApiWorkingTest(APIView):
    def get(self,request):
        return Response("API IS WORKING, GOOD TO GO!",status=status.HTTP_200_OK)