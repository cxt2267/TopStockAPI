# Generated by Django 5.1.2 on 2024-10-16 21:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sentimentdata",
            name="stock",
        ),
        migrations.RemoveField(
            model_name="stockranking",
            name="stock",
        ),
        migrations.RemoveField(
            model_name="technicaldata",
            name="stock",
        ),
        migrations.DeleteModel(
            name="FundamentalData",
        ),
        migrations.DeleteModel(
            name="SentimentData",
        ),
        migrations.DeleteModel(
            name="StockRanking",
        ),
        migrations.DeleteModel(
            name="TechnicalData",
        ),
    ]
