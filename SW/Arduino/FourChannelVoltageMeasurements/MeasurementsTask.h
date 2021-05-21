#ifndef MEASUREMENTSTASK_H
#define MEASUREMENTSTASK_H

#include <Arduino.h>
#include <Task.h>
#include <TaskScheduler.h>
// #include <OneWire.h>
// #include <DallasTemperature.h>
#include "Sample4ChannelVoltages.h"
#define MaxNoChannels 4

// global variable for the data exchange with the communication task
volatile float g_measuredVoltages[MaxNoChannels];
float *voltages;

// The 4-channel voltage sample interface
Sample4ChannelVoltage voltagesSampler();


// Timed task to do the temperature measurements
class MeasurementsTask : public TimedTask
{
public:
    // Create a new communication task with the activation rate.
    MeasurementsTask(uint32_t _rate);

    void getMeasurementValues(void);
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
void MeasurementsTask::getMeasurementValues(void)
{
  for(uint8_t k = 0; k < MaxNoChannels; k++)
     g_measuredVoltages[k] = voltages[k];
}

// comms setup
void MeasurementsTask::setup(void)
{
  Serial1.println("Setup in MeasurementsTask task started");
  
  // setup the voltages sampler
  voltagesSampler.setup();
  
  Serial1.println("Setup in MeasurementsTask task done");
}

void MeasurementsTask::run(uint32_t now)
{
  // get the measurement value
  voltagesSampler.getSamples();
  voltages = voltagesSampler.returnSamples();
  getMeasurementValues();
  
  // Run again in the required number of milliseconds.
  incRunTime(period);
}

#endif
