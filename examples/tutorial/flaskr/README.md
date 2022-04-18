# This is a step by step proces for running the flask project

## Clone the repo locally 
` $ git clone https://github.com/pallets/flask.git py-flask  `  

_Ref: https://github.com/pallets/flask/tree/main/examples/tutorial_

## Create and activate the virtual environment  

`$ cd py-flask `  
`$ cd examples/tutorial `  
`$ python -m venv venv `  
`$ venv\Scripts\activate.bat `  
`(venv) $ `  

## Install the required packages
`$ pip install -e . `  
`$ pip install cryptography `

## Set the environment variables
`$ set FLASK_APP=flaskr `  
`$ set FLASK_ENV=development `  

_Note: In windows, no spaces are allowed when setting up above variables_  

## Initialize the Sqlite database and run the server
`$ flask init-db `  
This will create a sqlite database _flaskr.sqlite_ under _tutorial/instance_ folder  

`$ flask run `  
Open the browser at http://127.0.0.1:5000  


 ## Test and run the database
`$ cd tutorial\instance `  
`$ sqlite3 flaskr.sqlite `  
`(sqlite)$ .schema post `  
`(sqlite)$ select * from post; `  
`(sqlite)$ .exit `  


## Creating the config file
`$ cd tutorial\instance `  
Create a config file _config.py_ 
Provide the app config key, values
- ` POST_MASTER_KEY="This is the key to encrypt post" `  
