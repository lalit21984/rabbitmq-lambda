import cfnresponse
import boto3
import json
import os
import requests
import logging

secret_client = boto3.client('secretsmanager')
logging.basicConfig(level=logging.INFO)

def handler(event, context):
  # Print event and context to allow manual success or failure reporting
  print(event)
  print(context.log_stream_name)
  
  if event["RequestType"] in ["Create", "Update"]:
    try:
      # Grab config file and env variables

      config_path = os.environ['LAMBDA_TASK_ROOT'] + "/rabbit_config_" + os.environ['ENVIRONMENT'] + ".json"
      json_config = json.loads(open(config_path).read())
      secret_arn = os.environ['SECRET_ARN']
      rabbit_endpoint = os.environ['RABBIT_ENDPOINT']
      print ('inside Create-Update loop')

      # Get secret from secrets manager
      response = secret_client.get_secret_value(SecretId=secret_arn)
      print ('secret retrival success')
      # Send config file to RabbitMQ api
      requests.post(url="https://" + rabbit_endpoint + "/api/definitions", json=json_config, auth=('rabbit-admin', response['SecretString']))
      print ('Print updated RabbitMQ Definitions')
      requests.post(url="https://" + rabbit_endpoint + "/api/definitions", json=json_config, auth=('rabbit-admin', response['SecretString']))

      # Report success
      cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
      print ('post cfnresponse command ')
    except Exception as e:
      response.error(str(e))
      # Log error and report failure
      logging.exception("Failed to configure RabbitMQ")
      print ('report failed')
      cfnresponse.send(event, context, cfnresponse.FAILED, {})

  elif event["RequestType"] == "Delete":
    # Do nothing on delete except report success
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {})


