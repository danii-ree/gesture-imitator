void setup()
{
  Serial.begin(9600)
}
void loop()
{
  if (Serial.available() > 0)
  {
    String data = Serial.readString();
    int finger_count = data.toInt();

    Serial.print("Number of fingers: ");
    Serial.println(finger_count);
  }

}
