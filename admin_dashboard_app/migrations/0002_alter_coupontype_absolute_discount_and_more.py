# Generated by Django 4.1.1 on 2022-09-15 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_dashboard_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupontype',
            name='absolute_discount',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='dilivery_price',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='total_price',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.FloatField(),
        ),
    ]
