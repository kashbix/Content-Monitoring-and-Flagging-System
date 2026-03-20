from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Keyword, ContentItem, Flag
from .services import ContentScannerService

class ContentScannerTests(APITestCase):
    
    def setUp(self):
        # Create a keyword to test with
        self.keyword_name = "django"
        self.keyword = Keyword.objects.create(name=self.keyword_name)
        
        # URLs for API testing
        self.scan_url = reverse('trigger-scan')
        self.flags_url = reverse('list-flags')

    def test_scoring_logic(self):
        """Test the deterministic scoring rules."""
        self.assertEqual(ContentScannerService.calculate_score("django", "Django", "body"), 100)
        self.assertEqual(ContentScannerService.calculate_score("django", "Learn Django Fast", "body"), 70)
        self.assertEqual(ContentScannerService.calculate_score("django", "Cooking", "I love django!"), 40)
        self.assertEqual(ContentScannerService.calculate_score("django", "Cooking Tips", "Recipes"), 0)

    def test_create_keyword_api(self):
        """Test the POST /keywords/ endpoint."""
        url = reverse('create-keyword')
        data = {'name': 'python'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Keyword.objects.count(), 2)

    @patch('scanner.services.requests.get')
    def test_full_scan_and_suppression_workflow(self, mock_get):
        """Test the end-to-end flow including the critical suppression rule."""
        
        class MockResponse:
            def __init__(self, json_data, status_code=200):
                self.json_data = json_data
                self.status_code = status_code
            def json(self):
                return self.json_data
            def raise_for_status(self):
                pass

        # --- STEP 1: Initial Scan ---
        initial_dev_to_payload = [{
            "title": "Learn Django Fast", 
            "description": "A great framework.", 
            "published_at": "2026-03-20T10:00:00Z"
        }]
        
        mock_get.return_value = MockResponse(initial_dev_to_payload)
        
        result = ContentScannerService.run_scan()
        self.assertEqual(result["flags_created"], 1)
        
        flag = Flag.objects.first()
        self.assertEqual(flag.score, 70) 
        self.assertEqual(flag.status, Flag.ReviewStatus.PENDING)

        # --- STEP 2: Reviewer marks as Irrelevant ---
        update_url = reverse('update-flag', kwargs={'pk': flag.pk})
        response = self.client.patch(update_url, {'status': 'irrelevant'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        flag.refresh_from_db()
        self.assertEqual(flag.status, Flag.ReviewStatus.IRRELEVANT)

        # --- STEP 3: Rescan with SAME content (Testing Suppression) ---
        mock_get.return_value = MockResponse(initial_dev_to_payload)
        ContentScannerService.run_scan()
        
        flag.refresh_from_db()
        self.assertEqual(flag.status, Flag.ReviewStatus.IRRELEVANT) # Still suppressed!

        # --- STEP 4: Rescan with UPDATED content (Testing Resurfacing) ---
        updated_dev_to_payload = [{
            "title": "Learn Django Fast", # MUST BE THE EXACT SAME TITLE
            "description": "Updated body with more info.", 
            "published_at": "2026-03-21T10:00:00Z" # Newer timestamp
        }]
        
        mock_get.return_value = MockResponse(updated_dev_to_payload)
        
        result = ContentScannerService.run_scan()
        self.assertEqual(result["flags_resurfaced_or_updated"], 1)
        
        flag.refresh_from_db()
        self.assertEqual(flag.status, Flag.ReviewStatus.PENDING) # Successfully resurfaced!
        self.assertEqual(flag.score, 70)