# Secure Authentication and Traceability of Physical Objects

## Overview
This project provides a framework for securely authenticating and tracking physical objects. It includes three main stages: 
- dataset creation, 
- enrolment, and
- authentication. 

## Requirements Installation
Before running the code, install the required dependencies:

```bash
pip install -r requirements.txt
```

## Dataset Creation
Update the `BASEPATH` in the `dataset_augmentation.py`, then run the code to create the dataset.

## Running the Code
### Vendor Setup
- If a new `server`, you should run the following command line on your terminal. With these command line, the DB is reset and all saved entries are deleted. 
```bash
python3 python/vendor.py <PORT> new
```  
- To run the vendor process without resetting the database, preserving existing entries:
```bash
python3 python/vendor.py <PORT> add
``` 

### Enrolment
Start the enrolment process using the command below. This step is required before authentication can be tested.
```shell
python3 python/enroll.py <PORT>
```

### Authentication
After completing the enrolment process, test the authentication performance with the following command:
```shell
python3 python/authenticate.py <PORT> 
```

## Notes
- Replace <PORT> with the actual port number where the server is running.
- Ensure all dependencies and prerequisites are installed before running the scripts.