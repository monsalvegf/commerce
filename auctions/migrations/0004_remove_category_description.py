# Generated by Django 4.2.6 on 2024-02-09 20:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_remove_listing_ends_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='description',
        ),
    ]
