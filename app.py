from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse
import datetime

app = Flask(__name__)

# Application version
APP_VERSION = os.environ.get("APP_VERSION", "v1.0.0")

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "passwors"
DATABASE = os.environ.get("DATABASE") or "employees"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = int(os.environ.get("DBPORT", "3306"))

# Create a connection to the MySQL database
try:
    db_conn = connections.Connection(
        host= DBHOST,
        port=DBPORT,
        user= DBUSER,
        password= DBPWD, 
        db= DATABASE
    )
    print(f"Database connection established to {DBHOST}:{DBPORT}")
except Exception as e:
    print(f"Database connection failed: {e}")
    db_conn = None

output = {}
table = 'employee';

# Define the supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}

# Create a string of supported colors
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Generate a random color
COLOR = random.choice(["red", "green", "blue", "blue2", "darkblue", "pink", "lime"])

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', color=color_codes[COLOR], version=APP_VERSION)

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html', color=color_codes[COLOR], version=APP_VERSION)

@app.route("/health", methods=['GET'])
def health():
    status = "healthy"
    db_status = "connected"
    
    if db_conn is None:
        status = "unhealthy"
        db_status = "disconnected"
    else:
        try:
            cursor = db_conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
        except Exception as e:
            status = "unhealthy"
            db_status = f"error: {str(e)}"
    
    return {
        "status": status,
        "version": APP_VERSION,
        "timestamp": datetime.datetime.now().isoformat(),
        "database": db_status
    }
    
@app.route("/addemp", methods=['POST'])
def AddEmp():
    if db_conn is None:
        return "Database connection not available", 500
        
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql,(emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    except Exception as e:
        print(f"Error inserting employee: {e}")
        return f"Error: {str(e)}", 500
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, color=color_codes[COLOR], version=APP_VERSION)

@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=color_codes[COLOR], version=APP_VERSION)

@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    if db_conn is None:
        return "Database connection not available", 500
        
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location from employee where emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql,(emp_id))
        result = cursor.fetchone()
        
        if result is None:
            return render_template("getempoutput.html", error="Employee not found", color=color_codes[COLOR], version=APP_VERSION)
        
        # Add No Employee found form
        output["emp_id"] = result[0]
        output["first_name"] = result[1]
        output["last_name"] = result[2]
        output["primary_skills"] = result[3]
        output["location"] = result[4]
        
    except Exception as e:
        print(f"Error fetching employee: {e}")
        return f"Error: {str(e)}", 500
    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], color=color_codes[COLOR], version=APP_VERSION)

if __name__ == '__main__':
    
    # Check for Command Line Parameters for color
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =" + args.color)
        COLOR = args.color
        if COLOR_FROM_ENV:
            print("A color was set through environment variable -" + COLOR_FROM_ENV + ". However, color from command line argument takes precendence.")
    elif COLOR_FROM_ENV:
        print("No Command line argument. Color from environment variable =" + COLOR_FROM_ENV)
        COLOR = COLOR_FROM_ENV
    else:
        print("No command line argument or environment variable. Picking a Random Color =" + COLOR)

    # Check if input color is a supported one
    if COLOR not in color_codes:
        print("Color not supported. Received '" + COLOR + "' expected one of " + SUPPORTED_COLORS)
        exit(1)

    print(f"Starting CLO835 Application Version: {APP_VERSION}")
    print(f"Database Host: {DBHOST}:{DBPORT}")
    print(f"Application Color: {COLOR}")
    
    app.run(host='0.0.0.0',port=8080,debug=True)
