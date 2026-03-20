from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Keyword, Flag
from .serializers import KeywordSerializer, FlagSerializer
from .services import ContentScannerService

class KeywordCreateView(generics.CreateAPIView):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer

class FlagListView(generics.ListAPIView):
    queryset = Flag.objects.select_related('keyword', 'content_item').all()
    serializer_class = FlagSerializer

class FlagUpdateView(generics.UpdateAPIView):
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer
    http_method_names = ['patch'] 

class ScanAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Triggers a live fetch from the Dev.to public API
        result = ContentScannerService.run_scan()
        if result.get("status") == "error":
            return Response(result, status=status.HTTP_502_BAD_GATEWAY)
        return Response(result, status=status.HTTP_200_OK)