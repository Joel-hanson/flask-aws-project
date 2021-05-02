## Requirements

1. Python (3.6, 3.7, 3.8, 3.9)
2. boto3 (1.12.39)
3. flask (1.1.2)

## Get started

Step 1: Install requirements

`pip install -r requirements.txt`

Step 2: Run the app

`python app.py`

## How to run
- You sould have configured the AWS `access_key` and `secret_key`
- In the current project I have set a AWS profile and using that profile we are making session to run the boto3 actions.

#### AWS configurations
- The app is configured to run all the instances in the region us-west-2
- The default server is t2.micro

#### How to create instances
1. The API to create the instance is at `/api/create`
2. The `instance_type` parameter can be passed to spin up instance with the given instance_type
3. The `use_custom_image` parameter can passed to spin up a custom image to spin up the image having docker

#### How to get status of the instances
1. The API to get the status of the instance is at `/api/status`
2. The parameter `instance_id` can be passed to get he status of a particular instance

#### How to create key pair using boto3
1. There is a function in utils.pt `create_key_pair` to create the key pair
