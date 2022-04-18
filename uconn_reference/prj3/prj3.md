# Project 3. A Simple Web Server

**Deadline: Tuesday, 4/5/2022.**

**Do not keep your code in a public repo.**

In this project, we will build a simple web server with Python and Flask. We
first study the code in an open-source project. Then we add a feature for 
encryting posts.

We do not have to complete the project in VirtualBox. It might be easier to
work in the host OS, e.g., Windows 10 or Linux. MacOS may not support all
libaries.

## Task 1. Run the application in tutorial

The link to the Flask main repo is [here](https://github.com/pallets/flask).

We first install and run the example in the repo. Detailed instructions are
available on the tutorial page, in a subdirectory in the Git repo
[link](https://github.com/pallets/flask/tree/main/examples/tutorial).

Read the instructions carefully. The latest version is 2.0.2, as of February 2022.

Basically, we take the following steps to run the example application. 

1.  Clone the repo. We can clone the repo (the entire flask repo) into any
    directory that is convenient. In later descriptions, we assume the repo is
    cloned in a "flask" directory, for example, "$home/flask".

2.  Create a Python virtual environment. It is recommended to work in a Python
    virtual environment so that any packages we install do not interfere with
    the system-wide installation. In later descriptions, we assume directory
    "venv" is the root of the virtual environment, which can be "$home/venv" in
    your system. **Do not forget to activate the virtual environment.**

3.  Install flask and other required packages in the virtual environment. Run
    `pip install -e .` in "flask/examples/tutorial". After the installation
    process is done, Flask and a few other packages are installed. The packages
    can be founder under "venv/Lib/site-packages" directory. 	

    Pay attention to the directory where you run pip.

    We have tested the system with Version 2.0.2. Probably you should check 
    out this version correct version before running pip. 

4.  In "flask/examples/tutorial" directory, run the example application.

    **Remember to activate the virtual environment and set proper environment
    variables * before starting the application. We can create a script to
    enter the virtual environment and set the environment variables. 

    The commands on the tutorial page include: set environment variables,
    initialize database, and then start the application (i.e., the web server).

    The commands for setting up environment variables in PowerShell are:

	$env:FLASK_APP = "flaskr"
	$env:FLASK_ENV = "development"

    We only need to initialize database once, before the first time we run the
    application.

        flask init-db

    Then, we start the web server.

        flask run

## Task 2. Study the example application in tutorial

Study the application code in the “flask/examples/tutorial/flaskr” directory
and answer the following questions. Show code (and the files you find the code)
to justify your answer.

The application files (Python code, template files, and CSS files) are located
under "flask/examples/tutorial/flaskr" directory. 

Flask documentation site has detailed explanations
[link](https://flask.palletsprojects.com/en/2.0.x/).

### 2a. Password

Only users who are logged in can create posts. Answer the following questions.

1.  How does the system generate and store the hash of passwords? What is the
    default algorithm that is used to hash passwords?

2.  How is the salt generated? 

3.  In which function (and file) is hash compared? Is it vulnerable to timing
    attacks? 

We can start with `auth.py`. Then we follow the imported modules and check some
files in installed packages (in "venv/Lib/site-packages" directory). If 
any Python library functions are used, read the manual page of the function.

### 2b. Session and cookie

Once users are logged in, the system recognizes them and then displays a
different page. Answer the following questions.

1.  How does the system do that? What cookies does the system set?

2.  What information is kept in cookies? 

3.  How is the integrity of cookies checked?

4.  Is signature verification vulnerable to timing attacks? In which 
    file is the code located?

5.  Since cookies are not encrypted, demonstrate that you can find out the
    (some) information in the cookies.

Session related code is in "flask/sessions.py" and it calls
`URLSafeTimedSerializer` in package itsdangerous. So we need to check out files
in itsdangerous, especially "signer.py".

[This page](https://flask.palletsprojects.com/en/2.0.x/quickstart/#sessions)
on the Flask documentation site explains sessions. 

[This page](https://pythonise.com/series/learning-flask/flask-session-object)
also explains the session object and includes some discussions on decoding
cookies. 

### 2c. Database

Answer the following questions.  We can focus on Python files in the flaskr
folder. 

1.   How does the application perform queries to database? 

2.   Do you see any vulnerability? 

### 2d. Output

Answer the following questions.  We can focus on Python files in the flaskr
folder. 

1.  How does the application generate html files? 

2.  Do you see any vulnerability? 

We can start with the templates under template directory.  The documentation site
also discusses templates. Search templates on the documentation site. 

## Task 3. Encrypt/decrypt the post

In this task, we modify the code so posts can be encrypted. Only users who
logged in the system can read the encrypted posts. 

We assume the following.

*   The application code (files under flaskr directory) and the database file
    (instance/) are backed up in the cloud. 

*   Adversaries may read the database file and even change the posts. 

*   We would like to protect the confidentiality and integrity of encrypted
    posts. We do not need to encrypt the subject.

*   We do not need to worry about adversaries deleting files although
    maintaining a log can help detection of some deletions.

### Configuration

We need to create a configuration file and set the application wide variable
`POST_MASTER_KEY`, which is the root key to protect posts. In this project, we
keep `config.py` under the instance directory (and we must remember that we
only back up this file to secure locations). 

The configuration file and examples can be found on the following page. The page
also has an example of generating secret bytes in Python.

[Configuration Handling — Flask Documentation
(2.0.x)](https://flask.palletsprojects.com/en/2.0.x/config/)

```
# example of generating secret bytes.
python -c 'import secrets; print(secrets.token_hex(32))'
```

Here is an example of configuraton file `instance/config.py`.
```
SECRET_KEY = "6c8dec2f3344b6d7460ace7374e13e91dac7ecf6563134f0319f0b9af1e165de"
POST_MASTER_KEY = "This is the key to encrypt post"
```

### Encrypt/Decrypt the post

Three files are revised to add the encrypt option on the pages where users
create or edit posts. Copy them to the correct directories.

Currently, if the encrypt option is checked, the post body is converted into a
hexadecimal string. The data saved in the body field of a post are a JSON
string, which is created from a dictionary in Python. You can add more data
(key and value pairs) to the dictionary. 

We can use Python cryptography package to encrypt/decrypt messages. We can use
pip to install the package in the virtual environment.

    pip install cryptography

Please read the following pages about some important functions we may need: key
derivation, key wrapping, and authenticated encryption. Select the
documentation for the version installed. 

[Primitives — Cryptography
Documentation](https://cryptography.io/en/latest/hazmat/primitives/)

In addition, you can find some examples in `ae.py`. Pay attention to the
conversion between strings and bytes.  Here are some additional requirements:

*   Each post should be encrypted by a separate key. The key and nonce are
    randomly generated. 

*   The encryption keys need to be protected. We wrap (encrypt) them with a key
    derived from the master secret. 

*   Instead of using the master secret directly, we want to apply KDF function
    to get the wrap key (KEK).  Using salt, the KEK for each post encryption
    key can be different. The reason we do not use the master secret directly
    is that it is configured by user so the randomness may not be distributed
    uniformly over the bits.

*   Save the wrapped (encrypted) post encryption key in the database. When
    decrypting messages, the code should derive KEK from the mater key and
    salt, and then decrypt the post encryption key, not loading the Python
    object where key has been unwrapped. As we process files, we would store
    filenames, instead of FILE structures, in database.

The information saved the database is sufficient to decrypt posts. If
decryption fails, write warning messsages and the JSON string to console. This
is for debugging purposes. 

## Deliverables

### Report

Write a report that documents your work, describes your findings, and explains
your design and code. Submit the report in PDF in HuskyCT. 

### Video. 

Make a short video (less than 5 minutes), which include the following. 

1.  Explain the code that encrypt/decrypt posts.

2.  Demo with two users that they can encrypt posts and read encrypted posts after (and only
    after) log in. 

### Submission instructions

On the submission page, click "Write Submission" button next to "Text Submission". Paste
the link to your video in the box. Make sure the link is clickable. 

Attach the PDF file by clicking the "Browse Local Files" button.

Click the "Submit" button.

## Additional Resources

### Python Virtual Environments

Python 3 has built-in support for virtual environment. For example, the
instructions for managing virtual environments in Python 3.9 are on the
[this page](https://docs.python.org/3/tutorial/venv.html)

[Anaconda](https://docs.anaconda.com/anaconda/) is also a popular option that
relies on Conda. Some students may already have it installed.

### Handling Users

The following page discuss security issues in user management. Although we do
not work on user management, some of you may find it interesting and helpful.

[Explore Flask: Users](https://exploreflask.com/en/latest/users.html)

### PowerShell Script

Here is a PowerShell script that makes set up Flask easier. Change
the path to where Python virtual environment and Flask are installed.

```
Invoke-Expression ${home}\venv\Scripts\activate.ps1
$Env:FLASK_APP = "flaskr"
$Env:FLASK_ENV = "development"
pushd ${home}\git\flask\examples\tutorial
```

### Output of ae.py

Here is an example output of `ae.py`

```
# python ae.py
key in hex = 42afb55b4a9bdb94e80a7a269f7840a4
nouce in hex = e3a83636b250fbf1c987a96121
ciphertext raw bytes = b'\x96\xde5cz\x0c\xec\xe4\xbdJ@\xfc\xfd\xd7{\xb3\xbd\x12\xf6O\xfe\r\x01\xe7\x97\x90\x02\x1a\xab\x8d7\x89\x84\xc0[\xa7\xee>\x02\xf5\t'
ciphertext in hex = 96de35637a0cece4bd4a40fcfdd77bb3bd12f64ffe0d01e79790021aab8d378984c05ba7ee3e02f509
Plaintext' = This is a secret message.
wrapped_key in hex = 265a3d4112f20a48c557ec7dbcae940d6f425327494f54e2
derived key in hex = 5a59412a713567b4095fc65bb6e8e5f2
```
