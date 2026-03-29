#!/bin/bash
set DATABASE_URL=postgresql://db_68e9_user:k5M4KoYVM5iam92Il5FERVRpbOs57N5w@dpg-d73pid9r0fns73clp24g-a.frankfurt-postgres.render.com/db_68e9
echo Starting ingestion to Render...
py src/ingest.py
echo Ingestion complete!
pause