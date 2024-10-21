from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view 
from .models import Stock
from .serializers import StockSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

@api_view(['GET'])
def stock_list(request):
    #get stocks by calling function in another module
    stocks = [
        {"name": "Tesla", "symbol": "TSLA", "price": 950.00},
        {"name": "Apple", "symbol": "AAPL", "price": 145.00},
    ]
    return Response(stocks)
