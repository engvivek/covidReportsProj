# Generated by Django 4.2.14 on 2024-07-28 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CovidReportByUser',
            fields=[
                ('username', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('countries_handled_by_user', models.TextField(max_length=1000)),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'country_by_user',
            },
        ),
        migrations.CreateModel(
            name='UserRegistration',
            fields=[
                ('name', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=64)),
                ('mobile', models.BigIntegerField()),
                ('email', models.EmailField(max_length=254)),
                ('added_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'user_register',
            },
        ),
        migrations.AddConstraint(
            model_name='userregistration',
            constraint=models.UniqueConstraint(fields=('username', 'mobile'), name='user_register_uniq'),
        ),
        migrations.AddConstraint(
            model_name='covidreportbyuser',
            constraint=models.UniqueConstraint(fields=('username',), name='country_by_user_uniq'),
        ),
    ]
