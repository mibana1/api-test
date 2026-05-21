# Book Search Backend

Django REST backend for unified book search across Aladin, the National Library of Korea, Google Books, Kakao, and Naver.

## Setup

```bash
conda create --name bookapp python=3.11
conda activate bookapp
pip install -r requirements.txt
```

Create `backend/.env` and fill in API keys:

```env
ALADIN_API_KEY=
NL_API_KEY=
GOOGLE_BOOKS_API_KEY=
KAKAO_REST_API_KEY=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
```

Run database migrations and start the API:

```bash
python manage.py migrate
python manage.py runserver
```

The development API is served at `http://127.0.0.1:8000`.

## Endpoints

- `POST /api/aladdin/search/`
- `POST /api/center/search/`
- `POST /api/google/search/`
- `POST /api/kakao/search/`
- `POST /api/naver/search/`
- `POST /api/search/`
- `POST /api/vision/analyze/`
- `POST /api/recommender/recommend/`

All search endpoints accept:

```json
{ "query": "book title or keyword" }
```

Search responses use this schema:

```json
{
  "id": "source_isbn_or_index",
  "source": "aladin",
  "sources": ["aladin", "google"],
  "title": "string",
  "author": "string",
  "publisher": "string",
  "pubDate": "string",
  "cover": "string or null",
  "isbn": "string or null",
  "description": "string or null",
  "link": "string or null",
  "tags": ["string"]
}
```

## Frontend

From the project root:

```bash
cd frontend
npm install
npm run dev
```

The Next.js dev server proxies `/api/*` to Django at `http://127.0.0.1:8000`.
