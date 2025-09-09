# Academic Project Management System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue?style=for-the-badge&logo=postgresql)
![Status](https://img.shields.io/badge/Status-Finished-green?style=for-the-badge)

## Overview
This project is a database system developed to manage academic projects, such as Scientific Initiation, Extension, and Tutoring.  
The application allows registering and querying information about students, professors, departments, projects, job opportunities, and sponsors.  
It was developed by me and my colleagues as part of the **Database** course.

The system includes a graphical user interface built in Python that connects to a PostgreSQL database to perform queries and operations, such as listing projects, enrolling students, approving applications, and generating reports on vacancies and funding contributions.

## Technologies Used
* **Programming Language:** Python  
* **Database:** PostgreSQL  
* **Graphical User Interface (GUI):** CustomTkinter  
* **Database Connector:** Psycopg2  

## Database Model
The project was modeled at three levels of abstraction: conceptual, relational, and physical.

### 1. Conceptual Schema
The Entity-Relationship (ER) model was designed to represent the main entities of the system and their relationships.  
Entities include `Student`, `Professor`, `Project`, `Opportunity`, `Department`, `Sponsor`, among others.  

The full diagram is available in the file `Esquema Conceitual.xml`.

### 2. Relational Schema
From the conceptual model, the relational schema was derived, defining the structure of the tables, their attributes, primary keys, and foreign keys.  
The main relations (tables) are:

* **Student**: Stores student information.  
* **Professor**: Stores professor data and their department.  
* **Department**: Institution’s departments.  
* **Project**: Central table storing all projects, with specializations such as **ExtensionProject**, **Tutoring**, and **ScientificInitiation**.  
* **Opportunity**: Defines available project vacancies, including **PaidOpportunity**.  
* **Enrolls**: Associative table that records student enrollment in opportunities.  
* **Sponsor** and **Contribution**: Manage sponsors and their financial contributions.  
* **Coordinates**: Associates professors with the projects they coordinate.  

Detailed information is available in the file `Esquema Relacional.pdf`.

### 3. Physical Schema
The physical schema was implemented in PostgreSQL.  
The file `Esquema Físico - SQL.sql` contains:
* `CREATE TABLE` commands for all tables.  
* All integrity constraints (`PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `CHECK`).  
* `INSERT INTO` commands to populate the database with example data, enabling immediate testing.  

## System Features
The graphical interface (`system.py`) offers the following features:

### Queries
* **List Projects and Professors**: Displays all projects, professors, and departments.  
* **List Students by Project**: Search by project code to list enrolled students and their status ("Approved" or "Enrolled").  
* **List Contributions by Sponsor**: Shows all contributions (projects and amounts) of a given sponsor.  
* **Vacancy Status**: Report showing total vacancies, filled positions, pending enrollments, and remaining spots.  
* **List Sponsors**: Displays all registered sponsors.  
* **Search Projects by Professor**: Search projects by professor’s name.  
* **Search Courses by Department**: Lists all courses for a given department.  

### Operations
* **Approve Student Enrollment**: Changes a student’s status from "Enrolled" to "Approved", recording start and end dates.  
* **Delete Enrollment**: Removes a student’s enrollment record from a project.  

## Environment Setup

### 1. Requirements
* Python 3.x installed  
* PostgreSQL installed and running  

### 2. Database Setup
1. Create a database on your PostgreSQL server.  
2. Run the script `Esquema Físico - SQL.sql` to create the tables and populate them with initial data. You can use a client like DBeaver/pgAdmin or the terminal:  
   ```bash
   psql -U your_user -d your_database -f "Esquema Físico - SQL.sql"
   ```
### 3. Application Setup

Clone this repository or download the files.
Create and activate a virtual environment (recommended):

```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux / macOS
    source venv/bin/activate
```
Install dependencies from requirements.txt:

```bash
    pip install -r requirements.txt
```

Adjust the database connection: Open system.py and edit the conectar_bd() function with your PostgreSQL credentials.

```python
    def conectar_bd():
        try:
            conn = psycopg2.connect(
                dbname="postgres",      # Ou o nome do seu banco
                user="postgres",        # Seu usuário do PostgreSQL
                password="laura123",    # Sua senha
                host="localhost",
                port="5432"
            )
            return conn
        # ...
```

With the environment set up and the database running, execute the following command in the terminal::

```bash
python system.py
```
