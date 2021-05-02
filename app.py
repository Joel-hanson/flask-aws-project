import flask
import boto3

from flask import request, jsonify
from utils import get_instance_status, get_running_instances
app = flask.Flask(__name__)
app.config.from_pyfile("settings.py")

session = boto3.session.Session(region_name=app.config.get("DEFAULT_REGION"), profile_name=app.config.get("KEYNAME"))

new_instance_image_data = '''#!/bin/bash
set -e -x
sudo apt-get -y install
sudo apt-get -y upgrade

# Install docker
sudo apt-get -y install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
    "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get -y update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io supervisor

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose


# Install git and pull latest version of a docker project
sudo apt-get -y install git
git clone https://github.com/Joel-hanson/nginx-docker.git /tmp/nginx-docker

cd /tmp/nginx-docker
sudo cp supervisor.conf /etc/supervisor/conf.d/
sudo service supervisor restart
'''

custom_image_user_data = '''#!/bin/bash
set -e -x

git clone https://github.com/Joel-hanson/nginx-docker.git /tmp/nginx-docker

sudo service supervisor restart
'''

@app.route("/", methods=["GET"])
def home():
    return """
        <h3>
            Segmind Assignement
        </h3>
        <ul>
        <li>
            For creating a new instance please send a request to the API /api/create
        </li>
        <li>
            The status of the current instance can be fetched using the /api/status API
        </li>
        </ul>
    """


@app.route("/api/create", methods=["GET", "POST"], strict_slashes=False)
def create_instance():
    """
    This the api function which create a instance

    Request ARGS:
        instance_type:
            default: <instance type>
            Instance type

    Return:
        Acknoledgement response (JSON)
    """

    instance_type = request.args.get(
        "instance_type", app.config.get("DEFAULT_INSTANCE_TYPE")
    )
    use_custom_image = request.args.get(
        "use_custom_image", False
    )
    if use_custom_image:
        print("custom image")
        image_id = app.config.get("CUSTOM_IMAGE_ID")
        user_data = custom_image_user_data
    else:
        user_data = new_instance_image_data
        image_id = app.config.get("DEFAULT_IMAGE_ID")

    ec2_client = session.client("ec2", region_name=app.config.get("DEFAULT_REGION"))
    instances = ec2_client.run_instances(
        ImageId=image_id,
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        SecurityGroups=['default'],
        UserData=user_data,
        KeyName=app.config.get("KEYNAME"),
    )

    instance_id = instances["Instances"][0]["InstanceId"]
    return jsonify({"instance_id": instance_id})


@app.route("/api/status", methods=["GET"], strict_slashes=False)
def status_all():
    """
    This the api which returns that status of all the instances

    Request ARGS:
        intance_id:
            default: None
            The instance id 

    Return:
        Status of the instance or instances will be returned based on the request input response (JSON)
    """
    instance_id = request.args.get(
        "instance_id"
    )
    instances_status = get_instance_status(instance_id)
    return jsonify(instances_status)


app.run()
