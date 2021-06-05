#ifndef COMMUNICATIONTASK_H
#define COMMUNICATIONTASK_H

#include <Arduino.h>
#include <Task.h>
#include <TaskScheduler.h>
#include "CmdMessengerPC.h"

// Timed task to process the communications to the PC
class CommunicationTask : public TimedTask
{
public:
    // Create a new communication task with the activation rate.
    CommunicationTask(uint32_t _rate);

    // get the measured temperature
    float getMeasuredTemperature();

    virtual void run(uint32_t now);
    void setup(void);
    
private:
    uint32_t period;    // communication task activation period.
};


// constructor
CommunicationTask::CommunicationTask(uint32_t _period)
: TimedTask(millis()),
  period(_period)
{
}

float CommunicationTask::getMeasuredTemperature()
{
  float measuredTemperature;
  return measuredTemperature;
}

// comms setup
void CommunicationTask::setup(void)
{
  Serial.println(F("Setup in communications task started"));
  
  // Attach callback methods to handle communication of the Mega2560 with the PC
  CM_PC::attachCommandCallbacksPCComms();
    
  Serial.println(F("Setup in communications task done"));
}

void CommunicationTask::run(uint32_t now)
{
  // for the test of the serial interface only
  // CM_PC::testComms();

  // Process incoming serial data, and perform callbacks
  CM_PC::cmdMessengerPC.feedinSerialData();
  // CM_PC::testComms();

  // Run again in the required number of milliseconds.
  incRunTime(period);
}

#endif
