import requests
from datetime import datetime
from django.utils.dateparse import parse_datetime
from .models import Keyword, ContentItem, Flag

class ContentScannerService:
    @staticmethod
    def calculate_score(keyword_str, title, body):
        keyword_lower = keyword_str.lower()
        title_lower = title.lower()
        body_lower = body.lower()

        if keyword_lower == title_lower:
            return 100
        elif keyword_lower in title_lower:
            return 70
        elif keyword_lower in body_lower:
            return 40
        return 0

    @classmethod
    def fetch_public_content(cls):
        """
        Fetches live data from the Dev.to public API.
        Maps the external payload to our internal structure.
        """
        url = "https://dev.to/api/articles?per_page=15"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            articles = response.json()
            
            payload = []
            for article in articles:
                # Map external API fields to our expected model fields
                payload.append({
                    "title": article.get("title", ""),
                    "body": article.get("description", "") or "", # Dev.to uses description as a summary
                    "source": "Dev.to", 
                    "last_updated": article.get("edited_at") or article.get("published_at")
                })
            return payload
        except requests.RequestException as e:
            # In a production app, we would log this error.
            print(f"Error fetching from external API: {e}")
            return []

    @classmethod
    def run_scan(cls):
        """
        Orchestrates fetching the live data and applying the scanning logic.
        """
        payload = cls.fetch_public_content()
        if not payload:
            return {"status": "error", "message": "Failed to fetch content from external API."}
            
        return cls._process_payload(payload)

    @classmethod
    def _process_payload(cls, payload):
        """
        The core ingestion, scoring, and suppression logic.
        """
        keywords = list(Keyword.objects.all())
        if not keywords:
            return {"status": "success", "message": "No keywords to scan."}

        flags_created = 0
        flags_updated = 0

        for item_data in payload:
            if not item_data['last_updated']:
                continue
                
            incoming_last_updated = parse_datetime(item_data['last_updated'])
            
            content_item, created = ContentItem.objects.get_or_create(
                title=item_data['title'],
                source=item_data['source'],
                defaults={
                    'body': item_data['body'],
                    'last_updated': incoming_last_updated
                }
            )

            content_changed = not created and incoming_last_updated > content_item.last_updated
            if content_changed:
                content_item.body = item_data['body']
                content_item.last_updated = incoming_last_updated
                content_item.save()

            for keyword in keywords:
                score = cls.calculate_score(keyword.name, item_data['title'], item_data['body'])
                if score == 0:
                    continue

                flag, flag_created = Flag.objects.get_or_create(
                    keyword=keyword,
                    content_item=content_item,
                    defaults={'score': score, 'status': Flag.ReviewStatus.PENDING}
                )

                if flag_created:
                    flags_created += 1
                else:
                    if flag.status == Flag.ReviewStatus.IRRELEVANT and not content_changed:
                        continue 
                    
                    if content_changed:
                        flag.score = score
                        flag.status = Flag.ReviewStatus.PENDING
                        flag.save()
                        flags_updated += 1

        return {
            "status": "success", 
            "flags_created": flags_created, 
            "flags_resurfaced_or_updated": flags_updated
        }