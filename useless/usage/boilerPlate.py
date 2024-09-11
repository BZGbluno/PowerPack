from powerMeasurement import PowerPackInputs
import nidaqmx
import sys
import time
import pdb
from nidaqmx.constants import TerminalConfiguration
from nidaqmx.stream_readers import AnalogUnscaledReader



def main():

    if len(sys.argv) != 4:
        print("This function needs 3 argument: sampleTime, samplingRate, Ohms of Resistor")
        sys.exit(1)


    samplingRate = sys.argv[2]
    samplingTime = sys.argv[1]
    resistorOhms = sys.argv[3]
    powerPackForThreeVolts = PowerPackInputs(resistorOhms)


    # Create a task
    task = nidaqmx.Task("Finding Total Power Consumption")

    '''
    This is the 3 type of modules that can be used 3.3V, 5V, and 12V
    '''
    # Channels for 3.3v measurements
    task.ai_channels.add_ai_voltage_chan("cDAQ1Mod4/ai0", terminal_config=nidaqmx.constants.TerminalConfiguration.DIFF)
    task.ai_channels.add_ai_voltage_chan("cDAQ1Mod4/ai3", terminal_config=nidaqmx.constants.TerminalConfiguration.DIFF)
    # Channels for 5V measurements
    task.ai_channels.add_ai_voltage_chan("cDAQ1Mod6/ai0", terminal_config=nidaqmx.constants.TerminalConfiguration.DIFF)


    # Channels for 12V measurements
    
    '''
    This is setting up the sampling rates
    '''
    task.timing.cfg_samp_clk_timing(
    rate=int(samplingRate), # The sampling rate in samples per second
    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
    )

    voltageDiff = []
    # Start the task
    task.start()
    start_time = time.time()


    try:
        while time.time() - start_time <=int(samplingTime):
            # Read the voltage value continuously
            voltage = task.read()
            voltageDiff.append(voltage)

            print("Voltage diff measured:", voltage)
    except KeyboardInterrupt:
        # Stop the task if Ctrl+C is pressed
        task.stop()
    task.close()

    '''
    This is where data is being saved and calculated
    '''
    powerPackForThreeVolts.setVoltageInformation(voltageDiff)
    wattsBeingUsed = powerPackForThreeVolts.powerCalculations(3.3)
    powerConsumed = powerPackForThreeVolts.powerConsumption(samplingTime)
    # Virginia cost is 14 cents per kWh
    costOfPower = powerPackForThreeVolts.cost(0.14)
    
    print(f"This operation requires {wattsBeingUsed} watts, "
          f"for {samplingTime} seconds we used {powerConsumed} kwh, the cost "
          f"of this in Virginia is {costOfPower}")





    



if __name__ == "__main__":
    main()



