# TechTreds Web Application

This is a Flask application that lists the latest articles within the cloud-native ecosystem.

## Run 

To run this application there are 2 steps required:

1. Initialize the database by using the `python init_db.py` command. This will create or overwrite the `database.db` file that is used by the web application.
2.  Run the TechTrends application by using the `python app.py` command. The application is running on port `3111` and you can access it by querying the `http://127.0.0.1:3111/` endpoint.

Info
Change the running port on app.py from 3111 to 8095. Made a runLocally.sh shell script to run in plain vanilla python. A /healthz and /metrics endpoint added as per expectations. Logging added as per expectations. Additionally, a new Health&Metrics page added (monitor.html) to show the health and metrics inside the application.