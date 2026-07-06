# Coins API

The coins API is an API that returns apprenticeship coins, and allows them to be marked as complete to track progress against the standard

<!-- what else does it do? placeholder -->

## Running/testing locally

### Prerequisites

Requires python 3.12 and pip package manager

### Setting up the environment

Clone this repository and navigate to the project root:

```bash
git clone https://github.com/joerawnsley/coins_api.git
cd coins_api
```

Create a virtual environment by running the following command from the project root directory

`python3 -m venv .venv`

Activate the virtual environment

` source .venv/bin/activate`

Install the requirements

`pip install -r requirements.txt`

Create a .env file in the project root, and paste in the following text, replacing the values for DB_HOST and DB_PASSWORD with your connection string and password:

```
DB_HOST=[your Digital Ocean connection string]
DB_PASSWORD=[your Digital Ocean DB passowrd]
DB_LOCATION=remote
REMOTE_SCHEMA=prod
DB_LOGGING=off
```

- DB_LOCATION can be set to 'local' allowing you to run the tests against a local sqlite database for speed, or 'remote', allowing you to use your hosted cloud database
- REMOTE_SCHEMA can be 'test' or 'prod'. If DB_LOCATION is 'remote', 'test' will let you run automated tests against the cloud database, while 'prod' will let you run the server and send requests manually
- DB_LOGGING= can be 'on' to show detailed database query logging during tests, 'off' to not show

### Running the tests

To run the tests, ensure REMOTE_SCHEMA is set to `test` in you .env file. Run

`pytest`

in the terminal.

- Do not run tests when remote schema is set to 'prod'
- DB_LOCATION in the .env file can be set to 'local' allowing you to run the tests against a local sqlite database for speed, or 'remote', allowing you to run the same tests using your hosted cloud database

Overall test coverage is 96%. To check coverage, run ```pytest --cov``` from the project root.

### Running the server

If you want to add some coins and duties to the database in order to test manually, you can add them (if they haven't already been added) by running the following command from the project root:

`python3 seed_prod_db.py`

**Note: The above command will overwrite any coins and duties currently in the database, and remove any associations between coins and duties**. You'll need to link coins and duties using the API - see instructions below.

The app uses port 8000. To start a local server, run:

`fastapi dev src/app.py`

You will get a link to the application running on localhost:8000. You can view auto-generated API documentation detailing availble endpoints by clicking the second link (localhost:8000/docs) There is also information about API endpoints and usage below.

## Deployment

The Coins API is automatically deployable on AWS using terraform. If you would like to deploy the API in this way, first complete the pre-requisites.

### Pre-requisites

1. Get the app running locally (see above)
2. Install Terraform (version 14.6 used for testing)
3. Have an AWS account
4. Sign into your AWS account via the AWS CLI

### Building the infrastructure

Once you have installed Terraform and authenticated using the AWS CLI, apply the terraform in the infrastructure directory:

```bash
cd infrastructure
terraform apply
```

Check the plan, and type `yes` to accept.

### Deploying the code

Once you have successfully built the infrastructure, there are two ways to deploy the API:

1. Deploy on push:
    - commit and push a change to the repo, and it will deploy automatically
2. Deploy manually on Github:
    - open the Github repository in your browser, and click the "Actions" tab.
    - In the left sidebar, click "build and deploy"
    - in the blue horizontal bar, click "Run worklfow"
    - ensure the "main" branch is selected, then click "Run Workflow"

### Getting the public IP

In the project root, run the folowing commands in the terminal:

```
chmod +x get-public-ip.sh
```

then

```
./get-public-ip.sh
```

The public IP should appear in your terminal

*Note: if you have recently deployed the app, wait for the deployment to complete before attempting to get the public IP. This can take up to 10 minutes.*

## Endpoints

Once the app is deployed or running locally, API calls are made to

```
http://<IP address>:8000/<endpoint>
```

for example, if your IP address is 127.0.0.1, send a request to:

`http://127.0.0.1:8000/` for the welcome page, or

`http://127.0.0.1/coins/automate` for the automate coin details.

The following endpoints are available:

### GET endpoints

- `/` returns a welcome message
- `/coins` returns a list of all coins
- `/coins/<coin_path>` returns information about a specific coin. Coin path are a shortened form of a coin's name. List all coins to see the available coin paths
- `/duties` returns a listof all duties
- `/duties/<duty_number>` returns information about a specific duty
- `/coins/<coin_path>/list-duties` returns a list of duties associated with the specified coin, with full duty details including descriptions

### POST endpoints

- `/coins` creates a new coin. Pass in the coin as JSON in the request body. For example:

    ```
        # POST request body:
        {
            "coin_name": "Going Deeper",
            "coin_path": "deeper"
        }
    ```

    The following fields are available:
    - "coin_name": (string, required)
    - "coin_path": (string, required, must be unique)
    - "duties": (list of integers, optional, must reference duties currently in the database by their duty_number)
    - "is_complete": (boolean, defaults to false if omitted)

- `/duties` creates a new duty. Pass in the duty as JSON in the request body. For example:

    ```
    # POST request body
    {
        "duty_number": 1,
        "description": "Script and code"
    }
    ```

    Only two fields are available:
    - "duty_number": (integer, required, must be unique)
    - "description": (string, required)

### PUT Endpoints

Used to update the properties of a coin or duty, or add a duty to a coin. Make a call to the coin's *path* - the shortened form of its name

- `/coins/<coin_path>/add-duties`: add one or more duties, passed in as an array (list) of integers representing duty numbers in the request body. A duty must exist in the database for each number in the array. For example:
     ```
    # endpoint
    /coins/houston/add-duties

    # request body
    [5, 7, 10]    
    ```
    will add duties 5, 7 and 10 to the *Houston, Prepare to Launch* coin, provided all of the duties exist in the database.

- `/coins/<coin_path>/remove-duties` works the same way as ```add-duties```. Duties to be removed from a coin can be passed in through the request body as an array (see *add-duties,* above)
- `/coins/<coin_path>/mark-complete` marks a coin as completed. Specify the coin by its *coin_path* in the endpoint url
- `/coins/<coin_path>/mark-incomplete` marks a coin as not completed. Specify the coin by its *coin_path* in the endpoint url
- `/duties/<duty_number>/update` update a duty's description. Specify the number of an existing duty in the endpoint url. Pass in the new description as the "desctiption" field in a JSON object in the request body. For example:
    ```
    # endpoint url
    /duties/1/update

    # request body
    {
        "description": "Follow test driven development and ensure appropriate test coverage"
    }

*Note: Duty descriptions can be update, but not their numbers.*

### DELETE endpoints

- ```/coins/<coin_path>``` the coin with the specified *coin_path* will be permanently deleted from the database

*Note: Duties cannot be deleted*

## Note on error handling and validation

The coins API validates that coin names, coin paths (the shortened form of a coin name) and duty numbers are unique, so duplicates cannot be created. But invalid inputs are not yet handled cleanly, so the following issues exist:

- Attempting to create a duplicate duty results in "Internal Server Error" rather than an informative error message
- Attempting to reference a coin or duty hat doesn't exist in a GET or PUT request results in "Internal Server Error" rather than an informative error message
- Attempting to DELETE a coin or duty that doesn't exist returns a "deleted" message, even though nothing was deleted
- There is no validation on coin paths other than uniqueness, So it's possible to create a coin with any arbitrary string as its path. This could cause problems, for exampe a coin path might be created with spaces in its path, making it difficult to access
- There might be other, similar, error handling and validation issues

These problems have been thought about and will be prioritised in the next update, but I haven't had time to properly test and implement the solution yet.