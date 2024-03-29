# Generated by Django 4.2.3 on 2023-10-14 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bus_arrival_info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bus_stop_location', models.CharField(max_length=100)),
                ('bus_number', models.CharField(max_length=20)),
                ('arrival_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='HumunFood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=100)),
                ('phone', models.CharField(default='번호 없음', max_length=50)),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('category', models.CharField(max_length=100)),
                ('content', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant_time',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_week', models.CharField(default='', max_length=100)),
                ('name', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='GaBean.restaurant')),
            ],
        ),
        migrations.CreateModel(
            name='OpeningHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.CharField(choices=[('월요일', '월요일'), ('화요일', '화요일'), ('수요일', '수요일'), ('목요일', '목요일'), ('금요일', '금요일'), ('토요일', '토요일'), ('일요일', '일요일'), ('매일', '매일'), ('휴무', '휴무')], max_length=50)),
                ('open_time', models.TimeField()),
                ('close_time', models.TimeField()),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GaBean.humunfood')),
            ],
        ),
    ]
