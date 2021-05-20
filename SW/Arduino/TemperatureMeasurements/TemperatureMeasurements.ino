/* Sketch to measure temperature and communicate the values to the PC via
 * CmdMessenger
 *
 *
 * @author: Dr. Markus Reinhardt, 30th March 2021
 *
 */

#include <Arduino.h>
#include <BlinkerTask.h>
#include "CommunicationTask.h"
#include "MeasurementsTask.h"

#define BlinkerPeriod 1000
#define CommsPeriod 1000         // period between the activations of the communication task in milliseconds
#define MeasurementsPeriod 1000 // period between the activations of the measurements task in milliseconds

BlinkerTask blinker(LED_BUILTIN, BlinkerPeriod);
CommunicationTask comms(CommsPeriod);
MeasurementsTask measurements(MeasurementsPeriod);

// the initial program setup
void setup()
{
  // start the serial port for the CmdMessenger interface
  Serial.begin(9600);

  // start the debug serial port
  Serial1.begin(9600);

  // setup the communication task
  comms.setup();
}

// the loop to start all tasks and to run the task scheduler (never returns)
void loop()
{
    // Initialise the task list and scheduler.
    // Task *tasks[] = {&blinker, &keyboardHandler, &measurements, &smpsControl};
    Task *tasks[] = {&blinker, &comms, &measurements};
    TaskScheduler sched(tasks, NUM_TASKS(tasks));

    // Run the scheduler - never returns.
    sched.run();
}
