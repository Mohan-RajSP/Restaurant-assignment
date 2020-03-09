# Rest-0-Cafe Microservice

REST API written in Python Flask using SQLAlchemy as the ORM with auto migration capabilities

## Pre-requisites
  - Download & install [Python 3.6](https://www.python.org/downloads/)
  - Download & install [Pip]
   ```bash
    python -m pip install -U pip 
   ```
  - Download & Install [MySQL](https://www.mysql.com/) Server locally or use an external database (OPTIONAL)


## Installation

  ```bash
  # Clone the repository 
    https://github.com/Mohan-RajSP/Restaurant-assignment.git
  # Change into the directory
    cd Rest-0-Cafe
  # Setup the .env file from .sample.env file


## Running the application

  **Start the app**
  ```bash
  Run the batch script
    manage.bat
  ```
  **Start the app for developers**
  ```bash
  python wsgi.py
  ```

 ## To Run the SWAGGER UI
 ```bash
    - Swagger for authorization and authentication
        http://localhost:5000/auth/
    - Swagger for Restaurants
        http://http://localhost:5000/restaurant/
    ```
  
 
## Author
Mohan Raj Paramasivam