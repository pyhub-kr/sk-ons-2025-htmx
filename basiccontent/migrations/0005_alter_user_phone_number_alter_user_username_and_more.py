# Generated by Django 4.2.20 on 2025-04-22 05:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basiccontent', '0004_alter_user_birthday_alter_user_phone_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(message='전화번호는 000-0000-0000 형식이어야 합니다.', regex='^\\d{3}-\\d{4}-\\d{4}$')], verbose_name='전화번호'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=255, verbose_name='이름'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.UniqueConstraint(fields=('username', 'phone_number'), name='unique_user_phone'),
        ),
    ]
