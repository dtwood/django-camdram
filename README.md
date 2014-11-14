django_camdram
==============

A toy project to learn the django web framework.

Installation
------------
The project requires python 3.0+ and sqlite3, there are (I believe) no other non-python dependencies. We suggest running inside a [python virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) with the python3 interpreter.

One you have the code change to the project root directory and run
```
pip install -r requirements.txt
```
to install the projects python dependencies.

Database
-------- 
The default database format is sqlite3, which should be fine for development work. You have two options for creating a database: initializing a blank database or importing a database from the real version of camdram.

### Option 1: Blank Database
Create the database:
```
python manage.py migrate
```

Add the initial data:
```

python manage.py loaddata initial_data term_dates
```

Create an admin user:
```
python manage.py createsuperuser
```

Initialize the audit log/reversion system:
```
python manage.py createinitialreversions
```

Rebuild the search index:
```
python manage.py rebuild_index
```

### Option 2: Import Database
Switch to the database migration version:
```
git checkout database-migration
```

Place your v1 database at v1_db.sqlite3 in the project root directory (or add your database credentials to the old database section in camdram/settings.py) then run:
```
python manage.py migrate
```

Initialize the audit log/reversion system:
```
python manage.py createinitialreversions
```

Rebuild the search index:
```
python manage.py rebuild_index
```

Create a new admin user if desired, although any admin user from the imported database will work:
```
python manage.py createsuperuser
```

Switch back to the main codebase:
```
git checkout master
```

Running
-------
Run the server:
```
python manage.py runserver
```
and visit http://127.0.0.1:8000
