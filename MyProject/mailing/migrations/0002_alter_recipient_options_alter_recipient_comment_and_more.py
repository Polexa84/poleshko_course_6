# Generated by Django 5.2 on 2025-04-18 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipient',
            options={'verbose_name': 'Получатель', 'verbose_name_plural': 'Получатели'},
        ),
        migrations.AlterField(
            model_name='recipient',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='recipient',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='recipient',
            name='full_name',
            field=models.CharField(max_length=255, verbose_name='Ф.И.О.'),
        ),
    ]
