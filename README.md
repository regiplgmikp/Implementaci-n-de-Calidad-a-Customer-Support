# Customer_Support
A place to upload the customer support project for the course "Bases de datos no relacionales" at ITESO.

### Setup a python virtual env with python requirements
```
# If pip is not present in you system
sudo apt update
sudo apt install py-pip

# Install and activate virtual env (Linux/MacOS)
py -m pip install virtualenv
py -m venv ./venv
source ./venv/bin/activate

# Install and activate virtual env (Windows)
py -m pip install virtualenv
py -m venv ./venv
.\venv\Scripts\Activate.ps1

# Install project python requirements
pip install -r requirements.txt
```

### Launch Databases containers
Ensure you have a running Mongodb, Dgraph and Cassandra instance
i.e.:
```
docker run --name Customer_Support_Mongodb -d -p 27017:27017 mongo
docker run --name Customer_Support_Dgraph -d -p 8080:8080 -p 9080:9080  dgraph/standalone
docker run --name Customer_Support_Cassandra -p 9042:9042 -d cassandra

```
