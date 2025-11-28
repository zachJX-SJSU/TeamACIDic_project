# TeamACIDic_project
![TeamACIDic](images/ACIDic_Logo.png)
  
## Project doc: [Link](https://docs.google.com/document/d/1KOwQlmOzraVL-2klA4cSM-j70bPivSmTgC_P4Kbr2zo/edit?usp=sharing)


## Database Schema:  

![Schema](images/employees.png)

## Initial setup steps:
1. First, run the starter script : `./setup_env.sh`, this will install all the required tools, it will also automatically install all the python packages in requrirement.txt.

2. Load the employee sql table:  
Employees_dev.sql is the samller cutoff database for developement, load them into mysql with:  
`sudo mysql -u root < employees_dev.sql`

3. Create a dedicated MySQL user for the database, and then set the username and password in db.py:
   - Run `sudo mysql -u root` to log into mysql
   - Create a user "hr_user" with a password: `CREATE USER 'hr_user'@'localhost' IDENTIFIED BY 'your_password';`
   - Then grant permission of the "employees" database to this user: `GRANT ALL PRIVILEGES ON employees.* TO 'new_user'@'localhost';`
     then update the changes: `FLUSH PRIVILEGES;` Then exit mysql. You can later verify the changes with `mysql -u hr_user -p`
   
   - Go to `/app/db.py` and update the URL with your username and password:
     `DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://hr_user:your_password@localhost:3306/employees",)`

4. Go back to the project directory, then run the script to populate the initial auth_user db with default username([initial]_[emp_no]) and password("abc123"):
`cd /path/to/projectsource  
.venv/bin/activate  
python -m scripts.backfill_auth_users`

5. At this point, all setup is complete, you should be able to start the FastAPI app with: `uvicorn app.main:app --reload` with no error.  

For testing, do the following:  
First make sure to activate virtual env:  
`source .venv/bin/activate`  
,then run:   
`pytest`
or with coverage:
`pytest --cov=app`
