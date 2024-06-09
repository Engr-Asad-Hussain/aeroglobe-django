# django_ems
A Django Event Management Service (BE)


## Setup local development
1. Clone the repository
```sh
git clone https://github.com/Engr-Asad-Hussain/aeroglobe-django.git && cd aeroglobe-django
```

2. Create a virtual environment (for Linux distribution) and activate virtual environment.
```sh
python -m virtualenv venv && . venv/bin/activate
```

3. Install dependencies
```sh
pip install -r requirements/local.txt
```

4. Setup database
```sh
docker-compose -f docker-compose.db.yaml up -d
```

5. Create a `.env` file in the root of the project and inject following variables:
```sh
USE_DOCKER=True
TOKEN_SECRET="EV2HDZLGGkUgI1I0WcMXpA18MOhvEsVT"

# Database Configurations
DATABASE_NAME="postgres-django"
DATABASE_USER="postgres"
DATABASE_PASSWORD="admin123"
DATABASE_HOST="localhost"
DATABASE_POST="5432"
```

6. Apply the migrations
```sh
python manage.py makemigrations && python manage.py migrate
```

7. Run the integration tests
```sh
pytest
```

8. Start the development server
```sh
python manage.py runserver
```

9. Cleanup resources
```sh
docker-compose -f docker-compose.db.yaml down -v
```
