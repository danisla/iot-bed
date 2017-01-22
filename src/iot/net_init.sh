#!/bin/bash
until /usr/bin/curl -sf -o /dev/null http://status.aws.amazon.com/data.json; do echo "Waiting for network.."; sleep 5; done
