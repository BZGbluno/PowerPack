import nidaqmx
import time

class PowerPackInputs:
    def __init__(self, resistorOhms):
        self.Ohms = resistorOhms
        self.Measurements = None
        self.WattBeingUsed = 0
        self.powerConsumed = 0


    '''
    These are all getter method or setter methods
    '''
    def setVoltageInformation(self, foundMeasurements):
        self.Measurements = foundMeasurements
    def getVoltageInformation(self):
        return self.Measurements
    def getTotalPowerConsumptionCost(self):
        return self.totalPowerConsumptionCost
    # def getWattBeingUsed(self) -> int:
    #     return self.WattBeingUsed
        
    

    '''
    Ohms law: deltaV = I/R
    Electric Power Law: P = VI

    I = current
    R = resistance
    P = power in watts
    V = volts

    This function currently returns the average watts
    '''
    # Questions to ask: For this do we want the average of watts since
    # that is how we find the kilowatts consumed per hour
    def powerCalculations(self, powerSupplyVolts) -> int:
        voltages = self.Measurements
        ohms = self.Ohms
        total = 0
        for measurement in voltages:
            total += float(measurement)
        averageOfTotal = total/len(voltages)
        power = powerSupplyVolts * (averageOfTotal/float(ohms))
        self.WattBeingUsed = power
        return power

        
        

    '''
    kWh = ( Watts * time(hours) )/ 1000
    returns the kilowatts hour by finding the process time where
    I will use the sample total time as the total process time
    '''
    #Does it make sense for process time to be the total sample time?
    def powerConsumption(self, totalProcessTime):
        totalProcessTime = float(totalProcessTime)/ (60 * 60)
        self.powerConsumed = (self.WattBeingUsed * totalProcessTime)/1000
        return self.powerConsumed


    '''
    This function will return the cost of using power in a specifc area
    '''
    #Is this useful ?????
    def cost(self, costInYourArea): 
        return float(costInYourArea) * self.powerConsumed



    

        
        




    
    
