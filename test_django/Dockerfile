FROM debian:stretch

EXPOSE 8000

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Project files
COPY manage.py .
COPY polls polls

# Run migrations, and load the database with fixtures
# RUN python manage.py migrate && python manage.py loaddata users

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]