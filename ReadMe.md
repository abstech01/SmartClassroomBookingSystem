# Welcome to SmartClassRoom Booking Portal

### 1.0 Getting Started
1. Create Account on Mailjet (If you wish to receive email notifications)

### 2.0 Clone Repository

### 3.0 Run Project
1. Open Solution File on IDE
2. Run the following commands:
   1. pip install -r requirements.txt
   2. del db.sqlite3
   3. python manage.py makemigrations accounts
   4. python manage.py makemigrations bookings
   5. python manage.py makemigrations
   6. python manage.py migrate
   7. python manage.py runserver
