Project developed as part of the Data Bases course in the first semester of the 2024/2025 academic year. Python application demonstrating access to a relational database of Taylor Swift's discography.

#  References

- [sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [Jinja templates](https://jinja.palletsprojects.com/en/3.0.x/)


# Installing dependencies

## Python 3 and pip

You must have Python 3 and the pip package manager installed. You can
install them on Ubuntu, for example, using:

```
sudo apt-get install python3 python3-pip
```

## Python libraries

```
pip3 install --user Flask
```

or

```
sudo apt install python3-flask
```
# Creating and populating the database
Run the “tables.sql” file to create the database, “taylor_swift.db”.
Run the “povoamento.py” file to populate that database.


# Running the application

Go to the “application” directory. 
Start the application by running `python3 server.py` and interact with it
by opening a window in your browser  with the address [__http://localhost:5001/__](http://localhost:5001/) 

```
$ python3 server.py
2024-12-09 17:01:24 - INFO - Connected to database
 * Serving Flask app ‘interface’
 * Debug mode: off
2024-12-09 17:01:24 - INFO - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5001
 * Running on http://172.17.17.146:5001
2024-12-09 17:01:24 - INFO - Press CTRL+C to quit
