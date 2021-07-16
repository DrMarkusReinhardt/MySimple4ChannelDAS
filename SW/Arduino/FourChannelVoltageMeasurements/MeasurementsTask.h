#ifndef MEASUREMENTSTASK_H
#define MEASUREMENTSTASK_H

#include <Arduino.h>
#include <Task.h>
#include <TaskScheduler.h>

#include "Sample4ChannelVoltages.h"
#include "Handle4ChannelSwitches.h"

#define MaxNoChannels 4

// global variable for the data exchange with the communication task
volatile float g_measuredVoltages[MaxNoChannels];
volatile int g_switchStatus[MaxNoChannels];
float *voltages;
int *switches;

// The 4-channel voltage sample interface
Sample4ChannelVoltages voltagesSampler;

// the 4-channel switch handler interface
Handle4ChannelSwitches switchesHandler;

// Timed task to do the temperature measurements
class MeasurementsTask : public TimedTask
{
public:
    // Create a new communication task with the activation rate.
    MeasurementsTask(uint32_t _rate);

    void storeMeasurementValues();
    void storeSwitchValues();
    void setup(void);
    virtual void run(uint32_t now);
    
private:
    uint32_t period;    // communication task activation period.
};

// constructor
MeasurementsTask::MeasurementsTask(uint32_t _period)
: TimedTask(millis()),
  period(_period)
{
}

// store the measured voltages
void MeasurementsTask::storeMeasurementValues()
{
  for(uint8_t k = 0; k < MaxNoChannels; k++)
     g_measuredVoltages[k] = voltages[k];
}

// store the status of the switches
void MeasurementsTask::storeSwitchValues()
{
  for(uint8_t k = 0; k < MaxNoChannels; k++)
  {
     g_switchStatus[k] = switches[k];
  }
  /*
  Serial.println("Global status of switches:");
  Serial.print("SW 0: ");Serial.print(g_switchStatus[0]);
  Serial.print(", SW 1: ");Serial.print(g_switchStatus[1]);
  Serial.print(", SW 2: ");Serial.print(g_switchStatus[2]);
  Serial.print(", SW 4: ");Serial.println(g_switchStatus[3]);
  */
}


// comms setup
void MeasurementsTask::setup(void)
{
  Serial.println(F("Setup in MeasurementsTask task started"));
  
  // setup the voltages sampler
  voltagesSampler.setup();
  
  Serial.println(F("Setup in MeasurementsTask task done"));
}

void MeasurementsTask::run(uint32_t now)
{
  // get the voltage measurements
  voltagesSampler.getSamples();                      // sample the voltages
  voltages = voltagesSampler.returnSamples();        // return the measured voltages
  storeMeasurementValues();                          // store the measured voltages in the global variable
  
  // get the status of the switches 
  switchesHandler.getSwitchStatus();                  // sample the status of the switches
  switches = switchesHandler.returnSwitchStatus();    // return the status of the switches
  storeSwitchValues();                                // store the status of the switches
  
  // Run again in the required number of milliseconds.
  incRunTime(period);
}

#endif
