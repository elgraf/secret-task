# Generated by Django 2.2.3 on 2019-08-01 12:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Category')),
            ],
        ),
        migrations.CreateModel(
            name='WishedProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_to', models.DateField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Product')),
            ],
        ),
        migrations.CreateModel(
            name='WishList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('products', models.ManyToManyField(through='articles.WishedProduct', to='articles.Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='wishedproduct',
            name='wish_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.WishList'),
        ),
        migrations.CreateModel(
            name='ProductPriceHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed', models.DateTimeField(auto_now=True)),
                ('start', models.DateField()),
                ('end', models.DateField(blank=True, null=True)),
                ('modifier', models.FloatField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='product',
            name='price_hystory',
            field=models.ManyToManyField(related_name='_product_price_hystory_+', to='articles.ProductPriceHistory'),
        ),
        migrations.CreateModel(
            name='CategoryPriceHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changed', models.DateTimeField(auto_now=True)),
                ('start', models.DateField()),
                ('end', models.DateField(blank=True, null=True)),
                ('modifier', models.FloatField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='category',
            name='price_hystory',
            field=models.ManyToManyField(related_name='_category_price_hystory_+', to='articles.CategoryPriceHistory'),
        ),
    ]