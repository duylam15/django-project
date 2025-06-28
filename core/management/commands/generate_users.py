from django.core.management.base import BaseCommand
from core.models import User
from django.contrib.auth.hashers import make_password
from datetime import datetime
import random

class Command(BaseCommand):
    help = 'Generate 10,000 users for testing'

    def handle(self, *args, **kwargs):
        users = []
        hashed_password = make_password('password123')  # mã hóa 1 lần

        for i in range(1000, 10000):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com',
                phone_number=f'090{i:07d}',
                is_active=True,
                is_online=bool(i % 2),
                last_active_at=datetime.now(),
                avatar='https://example.com/avatar.png',
                url_background='https://example.com/bg.jpg',
                role='USER',
                password=hashed_password
            )
            users.append(user)

        User.objects.bulk_create(users, batch_size=1000)
        self.stdout.write(self.style.SUCCESS('✅ Đã tạo xong 10,000 user!'))
