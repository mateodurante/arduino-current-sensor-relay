//Basic energy monitoring sketch - by Trystan Lea
//Licenced under GNU General Public Licence more details here
// openenergymonitor.org

//Sketch measures voltage and current.
//and then calculates useful values like real power,
//apparent power, powerfactor, Vrms, Irms.

//Setup variables
int numberOfSamples = 3000;

//Set Voltage and current input pins
int inPinV = 2;
int inPinI = A0;

//Calibration coeficients
//These need to be set in order to obtain accurate results
double VCAL = 1.0;
double ICAL = 1.0;
double PHASECAL = 2.3;

//Sample variables
int lastSampleV,lastSampleI,sampleV,sampleI;

//Filter variables
double lastFilteredV, lastFilteredI, filteredV, filteredI;
double filterTemp;

//Stores the phase calibrated instantaneous voltage.
double calibratedV;

//Power calculation variables
double sqI,sqV,instP,sumI,sumV,sumP;

//Useful value variables
double realPower,
       apparentPower,
       powerFactor,
       Vrms,
       Irms;
       
void setup()
{
   Serial.begin(9600);
}

void loop()
{

for (int n=0; n<numberOfSamples; n++)
{

   //Used for offset removal
   lastSampleV=sampleV;
   lastSampleI=sampleI;
   
   //Read in voltage and current samples.   
   sampleV = analogRead(inPinV);
   sampleI = analogRead(inPinI);
   
   //Used for offset removal
   lastFilteredV = filteredV;
   lastFilteredI = filteredI;
 
   //Digital high pass filters to remove 2.5V DC offset.
   filteredV = 0.996*(lastFilteredV+sampleV-lastSampleV);
   filteredI = 0.996*(lastFilteredI+sampleI-lastSampleI);
   
   //Phase calibration goes here.
   calibratedV = lastFilteredV + PHASECAL * (filteredV - lastFilteredV);
 
   //Root-mean-square method voltage
   //1) square voltage values
   sqV= calibratedV * calibratedV;
   //2) sum
   sumV += sqV;
   
   //Root-mean-square method current
   //1) square current values
   sqI = filteredI * filteredI;
   //2) sum
   sumI += sqI;

   //Instantaneous Power
   instP = calibratedV * filteredI;
   //Sum
   sumP +=instP;
}

//Calculation of the root of the mean of the voltage and current squared (rms)
//Calibration coeficients applied.
Vrms = VCAL*sqrt(sumV / numberOfSamples);
Irms = ICAL*sqrt(sumI / numberOfSamples);

//Calculation power values
realPower = VCAL*ICAL*sumP / numberOfSamples;
apparentPower = Vrms * Irms;
powerFactor = realPower / apparentPower;

//Output to serial
Serial.print(realPower);
Serial.print(' ');
Serial.print(apparentPower);
Serial.print(' ');
Serial.print(powerFactor);
Serial.print(' ');
Serial.print(Vrms);
Serial.print(' ');
Serial.println(Irms);

//Reset accumulators
sumV = 0;
sumI = 0;
sumP = 0;

}
