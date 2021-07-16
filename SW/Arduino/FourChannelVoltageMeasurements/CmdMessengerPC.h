#ifndef CMDMESSENGER_PC_H
#define CMDMESSENGER_PC_H

#include <Arduino.h>
#include <CmdMessenger.h>      // load CmdMessenger library
#include <Callback.h>
#include <SoftwareSerial.h>

extern volatile float g_measuredVoltages[];
extern volatile int g_switchStatus[];

extern SoftwareSerial SWSerial;

namespace CM_PC 
{

int seriesLength;
int seriesLengthCount;

float measuredTemperature = 0.0;

// Attach a new CmdMessenger object to the default Serial serial port to communicate with the PC via Arduino Monitor
char field_separator_PC   = ',';
char command_separator_PC = ';';
char escape_separator_PC  = '/';
CmdMessenger cmdMessengerPC = CmdMessenger(SWSerial, field_separator_PC, command_separator_PC,escape_separator_PC);
Signal<float> measuredTemperatureSignal;

// the following enum sequence has to correspond to the sequence of the enum in the Arduino part
// enums for the communication commands
enum
{
  // General commands
  kCommError                , // Command reports serial port comm error (only works for some comm errors)
  kComment                  , // Command to sent comment in argument
  
  // Setup connection test
  kAcknowledge              , // Command to acknowledge that cmd was received
  kAreYouReady              , // Command to ask if other side is ready
  kError                    , // Command to report errors
  
  // Acknowledge test
  kAskUsIfReady             , // Command to ask other side to ask if ready 
  kYouAreReady              , // Command to acknowledge that other is ready

  // send voltage measurements to the PC
  kSendMeasuredVoltage1     , // Command to send the measured voltage1 to the PC
  kSendMeasuredVoltage2     , // Command to send the measured voltage2 to the PC
  kSendMeasuredVoltage3     , // Command to send the measured voltage3 to the PC
  kSendMeasuredVoltage4     , // Command to send the measured voltage4 to the PC

  // send the status of the switches to the PC
  kSendSwitchChannel1       , // Command to send the status of the switch of channel1 to the PC
  kSendSwitchChannel2       , // Command to send the status of the switch of channel2 to the PC
  kSendSwitchChannel3       , // Command to send the status of the switch of channel3 to the PC
  kSendSwitchChannel4       , // Command to send the status of the switch of channel4 to the PC

  // turn on and off and reset the measurements
  kturnOnMeasurements       , // Command to turn on the measurements
  kturnOffMeasurements      , // Command to turn off the measurements
  kResetMeasurements        , // Command to reset the measurements

  // sent back a numeric value
  kFloatValue               , // Command to sent back a float value
  kInt16Value               , // Command to sent back a int16 value
  
  // Clear & Binary text data test
  kValuePing                , // Command to send value to other side
  kValuePong                , // Command to return value received with pong
  
  // Multiple Arguments test
  kMultiValuePing           , // Command to send values to other side
  kMultiValuePong           , // Command to return values received with pong
   
  // Benchmarks
  kRequestReset             , // Command Request reset
  kRequestResetAcknowledge  , // Command to acknowledge reset

  kRequestSeries            , // Command Request to send series in plain text
  kReceiveSeries            , // Command to send an item in plain text
  kDoneReceiveSeries,
        
