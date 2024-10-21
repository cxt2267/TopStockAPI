from django.db import models

class Stock(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_change = models.DecimalField(max_digits=10, decimal_places=2)
    day_trade_rating = models.IntegerField()
    swing_trade_rating = models.IntegerField()
    scalp_trade_rating = models.IntegerField()
    position_trade_rating = models.IntegerField()

    def __str__(self):
        return self.name

    
