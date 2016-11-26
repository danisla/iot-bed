# AWS Lambda Function to update IoT Thing Shadow

This lambda function will be called by the Alexa Skills SDK after the voice intent has been processed in the AVS model. Based on the incoming intent, the function will update the device shadow `desired` state which will notify the conroller via MQTT.

## Creating the Lambda Function from the CLI
Set environment variables:

```
export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
export AWS_DEFAULT_REGION=us-east-1
```

> NOTE: alexa skills with lambda must be created in the us-east-1 region.

```
export ROLE_NAME=iot-bed-lambda-exec
export FUNCTION_NAME=iot-bed-action
```

Create an execution role:

```
ROLE_NAME=iot-bed-lambda-exec
ASSUME_ROLE_POLICY='{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}'
ROLE_ARN=$(aws iam create-role \
  --role-name "${ROLE_NAME}" \
  --assume-role-policy-document "${ASSUME_ROLE_POLICY}" | jq -r '.Role.Arn')
```

Attach policy to role that allows it to update the shadow:

```
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/AWSIoTDataAccess
```

Update the source with your IoT endpoint.

```
IOT_ENDPOINT=$(aws iot describe-endpoint | jq -r '.endpointAddress')
sed -i -e s/YOUR_IOT_ENDPOINT/$IOT_ENDPOINT/g src/lambda/lambda_function.js
```

Create lambda code zip file:

```
cd src/lambda
zip code.zip *
```

Create the lambda function:

```
aws lambda create-function \
  --function-name "${FUNCTION_NAME}" \
  --runtime nodejs4.3 \
  --role "${ROLE_ARN}" \
  --handler index.handler \
  --timeout 5 \
  --publish \
  --region us-east-1 \
  --zip-file fileb://code.zip
```

In the Lambda console, you must add the `Alexa Skills Kit` trigger to the lambda function before it can be used with the Alexa Skill.

## References

- [Alexa Smart Home Skills API](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference)
