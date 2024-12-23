#include <Keypad.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <Preferences.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const String host = "http://rnbfm-45-9-29-243.a.free.pinggy.link";
const String id = "1";
const String ip = "78.59.214.159";

const char* ssid = "Wokwi-GUEST";
const char* password = "";

void fetchData() {
  HTTPClient http;
  String url = host + "/api/locks/" + id + "/" + ip;
  // Replace with your example URL
  
  Serial.println("Starting HTTP request...");
  
  http.begin(url); // Start the HTTP request
  
  int httpCode = http.GET(); // Send GET request
  
  if (httpCode > 0) {
    String payload = http.getString(); // Get the response payload
   
    // You can process the payload here, for example, store it in preferences
  } else {
    // Provide more detailed error information
  
    String errorMessage = http.errorToString(httpCode); // Get the error message corresponding to the status code
    Serial.print("Error message: ");
    Serial.println(errorMessage);
    
    if (httpCode == -1) {
      Serial.println("Possible cause: Network issues, ngrok connection expired or not accepting connections.");
    }
  }
  
  http.end(); // End the HTTP request
}



int postData(String data) {
  HTTPClient http;

  // URL components
  String apiPath = "/api/locks/unlock/";
  String url = host + apiPath + id + "/" + ip;


  http.begin(url); // Start the HTTP request

  // Send the data to the server
  http.addHeader("Content-Type", "application/json");
  String jsonData = "{\"access_key\": \"" + data + "\"}"; // Creating the payload with the key "access_key"
  int httpCode = http.POST(jsonData); // Send POST request

  if (httpCode > 0) {
    String payload = http.getString(); // Get the response payload


    // Parse the JSON response
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.print("JSON deserialization failed: ");
      Serial.println(error.c_str());
      return -1; // Return error code
    }

    // Extract the status from the response
    int status = doc["status"];

    return status; // Return the status as integer
  } else {
    // Provide detailed error information
    Serial.print("HTTP request failed. Status code: ");
    Serial.println(httpCode);
    String errorMessage = http.errorToString(httpCode); // Get the error message corresponding to the status code
    Serial.print("Error message: ");
    Serial.println(errorMessage);
    return -1; // Return error code
  }

  http.end(); // End the HTTP request
}


void notifyHumidity(String data) {
  HTTPClient http;

  // URL components
  String apiPath = "/api/humidity/";
  String url = host + apiPath + id;



  http.begin(url); // Start the HTTP request

  // Send the data to the server
  http.addHeader("Content-Type", "application/json");
  String jsonData = "{\"value\": \"" + data + "\"}"; // Creating the payload with the key "access_key"
  int httpCode = http.POST(jsonData); // Send POST request

  if (httpCode > 0) {
    String payload = http.getString(); // Get the response payload


    // Parse the JSON response
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.print("JSON deserialization failed: ");
      Serial.println(error.c_str());
    }

    // Extract the status from the response
    int status = doc["status"];

  } else {
    // Provide detailed error information
    Serial.print("HTTP request failed. Status code: ");
    Serial.println(httpCode);
    String errorMessage = http.errorToString(httpCode); // Get the error message corresponding to the status code
    Serial.print("Error message: ");
    Serial.println(errorMessage);
  }

  http.end(); // End the HTTP request
}


void setupWIFIConnection(){

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }
  Serial.println("Connected!");

  // Print the ESP32's IP address
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}