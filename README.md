# Megaphone OMS

## Summary

Megaphone OMS is an Order Management System designed for integration with multiple ad servers. This project focuses on connecting with the Megaphone podcast ad server via its API ([Megaphone API Docs](https://developers.megaphone.fm/)), enabling users to manage advertising campaigns (create, view, update) and synchronize data and status with Megaphone. This project manages campaigns only.

## Features

### Basic Features
- Campaign Management: Users can manage campaigns via a RESTful API service.
- Add Campaigns: Users can add new campaigns, with current advertisers fetched from Megaphone and campaigns synced upon creation.
- Update Campaigns: Users can update existing campaigns, with updates synced to Megaphone.

### Advanced Features
- Search, Pagination, and Sorting:  
  The API supports searching campaigns by title, filtering by advertiser or archive status, and sorting by various fields. Pagination is also supported for efficient data handling.
- Archiving Campaigns:  
  Campaigns can be archived or unarchived via the API. Archived campaigns can be filtered and are not deleted from the database.
- Automated Periodic Sync:  
  The system includes a scheduled job (using APScheduler) that automatically syncs all campaigns with Megaphone every 30 minutes and once at application startup, ensuring data consistency.
- Logging and Log Management:  
  Application logs are managed with log rotation, automatic compression of old log files, and automatic deletion of logs older than 90 days to ensure efficient log storage and maintenance.
- Unit and Integration Testing:  
  The project includes unit and integration tests to ensure code reliability and correctness.

## Why These Features?
- Search, Pagination, and Sorting:  
  These are essential for any production-grade OMS, especially when managing a large number of campaigns. They improve usability and performance.
- Archiving:  
  Archiving is a safer alternative to deletion, preserving data for audit/history purposes.
- Automated Sync:  
  This demonstrates backend automation and reliability, reducing manual sync needs and keeping data fresh.
- Logging and Log Management:  
  Robust logging with rotation, compression, and automatic deletion of logs older than 90 days ensures that application events and errors are tracked for debugging and monitoring, while keeping storage usage efficient over time.
- Unit and Integration Testing:  
  Automated tests help maintain code quality, catch regressions early, and ensure that both individual components and their interactions work as intended.

## Design Decisions & Trade-offs
- API-first Approach:  
  Chose RESTful APIs (with FastAPI) for flexibility, testability, and easy integration with UIs or other services.
- Database:  
  Used SQLite for simplicity and ease of setup.
- Synchronization:  
  All campaign changes are synced to Megaphone, and a background scheduler ensures periodic updates to keep data aligned.
- Archiving vs. Deletion:  
  Opted for soft-archiving to prevent accidental data loss.
- Error Handling:  
  API responses are designed to provide clear error messages, especially for remote API failures.
- Logging and Log Management:  
  Used timed log rotation with compression and a 90-day retention policy to control disk usage and reduce maintenance overhead, accepting the trade-off of limited long-term log availability.
- Unit and Integration Testing:  
  Included unit and integration tests to improve reliability and ensure confidence in future changes, at the cost of additional development and maintenance effort.

## Getting Started

### Prerequisites
- Python 3.10
- (Optional) Virtual environment tool (e.g., `venv` or `conda`)

### Installation (Local)
1. Clone the repository:
   ```bash
   git clone https://github.com/JennaLiao5/megaphone-api-service.git
   cd megaphone-api-service
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - Copy `.env.example` to `.env` and fill in the required Megaphone API credentials and settings.

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Environment Variables
The application requires the following environment variables (see `.env.example`):

| Variable              | Description                                 | Example Value                          |
|-----------------------|---------------------------------------------|----------------------------------------|
| MEGAPHONE_BASE_URL    | Megaphone API base URL                      | https://cms.megaphone.fm/api           |
| MEGAPHONE_API_TOKEN   | Your Megaphone API token (keep secret)      | (obtain from Megaphone)                |
| MEGAPHONE_ORG_ID      | Organization ID from Megaphone              | (obtain from Megaphone)                |

- When running locally, set these in your `.env` file (use `.env.example` as a template).

### API Documentation
Once running, interactive API docs are available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example API Endpoints

#### Local APIs
- `GET /advertisers` — List advertisers (required for campaign creation)
- `GET /campaigns` — List campaigns (supports search, pagination, sorting, filtering)
- `POST /campaigns` — Create a new campaign
- `GET /campaigns/{campaign_id}` — Get a campaign by ID
- `PUT /campaigns/{campaign_id}` — Update a campaign
- `PUT /campaigns/{campaign_id}/archive` — Archive/unarchive a campaign

#### Remote APIs
- `GET /remote/advertisers` — List advertisers from Megaphone
- `GET /remote/campaigns` — List campaigns directly from Megaphone
- `POST /remote/campaigns` — Create a campaign on Megaphone
- `GET /remote/campaigns/{campaign_id}` — Get a campaign from Megaphone
- `PUT /remote/campaigns/{campaign_id}` — Update a campaign on Megaphone


#### Sync APIs
- `POST /sync/advertisers` — Sync all advertisers to Megaphone
- `POST /sync/campaigns` — Sync all campaigns to Megaphone


## Running Tests
To run all unit and integration tests:

```bash
pytest tests/
```

## Thought Process
- Focused on reliability (automatic sync), usability (search/pagination), and data safety (archiving).
- Designed for extensibility (easy to add new ad server integrations or UI layers).
- Chose FastAPI for its speed, modern features, and built-in API docs.

## Contact
For questions or suggestions, please open an issue or contact the maintainer.
