/* Class to check and report the status of the switches for the four channels
 *  
 * @author: Dr. Markus Reinhardt 
 * @date:   16th July 2021
 */
#ifndef HANDLE4CHANNELSWITCHES_H
#define HANDLE4CHANNELSWITCHES_H

#include <Arduino.h>

#define MaxNoChannels 4

#define SWITCH_PIN_CHANNEL_1 11
#define SWITCH_PIN_CHANNEL_2 10
#define SWITCH_PIN_CHANNEL_3 9
#define SWITCH_PIN_CHANNEL_4 8

class Handle4ChannelSwitches
{
public:
  Handle4ChannelSwitches()
  {
    pinMode(SWITCH_PIN_CHANNEL_1, INPUT);   // set channel1 switch pin as input
    pinMode(SWITCH_PIN_CHANNEL_2, INPUT);   // set channel2 switch pin as input
    pinMode(SWITCH_PIN_CHANNEL_3, INPUT);   // set channel3 switch pin as input
    pinMode(SWITCH_PIN_CHANNEL_4, INPUT);   // set channel4 switch pin as input
  };
  
  int* returnSwitchStatus() { return m_switchStatus; };

  void getSwitchStatus()
  {
    m_switchStatus[0] = digitalRead(SWITCH_PIN_CHANNEL_1);
    m_switchStatus[1] = digitalRead(SWITCH_PIN_CHANNEL_2);
    m_switchStatus[2] = digitalRead(SWITCH_PIN_CHANNEL_3);
    m_switchStatus[3] = digitalRead(SWITCH_PIN_CHANNEL_4);

    Serial.print("Switches: CH1: ");Serial.print(m_switchStatus[0]);
    Serial.print(",    CH2: ");Serial.print(m_switchStatus[1]);
    Serial.print(",    CH3: ");Serial.print(m_switchStatus[2]);
    Serial.print(",    CH4: ");Serial.println(m_switchStatus[3]);
  }
  
private:
  int m_switchStatus[MaxNoChannels];  
};


#endif
 
