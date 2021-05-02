from os import environ

# SECRET_KEY = environ.get('SECRET_KEY')
# API_KEY = environ.get('API_KEY')
DEBUG = environ.get("API_KEY")
DEFAULT_REGION = "us-west-2"
DEFAULT_IMAGE_ID = "ami-0ca5c3bd5a268e7db"
CUSTOM_IMAGE_ID = "ami-0baa8a6f229480332"
DEFAULT_INSTANCE_TYPE = "t2.micro"
KEYNAME = "segmind-assignment-user"