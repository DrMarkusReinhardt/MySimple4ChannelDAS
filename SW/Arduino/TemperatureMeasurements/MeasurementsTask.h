#ifndef MEASUREMENTSTASK_H
#define MEASUREMENTSTASK_H

#include <Arduino.h>
#include <Task.h>
#include <TaskScheduler.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// Data wire is connected to the Arduino digital pin 4
#define ONE_WIRE_BUS 4

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas temperature sensor 
DallasTemperature sensor(&oneWire);

// global variable for the data exchange with the communication task
volatile float g_measuredTemperature;   

// Timed task to do the temperature measurements
class MeasurementsTask : public TimedTask
{
public:
    // Create a new communication task with the activation rate.
    MeasurementsTask(uint32_t _rate);

    float getMeasurementValue(void);
    void setup(void);
    virtual void run(uint32_t now);
    
private:
    uint32_t period;    // communication task activation period.
    float temperatureValue;
};

// constructor
MeasurementsTask::MeasurementsTask(uint32_t _period)
: TimedTask(millis()),
  period(_period)
{
}

// get the temperature value
float MeasurementsTask::getMeasurementValue(void)
{
  // Call sensor.requestTemperatures() to issue a global temperature and requests to all devices on the bus
  sensor.requestTemperatures();

  // get the value
  temperatureValue = sensor.getTempCByIndex(0);
  
  Serial1.print("Celsius temperature: ");
  // Why "byIndex"? You can have more than one IC on the same bus. 0 refers to the first IC on the wire
  Serial1.println(temperatureValue); 

  return temperatureValue;
}

// comms setup
void MeasurementsTask::setup(void)
{
  Serial1.println("Setup in MeasurementsTask task started");
  
  // Start up the sensor measurement
  sensor.begin();
  
  Serial1.println("Setup in MeasurementsTask task done");
}

void MeasurementsTask::run(uint32_t now)
{
  // get the measurement value
  g_measuredTemperature = getMeasurementValue();
  
  // Run again in the required number of milliseconds.
  incRunTime(period);
}

#endif
