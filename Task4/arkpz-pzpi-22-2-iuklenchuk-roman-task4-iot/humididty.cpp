#include <Arduino.h>  

float humidityReadings[10];  // Array for 10 humidity readings
int humidityIndex = 0;

unsigned long lastHumidityTime = 0;  // Time tracker for humidity check
const unsigned long humidityInterval = 2000;  // Interval for humidity check (2 seconds)

void notifyHumidity(String data);
void check_humidity() {
  // Generate a random humidity from 30% to 90%
  float humidity = random(30, 91);  // Humidity range from 30% to 90%

  // Save the value in the array
  humidityReadings[humidityIndex] = humidity;
  humidityIndex = (humidityIndex + 1) % 10;  // Overwrite the array with a cyclic shift

  // Calculate the average humidity
  float averageHumidity = 0;
  for (int i = 0; i < 10; i++) {
    averageHumidity += humidityReadings[i];
  }
  averageHumidity /= 10;

  // Determine the minimum and maximum humidity
  float minHumidity = humidityReadings[0];
  float maxHumidity = humidityReadings[0];
  for (int i = 1; i < 10; i++) {
    if (humidityReadings[i] < minHumidity) minHumidity = humidityReadings[i];
    if (humidityReadings[i] > maxHumidity) maxHumidity = humidityReadings[i];
  }

  // Notify user if humidity is too low or high
  if (humidity < 30) {
    notifyHumidity("Рівень вологості занизький!");
  } else if (humidity > 70) {
    notifyHumidity("Рівень вологості зависокий");
  }

  // Send data to the monitor
  Serial.print("Current humidity: ");
  Serial.println(humidity);
  Serial.print("Average humidity: ");
  Serial.println(averageHumidity);
  Serial.print("Minimum humidity: ");
  Serial.println(minHumidity);
  Serial.print("Maximum humidity: ");
  Serial.println(maxHumidity);
}
