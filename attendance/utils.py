from django.utils import timezone
from django.db.models import Max
from rest_framework_simplejwt.tokens import RefreshToken

import re

def generate_user_id(dept,doj):

    # 24gkt.tec01
    from .models import AppUser,SystemStats
    prefix = 'gkt'

    dept_map = {
        'technology': 'tec',
        'developer': 'dev',
        'ai engineer': 'aie',
        'graphic designing': 'grd'
    }

    dept_code = dept_map.get(dept.lower())

    if not dept_code:
        raise ValueError(f"Bad Request: Department '{dept}' does not exist.")

    year = str(doj.year)[-2:]

    systemstat_data,created = SystemStats.objects.get_or_create(
        id = 1,
        defaults={
            "total_users": 0,
            "total_active_users": 0,
            "total_admins": 0,
            "last_updated_at": timezone.now
        })
    total_users = systemstat_data.total_users
    if total_users and total_users>0:
        new_number = total_users + 1
    else:
        new_number = 1
        
    sequence = str(new_number).zfill(3)
    return f"{year}{prefix}.{dept_code}{sequence}"

def get_token_for_app_user(user):
    refresh = RefreshToken()
    refresh['user_id'] = user.user_id
    refresh['email'] = user.email
    refresh['role'] = user.role

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }
