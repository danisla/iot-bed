# AWS IoT Device for Serta MP III BLE Bed

Set environment variables:

```
export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
export AWS_DEFAULT_REGION=us-east-1
export IOT_ENDPOINT=$(aws iot describe-endpoint | jq -r '.endpointAddress')
export THING_NAME=iot-bed
```

Create the certificates:

```
CERT_ARN=$(aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile device.pem \
  --public-key-outfile device.pub \
  --private-key-outfile device-key.pem | jq -r '.certificateArn')
```

Create the IoT Thing:

```
THING_ARN=$(aws iot create-thing \
  --thing-name "${THING_NAME}" | jq -r '.thingArn')
```

Connect certificate to thing:

```
aws iot attach-thing-principal \
  --thing-name "${THING_NAME}" \
  --principal "${CERT_ARN}"
```

Create the policy:

```
aws iot create-policy \
  --policy-name "${THING_NAME}" \
  --policy-document '{"Version":"2012-10-17","Statement":[{"Action":"iot:*","Resource":"*","Effect":"Allow"}]}'
```

Attach the policy:

```
aws iot attach-principal-policy \
  --principal "${CERT_ARN}" \
  --policy-name "${THING_NAME}"
```

Download the root cert:

```
curl -o root-CA.crt https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem
```

The code that connects to this shadow is in the [`src/iot`](../src/iot) directory.

Next we create a [Lambda function that will update the thing shadow.](./04_LAMBDA_SHADOW.md)