# TeamACIDic_project
![TeamACIDic](images/ACIDic_Logo.png)
Project doc: [Link](https://docs.google.com/document/d/1KOwQlmOzraVL-2klA4cSM-j70bPivSmTgC_P4Kbr2zo/edit?usp=sharing)


Database Schema:
![Schema](images/employees.png)

Employees_dev.sql is the samller database for dev, load them into mysql with:  


`mysql -u root -p < employees_dev.sql`


For testing, run the following:
First make sure to activate virtual env:
`source .venv/bin/activate`
,then run:
`pytest`
or with coverage:
`pytest --cov=app`