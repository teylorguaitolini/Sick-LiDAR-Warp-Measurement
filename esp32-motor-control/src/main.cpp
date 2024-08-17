#include <Arduino.h>

const int stepPin = 5;
const int dirPin = 18;

void performMotorRoutine();
void rotateStepperR(int numRotations, int speed);
void rotateStepperL(int numRotations, int speed);

/* Setup */
void setup() 
{
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  Serial.begin(115200);
}

/* Loop */
void loop() 
{
  if (Serial.available()) 
  {
    String data = Serial.readString();
    data.trim();
    if (data == "start") 
    {
      Serial.println("starting");
      performMotorRoutine();
      Serial.println("done");
    }
  }
}

/* Functions */

/**
 * Perform the motor routine by rotating the stepper motor to the right and then to the left.
 */
void performMotorRoutine() 
{
  rotateStepperR(45, 100);
  delay(500);
  rotateStepperL(45, 100);
  delay(500);
}

/**
 * Rotate the stepper motor to the right for a specified number of rotations at a given speed.
 * 
 * @param numRotations The number of rotations to perform.
 * @param speed The speed of the rotation.
 */
void rotateStepperR(int numRotations, int speed) 
{
  int stepsPerRotation = 1600;

  digitalWrite(dirPin, HIGH);

  for(int i = 0; i < numRotations * stepsPerRotation; i++) 
  {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(speed);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(speed);
  }
}

/**
 * Rotate the stepper motor to the left for a specified number of rotations at a given speed.
 * 
 * @param numRotations The number of rotations to perform.
 * @param speed The speed of the rotation.
 */
void rotateStepperL(int numRotations, int speed) 
{
  int stepsPerRotation = 1600;

  digitalWrite(dirPin, LOW);

  for(int i = 0; i < numRotations * stepsPerRotation; i++) 
  {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(speed);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(speed);
  }
}
