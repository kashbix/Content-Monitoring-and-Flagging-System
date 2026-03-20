# Content Monitoring and Flagging System

This my submission for the Take-Home Assignment as mention in the PDF. This backend system handles content ingestion from external sources, performs automated keyword matching with deterministic scoring, and manages a human review workflow with specific suppression rules.

## Technical Stack

  - **Framework:** Django 4.2+
  - **API:** Django REST Framework (DRF)
  - **Database:** SQLite (local development)
  - **External Integration:** Dev.to API (Public Articles)


## Installation and Setup

### 1\. Environment and Dependencies

Ensure Python 3.10 or higher is installed.

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2\. Database Setup

Initialize the SQLite database and create the schema.

```bash
python manage.py makemigrations scanner
python manage.py migrate
```

### 3\. Administrative Setup

Create a superuser to access the Django Admin interface for manual flag review.

```bash
python manage.py createsuperuser
```

### 4\. Run Server

```bash
python manage.py runserver
```

The API is accessible at `[http://127.0.0.1:8000/](http://127.0.0.1:8000/)`.


## API Documentation

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| POST | \`/keywords/` | Register a new monitoring keyword |
| POST | `/scan/` | Trigger live content ingestion and matching |
| GET | `/flags/` | List all generated flags and their scores |
| PATCH | `/flags/{id}/` | Update flag status (pending, relevant, irrelevant) |

### Sample Keyword Creation
```bash
curl -X POST http://127.0.0.1:8000/keywords/ -H "Content-Type: application/json" -d '{"name": "python"}'
```

---

## Implementation Details

### Matching Logic
The system applies a deterministic scoring mechanism based on keyword location within the ingested content:
- **Score 100:** Exact keyword match in the title.
- **Score 70:** Partial keyword match in the title.
- **Score 40:** Keyword appears only in the body/description.

### Suppression Logic
The suppression rule prevents redundant flags for items previously reviewed and dismissed.
- **Criteria:** If a flag is marked as `irrelevant`, it will not reappear in subsequent scans unless the `last_updated` timestamp from the source API has changed.
- **Resurfacing:** If the source content is updated (newer timestamp), the existing flag is reset to `pending` and the score is recalculated to reflect any changes in the text.

### Testing
Automated tests verify the scoring algorithm and the suppression workflow. These tests use the `unittest.mock` library to simulate API responses, ensuring the suite runs independently of internet connectivity.
```bash
python manage.py test
```


## Assumptions and Trade-offs

- **Content Uniqueness:** Content items are uniquely identified by a combination of `title` and `source`. This prevents duplicate records for the same article across multiple scan triggers.
- **External Source:** I utilized the Dev.to Public API (`/articles`) for the "Preferred Option" requirement. It was selected because it provides real-time data without requiring authentication keys, simplifying the reviewer's setup.
- **Service Layer:** All business logic (matching, scoring, and suppression) is abstracted into a service layer (`services.py`). This keeps the views "thin" and focuses them solely on request/response handling.
- **Admin Interface:** The Django Admin has been customized to allow reviewers to update flag statuses directly from the list view, improving the efficiency of the human review workflow.
- **External API Choice:**I utilized the Dev.to Public API for content ingestion as it provides high-quality, real-time technical data and, crucially, does not require an API key. This ensures the it can run the "Preferred Solution" immediately without external configuration.



## Project Structure
```text
scanner/
├── models.py       # Database schema (Keyword, ContentItem, Flag)
├── services.py     # Core logic (Matching algorithm, Ingestion, Suppression)
├── serializers.py  # Data transformation for API
├── views.py        # API Endpoints (Thin controllers)
├── tests.py        # Automated test suite (with Mocking)
└── admin.py        # Enhanced Admin UI configuration
```


### Note:
*To see the system in action quickly, I recommend adding the keyword "python" or "javascript" via the `/keywords/` endpoint, then triggering a `/scan/`. These tags are highly active on Dev.to and will consistently generate results.*
