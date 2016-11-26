/* eslint-disable  func-names */
/* eslint quote-props: ["error", "consistent"]*/

'use strict';

const Alexa = require('alexa-sdk');
const AWS = require('aws-sdk');

const config = {
    "APP_ID": undefined, // TODO replace with your app ID (OPTIONAL).
    "thingName": 'iot-bed',
    "endpointAddress": "a21frlxo8kxe8s.iot.us-east-1.amazonaws.com"
}

const iotdata = new AWS.IotData({endpoint: config.endpointAddress});

const setBedPreset = function(preset, cb) {
    iotdata.getThingShadow({
        thingName: config.thingName
    }, function(err, data) {
        if (err) {
            cb(err);
        } else {
            const update = {
                "state": {
                    "desired": {
                        "preset": preset
                    }
                }
            }
            iotdata.updateThingShadow({
                payload: JSON.stringify(update),
                thingName: config.thingName
            }, function(err, data) {
                if (err) {
                    cb(err)
                } else {
                    cb();
                }
            });
        }
    });
}

const setBedMassage = function(state, cb) {
    iotdata.getThingShadow({
        thingName: config.thingName
    }, function(err, data) {
        if (err) {
            cb(err);
        } else {
            const jsonPayload = JSON.parse(data.payload);

            var currVal;
            if (jsonPayload.state.reported === undefined || jsonPayload.state.reported.massage === undefined) {
              currVal = 0.0;
            } else {
              currVal = jsonPayload.state.reported.massage;
            }

            var update = {
                "state": {
                    "desired": {
                    }
                }
            }
            var newVal;

            if (state == "on") {
              newVal = Math.min((currVal + 25) % 100, 100);
            } else {
              newVal = currVal * -1
            }

            update.state.desired.massage = newVal;

            iotdata.updateThingShadow({
                payload: JSON.stringify(update),
                thingName: config.thingName
            }, function(err, data) {
                if (err) {
                    cb(err)
                } else {
                    cb();
                }
            });
        }
    });
}

const handlers = {
    'SetPreset': function () {
        const _this = this;
        const preset = this.event.request.intent.slots.Preset.value.toLowerCase();
        var speechOutput;
        var cardOutput = preset;
        var sendPreset = true;
        if (preset == "0g" || preset == "0 g") {
            speechOutput = "Welcome to Zero-G";
            cardOutput = "Zero-G";
        } else if (preset == "tv") {
          speechOutput = "Moving bed to TV preset";
        } else if (preset == "flat") {
            speechOutput = "Moving bed to flat preset";
        } else if (preset == "massage") {
          setBedMassage("on", function(err) {
              if (err) {
                  console.log(err);
                  _this.emit(':tell', "Sorry, I'm having trouble communicating with the bed right now.");
              } else {
                  speechOutput = "Enjoy your relaxing massage";
                  _this.emit(':tell', speechOutput);
              }
          });
          sendPreset = false;
        } else {
            speechOutput = "Sorry I don't know about the preset " + preset;
            _this.emit(':tellWithCard', speechOutput, "IoT Bed", "Could not find preset: " + preset);
            return;
        }

        if (!sendPreset) return;

        setBedPreset(preset, function(err) {
            if (err) {
                console.log(err);
                _this.emit(':tell', "Sorry, I'm having trouble communicating with the bed right now. ");
            } else {
                _this.emit(':tellWithCard', speechOutput, "IoT Bed", "Setting bed to " + cardOutput);
            }
        });
    },
    'SetMassage': function () {
        const _this = this;
        const state = this.event.request.intent.slots.State.value.toLowerCase();
        var speechOutput = "";

        if (state != "on" && state != "off") {
          speechOutput = "Sorry I don't know to set massage to " + state;
          _this.emit(':tellWithCard', speechOutput, "IoT Bed", "Could not set massage state: " + state);
          return;
        }

        setBedMassage(state, function(err) {
            if (err) {
                console.log(err);
                _this.emit(':tell', "Sorry, I'm having trouble communicating with the bed right now.");
            } else {
                if (state == "on") {
                    speechOutput = "Enjoy your relaxing massage";
                    _this.emit(':tell', speechOutput);
                }
            }
        });
    }
};

exports.handler = (event, context) => {
    const alexa = Alexa.handler(event, context);
    alexa.APP_ID = config.APP_ID;
    // alexa.resources = APP_RESOURCES;
    alexa.registerHandlers(handlers);
    alexa.execute();
};
