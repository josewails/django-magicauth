# Generated by Django 2.2.13 on 2020-06-25 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('magicauth', '0004_move_old_key_to_new_encrypted_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='magictoken',
            name='old_key',
        ),
    ]
