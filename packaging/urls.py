from django.urls import path
from packaging.views import RecommendBoxAPIView

urlpatterns = [
    path('orders/recommend-box/', RecommendBoxAPIView.as_view(), name='recommend-box'),
]
