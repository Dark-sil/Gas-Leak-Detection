#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Servo.h> // Include the Servo library
#include <Wire.h>  // Include the Wire library for I2C devices

// Wi-Fi credentials
const char *ssid = "Ankan's S20 FE";
const char *password = "entq3186";

// Server details
const char *serverAddress = "http://192.168.200.3:8000";
WiFiClient wifiClient;

// Servo configuration
Servo myservo;
const int servoPin = D1; // Pin to which the servo is connected

// MQ-135 sensor configuration
const int mq135SensorPin = A0;              // Pin to which the MQ-135 sensor is connected
const unsigned long requestInterval = 5000; // Interval between requests (milliseconds)
unsigned long lastRequestTime = 0;

// URL parameters
const char *urlParametersGasValue = "?gasvalue=";
const char *urlParameterValveStatusRead = "&valvestatusread=true";
const char *urlParameterValveStatus = "&valvestatus=";
const char *urlParameterManualOverrideRead = "&manualoverrideread=true";

void setup()
{
    myservo.attach(servoPin);   // Attach servo to the specified pin
    Serial.begin(9600);         // Start serial communication
    WiFi.begin(ssid, password); // Connect to Wi-Fi network
}

void loop()
{
    unsigned long currentTime = millis();

    if (currentTime - lastRequestTime >= requestInterval)
    {
        lastRequestTime = currentTime;

        if (WiFi.status() == WL_CONNECTED)
        {
            HTTPClient http;
            int mq135Value = analogRead(mq135SensorPin); // Read value from the MQ-135 sensor

            // Construct the URL with the gas value
            char url[100];
            sprintf(url, "%s%d%s", serverAddress, mq135Value, urlParametersGasValue);
            strcat(url, urlParameterValveStatusRead);

            // Send HTTP GET request
            http.begin(wifiClient, url);
            int httpCode = http.GET();

            if (httpCode > 0)
            {
                String payload = http.getString();
                Serial.println(payload);

                if ((payload == "1") || (mq135Value > 710))
                {
                    myservo.write(90); // Open the valve
                    sprintf(url, "%s%d%s", serverAddress, 1, urlParameterValveStatus);
                    http.begin(wifiClient, url);
                    httpCode = http.GET();
                }
                else
                {
                    sprintf(url, "%s%s%s", serverAddress, urlParameterManualOverrideRead, urlParameterValveStatus);
                    http.begin(wifiClient, url);
                    httpCode = http.GET();

                    if (httpCode > 0)
                    {
                        String payload1 = http.getString();
                        if (payload1 == "0")
                        {
                            myservo.write(0); // Close the valve
                            sprintf(url, "%s%d%s", serverAddress, 0, urlParameterValveStatus);
                            http.begin(wifiClient, url);
                            httpCode = http.GET();
                        }
                    }
                }
            }
            else
            {
                Serial.printf("HTTP request error: %s\n", http.errorToString(httpCode).c_str());
            }

            http.end(); // Close the connection
        }
    }
}
