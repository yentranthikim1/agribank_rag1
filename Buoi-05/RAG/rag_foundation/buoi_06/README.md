Buoi 6 environment setup
=========================

Run the setup with the existing Buoi 5 interpreter. Do not create a new virtual environment:

	..\buoi_05\.venv\Scripts\python.exe setup_environment.py

The script creates missing .env settings without overwriting existing values, installs only the packages listed in requirements.txt, checks imports, initializes Chroma Embedded Local when no Chroma Server is available, and creates rag_db when PostgreSQL is reachable.
