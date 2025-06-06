# Generated by Django 5.1.1 on 2025-05-31 09:18

import django.core.validators
import re
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_remove_user_type_role_user_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254,
                unique=True,
                validators=[
                    django.core.validators.EmailValidator(message="Email không hợp lệ!")
                ],
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                blank=True,
                max_length=15,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Số điện thoại phải từ 8 đến 15 chữ số, có thể bắt đầu bằng +.",
                        regex="^\\+?\\d{8,15}$",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="url_avatar",
            field=models.URLField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.URLValidator(
                        message="URL avatar không hợp lệ."
                    ),
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag["IGNORECASE"],
                        message="Avatar chỉ chấp nhận đuôi .jpg, .jpeg, .png",
                        regex=".*\\.(jpg|jpeg|png)$",
                    ),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="url_background",
            field=models.URLField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.URLValidator(
                        message="URL background không hợp lệ."
                    ),
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag["IGNORECASE"],
                        message="Background chỉ chấp nhận đuôi .jpg, .jpeg, .png",
                        regex=".*\\.(jpg|jpeg|png)$",
                    ),
                ],
            ),
        ),
    ]
