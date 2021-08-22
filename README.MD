## Key-Value Store

RESTFul API implementing a store and some user management.

## Installation

1. Install requirements inside a python3 virtualenv `python3 -m venv venvv`
2. Activate the venv :
`source venv/bin/activate`
3. Install requirements :
`pip3 install -r requirements.txt`

## Coverage

The tests cover the following cases :
1. Create user + verification that it is not possible to create another user with the same username
2. Retrieve user
3. Modify user
4. Delete user
5. Verification that we cannot create a user with a username longer than the system limit (KEY_MAXIMUM_LENGTH)
6. Task creation + verification of credits exhaustion (cannot create more tasks than the limit)
7. Access to global metrics by super admin
8. Access to my own metrics
9. Access to any user metrics by the admin
10. Get top 10 users by number of tasks

## Usage
Launch the server using 
`python3 main.py`

#### REST API for user management access by admin
1. POST `/users` `{"username":"username", "password":"password", "credits":10}`
2. PATCH `/users/<username>` `{"username":"username", "credits":10}`
3. DELETE `/users/<username>`
4. GET `/users/<username>`
5. GET `/users`
6. GET `/metrics`
7. GET `/top_metrics`
8. GET `/metrics/<username>`

#### REST API for regular users

1. GET `/metrics/<username>`
2. POST `/tasks` `{"completed" : false}`


## Implementation details

1. The API is implemented using the python framework FastAPI
2. User and their tasks are stored inside a Singleton class (see the file `models.py`)
3. User authentication is performed through a X-Token header of the http request.
   1. Admin user is not stored but is recognized through the use of the token `super_admin`
   2. Other users are stored and recognized through the user of a token `<username>`

## Limitations

1. The test depend on each other
2. Bonuses were not implemented
3. Deletion of task is not implemented
4. Allow credit over-provisioning --> Not implemented
5. Total number of objects limits is implemented only ony the tasks
6. Concurrent access is not well tested and might cause bugs, singleton and locks are implemented though