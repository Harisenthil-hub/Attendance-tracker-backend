from .views import RegisterView,UserDeleteView,LoginView,RefreshTokenView,CheckInView
from .views import AdminAttendanceCorrectionView,  AdminUpdateUserDetailsView, SystemStatsView
from .views import CheckOutView,AttendanceHistoryView,UserProfileView, ChangePasswordView
from .views import  AdminAttendanceView, UserListView, ApiWorkingTest
from django.urls import path


urlpatterns = [
    path('token/refresh/',RefreshTokenView.as_view(),name='new_access_token'),
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name='login'),
    # path('user/<str:id>',UserDeleteView.as_view(),name='delete-user'),
    path('attendance/checkin/',CheckInView.as_view(),name='checkin'),
    path('attendance/checkout/',CheckOutView.as_view(),name='checkout'),
    path('attendance/history/',AttendanceHistoryView.as_view(),name='attendance-logs'),
    path('profile/',UserProfileView.as_view(),name='profile'),
    path('change-password/',ChangePasswordView.as_view(),name='change-password'),
    path('admin/attendance-logs/',AdminAttendanceView.as_view(),name='admin-attendance-log'),
    path('users/',UserListView.as_view(),name='user-list'),
    path('admin/user/<str:user_id>/',AdminUpdateUserDetailsView.as_view(),name='admin-update-user'),
    path('admin/attendance/correction/<int:session_id>/',AdminAttendanceCorrectionView.as_view(),name='admin-attendance-correction'),
    path('admin/system-stats/',SystemStatsView.as_view(),name='system-stats'),
    #testing
    path('test/',ApiWorkingTest.as_view(),name='work-test'),
]