  kPrepareSendSeries        , // Command to tell other side to prepare for receiving a series of text float commands
  kSendSeries               , // Command to send a series of text float commands
  kAckSendSeries            , // Command to acknowledge the send series of text float commands
};

// Needed for ping-pong function to exchange data with PC
enum
{
  kBool,
  kInt16,
  kInt32,
  kFloat,
  kFloatSci,
  kDouble,
  kDoubleSci,
  kChar,
  kString,
  kBBool,
  kBInt16,
  kBInt32,
  kBFloat,
  kBDouble,
  kBChar,
  kEscString,
};

void OnAcknowledgePC()
{
  cmdMessengerPC.sendCmd(kAcknowledge,F("to PC: ACK"));
}

void OnArduinoReadyPC()
{
  // In response to ping. We just send a throw-away acknowledgment to say "i'm ready"
  cmdMessengerPC.sendCmd(kAcknowledge,F("to PC: Arduino ready"));
}

void OnUnknownCommandPC()
{
  // Default response for unknown commands and corrupt messages
  cmdMessengerPC.sendCmd(kError,F("to PC: Unknown command"));
  cmdMessengerPC.sendCmdStart(kYouAreReady);  
  cmdMessengerPC.sendCmdArg(F("to PC: Command without attached callback"));    
  cmdMessengerPC.sendCmdArg(cmdMessengerPC.commandID());    
  cmdMessengerPC.sendCmdEnd();
}

void OnAskUsIfReadyPC()
{
  // The other side asks us to send kYouAreReady command, wait for acknowledge
  int isAck = cmdMessengerPC.sendCmd(kAreYouReady, F("Asking PC if ready"), true, kAcknowledge, 1000);
  
  // Now we send back whether or not we got an acknowledgments  
  cmdMessengerPC.sendCmd(kYouAreReady,isAck?1:0);
}

void OnSendMeasuredVoltage1ToPC()
{
  cmdMessengerPC.sendBinCmd(kFloatValue,g_measuredVoltages[0]);
}

void OnSendMeasuredVoltage2ToPC()
{
  cmdMessengerPC.sendBinCmd(kFloatValue,g_measuredVoltages[1]);
}

void OnSendMeasuredVoltage3ToPC()
{
  cmdMessengerPC.sendBinCmd(kFloatValue,g_measuredVoltages[2]);
}

void OnSendMeasuredVoltage4ToPC()
{
  cmdMessengerPC.sendBinCmd(kFloatValue,g_measuredVoltages[3]);
}

void OnSendSwitchStatusChannel1ToPC()
{
  cmdMessengerPC.sendBinCmd(kInt16Value,g_switchStatus[0]);
}

void OnSendSwitchStatusChannel2ToPC()
{
  cmdMessengerPC.sendBinCmd(kInt16Value,g_switchStatus[1]);
}

void OnSendSwitchStatusChannel3ToPC()
{
  cmdMessengerPC.sendBinCmd(kInt16Value,g_switchStatus[2]);
}

void OnSendSwitchStatusChannel4ToPC()
{
  cmdMessengerPC.sendBinCmd(kInt16Value,g_switchStatus[3]);
}

void OnTurnOnMeasurements()
{
  cmdMessengerPC.sendCmd(kAcknowledge,F("to PC: turn on measurements"));
}

void OnTurnOffMeasurements()
{
  cmdMessengerPC.sendCmd(kAcknowledge,F("to PC: turn off measurements"));
}

void OnResetMeasurements()
{
  cmdMessengerPC.sendCmd(kAcknowledge,F("to PC: reset measurements"));  
}

void OnValuePingPC()
{
   int dataType = cmdMessengerPC.readInt16Arg(); 
   switch (dataType) 
   {
      // Plain text
      case kBool:
      {
        bool value = cmdMessengerPC.readBoolArg();
       cmdMessengerPC.sendCmd(kValuePong, value);
        break;
      }
      case kInt16:
      {
        int value = cmdMessengerPC.readInt16Arg();
        cmdMessengerPC.sendCmd(kValuePong, value);
        break;
      }
      case kInt32:    
      {  
        long value = cmdMessengerPC.readInt32Arg();
        cmdMessengerPC.sendCmd(kValuePong, value);
        break;
      }
      case kFloat:
      {
         float value = cmdMessengerPC.readFloatArg();
         cmdMessengerPC.sendCmd(kValuePong, value);
         break;
      }
      case kDouble:
      {
         double value = cmdMessengerPC.readDoubleArg();
         cmdMessengerPC.sendCmd(kValuePong, value);
         break;
      }
      case kChar:    
      {  
        char value = cmdMessengerPC.readCharArg();
        cmdMessengerPC.sendCmd(kValuePong, value);
        break;
      }
      case kString:   
      {   
        char * value = cmdMessengerPC.readStringArg();
        cmdMessengerPC.sendCmd(kValuePong, value);
        break;
      }
      // Binary values
      case kBBool:
      {
         bool value = cmdMessengerPC.readBinArg<bool>();
         cmdMessengerPC.sendBinCmd(kValuePong, value);
         break;
      }
      case kBInt16:
      {
         int16_t value = cmdMessengerPC.readBinArg<int16_t>();
         cmdMessengerPC.sendBinCmd(kValuePong, value);
         break;
      }
      case kBInt32:
      {
         int32_t value = cmdMessengerPC.readBinArg<int32_t>();
         cmdMessengerPC.sendBinCmd(kValuePong, value);
         break;
      }
      case kBFloat:
      {
         float value = cmdMessengerPC.readBinArg<float>();
         cmdMessengerPC.sendBinCmd(kValuePong, value);
         break;
      }
      case kFloatSci:
      {
        float value = cmdMessengerPC.readFloatArg();
        cmdMessengerPC.sendCmdStart(kValuePong);
        cmdMessengerPC.sendCmdSciArg(value,2);
        cmdMessengerPC.sendCmdEnd();
         break;
      }
      case kBDouble:
      {
         double value = cmdMessengerPC.readBinArg<double>();
         cmdMessengerPC.sendBinCmd(kValuePong, value);
         break;
      }
      case kDoubleSci:
      {
        double value = cmdMessengerPC.readDoubleArg();
        cmdMessengerPC.sendCmdStart(kValuePong);
        cmdMessengerPC.sendCmdSciArg(value,4);
        cmdMessengerPC.sendCmdEnd();
       break;
      }
      case kBChar:    
      {  
         char value = cmdMessengerPC.readBinArg<char>();
         cmdMessengerPC.sendBinCmd(kValuePong, value);
         break;
      }
      case kEscString:   
      {   
        char * value = cmdMessengerPC.readStringArg();
        cmdMessengerPC.unescape(value);
        cmdMessengerPC.sendCmdStart(kValuePong);
        cmdMessengerPC.sendCmdEscArg(value);
        cmdMessengerPC.sendCmdEnd();
        break;
      }
      default: 
        cmdMessengerPC.sendCmd(kError,F("Unsupported type for valuePing!"));  
        break;
   }   
}

void OnMultiValuePingPC()
{  
   int16_t valueInt16 = cmdMessengerPC.readBinArg<int16_t>();  
   int32_t valueInt32 = cmdMessengerPC.readBinArg<int32_t>();  
   double valueDouble = cmdMessengerPC.readBinArg<double>();
   
   cmdMessengerPC.sendCmdStart(kMultiValuePong);
   cmdMessengerPC.sendCmdBinArg(valueInt16);
   cmdMessengerPC.sendCmdBinArg(valueInt32);
   cmdMessengerPC.sendCmdBinArg(valueDouble);
   cmdMessengerPC.sendCmdEnd();
}

//--------------- Benchmarks ----------------------
void OnRequestResetPC()
{
   seriesLengthCount = 0;
   cmdMessengerPC.sendCmd(kRequestResetAcknowledge,"");
}

// Callback function calculates the sum of the two received float values
void OnRequestSeriesPC()
{
  // Get series length from 1st parameter
  int seriesLength = cmdMessengerPC.readInt16Arg();
  float seriesBase = cmdMessengerPC.readFloatArg();
 
  // Send back series of floats
  for(int i=0;i< seriesLength;i++) {
     cmdMessengerPC.sendCmdStart (kReceiveSeries);
     cmdMessengerPC.sendCmdArg<float>(((float)i*(float)seriesBase),6);
     cmdMessengerPC.sendCmdEnd ();
  }
  cmdMessengerPC.sendCmd(kDoneReceiveSeries,"");
}

void OnPrepareSendSeriesPC()
{
  seriesLength      = cmdMessengerPC.readInt16Arg();
  seriesLengthCount = 0;
}

void OnSendSeriesPC()
{
  seriesLengthCount++;
  //float seriesBase = cmdMessengerPC.readFloatArg();
  if (seriesLengthCount == seriesLength) {
    cmdMessengerPC.sendCmd(kAckSendSeries,"");
  }
}

void testComms()
{
  SWSerial.print(".");
}

// Attach callback methods to handle communication with the PC
void attachCommandCallbacksPCComms()
{
  cmdMessengerPC.attach(kAreYouReady,       OnArduinoReadyPC);
  cmdMessengerPC.attach(kAskUsIfReady,      OnAskUsIfReadyPC);

  // acknowledge
  cmdMessengerPC.attach(kAcknowledge,       OnAcknowledgePC);

  // voltage1 measurement sent to the PC
  cmdMessengerPC.attach(kSendMeasuredVoltage1, OnSendMeasuredVoltage1ToPC);

  // voltage1 measurement sent to the PC
  cmdMessengerPC.attach(kSendMeasuredVoltage2, OnSendMeasuredVoltage2ToPC);
  
  // voltage1 measurement sent to the PC
  cmdMessengerPC.attach(kSendMeasuredVoltage3, OnSendMeasuredVoltage3ToPC);
  
  // voltage1 measurement sent to the PC
  cmdMessengerPC.attach(kSendMeasuredVoltage4, OnSendMeasuredVoltage4ToPC);

  // status of channel1 switch sent to the PC
  cmdMessengerPC.attach(kSendSwitchChannel1, OnSendSwitchStatusChannel1ToPC);

  // status of channel2 switch sent to the PC
  cmdMessengerPC.attach(kSendSwitchChannel2, OnSendSwitchStatusChannel2ToPC);

  // status of channel3 switch sent to the PC
  cmdMessengerPC.attach(kSendSwitchChannel3, OnSendSwitchStatusChannel3ToPC);

  // status of channel4 switch sent to the PC
  cmdMessengerPC.attach(kSendSwitchChannel4, OnSendSwitchStatusChannel4ToPC);

  // turn on an off and reset the measurements
  cmdMessengerPC.attach(kturnOnMeasurements, OnTurnOnMeasurements);
  cmdMessengerPC.attach(kturnOffMeasurements, OnTurnOffMeasurements);
  cmdMessengerPC.attach(kResetMeasurements, OnResetMeasurements);
  
  // Clear & Binary text data test
  cmdMessengerPC.attach(kValuePing, OnValuePingPC);
  cmdMessengerPC.attach(kMultiValuePing,    OnMultiValuePingPC);
  
  // Benchmarks
  cmdMessengerPC.attach(OnUnknownCommandPC);
  cmdMessengerPC.attach(kRequestReset,      OnRequestResetPC);
  cmdMessengerPC.attach(kRequestSeries,     OnRequestSeriesPC);

  cmdMessengerPC.attach(kPrepareSendSeries, OnPrepareSendSeriesPC);
  cmdMessengerPC.attach(kSendSeries,        OnSendSeriesPC);
}

} // namespace CM_PC

#endif
