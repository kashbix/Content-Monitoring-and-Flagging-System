from django.urls import path
from .views import KeywordCreateView, ScanAPIView, FlagListView, FlagUpdateView

urlpatterns = [
    # POST /keywords/ - Create a keyword
    path('keywords/', KeywordCreateView.as_view(), name='create-keyword'),
    
    # POST /scan/ - Trigger a scan against the chosen source
    path('scan/', ScanAPIView.as_view(), name='trigger-scan'),
    
    # GET /flags/ - List generated flags
    path('flags/', FlagListView.as_view(), name='list-flags'),
    
    # PATCH /flags/{id}/ - Update review status
    path('flags/<int:pk>/', FlagUpdateView.as_view(), name='update-flag'),
]