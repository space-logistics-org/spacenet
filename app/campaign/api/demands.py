from fastapi import APIRouter, Depends, HTTPException
import json

router = APIRouter()

defaultReservesDuration = 0
defaultwaterRecoveryRate = 0.42
defaultclothingLifetime = 4
defaultWaterRate = 3.6
defaultEvaWaterRate = 0.6875
defaultFoodSupportRate = 0.05556
defaultAmbientFoodRate = 0.76389
defaultRfFoodRate = 1.61667
defaultOxygenRate = 3.85714
defaultEvaOxygenRate = 0.07875
defaultNitrogenRate = 2.21429
defaultHygieneRate = 0.27778
defaultHygieneKit = 1.8
defaultClothingRate = 2.3
defaultPersonalItems = 10
defaultOfficeEquipment = 5
defaultEvaSuit = 107
defaultEvaLithiumHydroxide = 0.3625
defaultHealthEquipment = 20
defaultHealthConsumables = 0.1
defaultSafetyEquipment = 25
defaultCommEquipment = 20
defaultComputerEquipment = 5
defaultTrashBagRate = 0.05
defaultWasteContainmentRate = 0.05

with open("spacenet/schemas/apollo_17/apollo_17.json") as json_file:
        json_data = json.load(json_file)
        for i in json_data:
                print(i)

def getMissionCrewSize():
        count=0

        for i in json_data['elementList']:
                if i['type'] == "HumanAgent":
                        count += 1

def getReservesDuration():
        return defaultReservesDuration

def getWaterRate():
        return defaultWaterRate

def getWaterRecoveryRate():
        return defaultwaterRecoveryRate

def getEvaWaterRate():
        return defaultEvaWaterRate

def getFoodSupportRate():
        return defaultFoodSupportRate

def getAmbientFoodRate():
        return defaultAmbientFoodRate

def getRfFoodRate():
        return defaultRfFoodRate

def getOxygenRate():
        return defaultOxygenRate

def getEvaOxygenRate():
        return defaultEvaOxygenRate

def getNitrogenRate():
        return defaultNitrogenRate

def getHygieneRate():
        return defaultHygieneRate

def getHygieneKit():
        return defaultHygieneKit

def getClothingRate():
        return defaultClothingRate

def getClothingLifetime():
        return defaultclothingLifetime

def getPersonalItems():
        return defaultPersonalItems

def getOfficeEquipment():
        return defaultOfficeEquipment

def getEvaSuit():
        return defaultEvaSuit

def getEvaLithiumHydroxide():
        return defaultEvaLithiumHydroxide

def getHealthEquipment():
        return defaultHealthEquipment

def getHealthConsumables():
        return defaultHealthConsumables

def getSafetyEquipment():
        return defaultSafetyEquipment

def getCommEquipment():
        return defaultCommEquipment

def getComputerEquipment():
        return defaultComputerEquipment

def getTrashBagRate():
        return defaultTrashBagRate

def getWasteContainmentRate():
        return defaultWasteContainmentRate

@router.post("/analysis")
def generateDemands():
        """
        water = (getMissionExplorationDuration()+getMissionTransitDuration()+getReservesDuration())*getWaterRate()*getMissionCrewSize()*(1-getWaterRecoveryRate())
        evaWater = getMissionEvaCrewTime()*getEvaWaterRate()
        totalWater = water + evaWater

        food = (getMissionExplorationDuration()+getMissionTransitDuration()+getReservesDuration())*getFoodSupportRate()*getMissionCrewSize()
        ambientFood = (getMissionExplorationDuration()+getMissionTransitDuration()+getReservesDuration())*getAmbientFoodRate()*getMissionCrewSize()
        rfFood =  (getMissionExplorationDuration()+getMissionTransitDuration()+getReservesDuration())*getRfFoodRate()*getMissionCrewSize()
        totalFood = food + ambientFood + rfFood

        oxygen = (getMissionExplorationDuration()+getMissionTransitDuration()+getReservesDuration())*getOxygenRate()*getMissionCrewSize()
        evaOxygen = getMissionEvaCrewTime()*getEvaOxygenRate()
        nitrogen = (getMissionExplorationDuration()+getMissionTransitDuration()+getReservesDuration())*getNitrogenRate()*getMissionCrewSize()
        gases = oxygen + evaOxygen + nitrogen

        hygieneItems = (getMissionExplorationDuration()+getMissionTransitDuration()+getReservesDuration())*getHygieneRate()*getMissionCrewSize()
        hygieneKits = getHygieneKit()*getMissionCrewSize()
        totalHygiene = hygieneItems + hygieneKits

        clothing = (getMissionExplorationDuration()+getMissionTransitDuration())*getClothingRate()*getMissionCrewSize()/getClothingLifetime()

        personalItems = getPersonalItems()*getMissionCrewSize()

        officeEquipment = getOfficeEquipment()*getMissionCrewSize()

        evaSuit = getEvaSuit()*getMissionCrewSize()
        evaGas = getEvaLithiumHydroxide()*getMissionEvaCrewTime()
        totalEva = evaSuit + evaGas

        healthEquipment = getHealthEquipment()
        healthConsumables = getHealthConsumables()*getMissionCrewSize()
        totalHealth = healthEquipment + healthConsumables

        safetyEquipment = getSafetyEquipment()

        commEquipment =  getCommEquipment()

        computerEquipment = getComputerEquipment()*getMissionCrewSize()

        trashBags = (getMissionExplorationDuration()+getMissionTransitDuration())*getTrashBagRate()*getMissionCrewSize()

        wasteEquipment = (getMissionExplorationDuration()+getMissionTransitDuration()+getReservesDuration())*getWasteContainmentRate()*getMissionCrewSize()
        """