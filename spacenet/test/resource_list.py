from spacenet.schemas.resource import DiscreteResource, ContinuousResource
import json

r1 = DiscreteResource(name="res1", class_of_supply=101, units="kg", type="Discrete", unit_mass=20,
                      unit_volume=0)
r2 = DiscreteResource(name="res2", class_of_supply=102, units="kg", type="Discrete", unit_mass=40,
                      unit_volume=30)
r3 = DiscreteResource(name="res3", class_of_supply=103, units="kg", type="Discrete", unit_mass=20,
                      unit_volume=20)
r4 = DiscreteResource(name="res4", class_of_supply=104, units="kg", type="Discrete", unit_mass=2,
                      unit_volume=5)
r5 = DiscreteResource(name="res5", class_of_supply=105, units="kg", type="Discrete", unit_mass=20,
                      unit_volume=20)
r6 = DiscreteResource(name="res6", class_of_supply=106, units="kg", type="Discrete", unit_mass=100,
                      unit_volume=50)
r7 = DiscreteResource(name="res7", class_of_supply=201, units="kg", type="Discrete", unit_mass=20,
                      unit_volume=20)
r8 = DiscreteResource(name="res8", class_of_supply=202, units="kg", type="Discrete", unit_mass=6,
                      unit_volume=8)
r9 = DiscreteResource(name="res9", class_of_supply=203, units="kg", type="Discrete", unit_mass=20,
                      unit_volume=20)
r10 = DiscreteResource(name="res10", class_of_supply=204, units="kg", type="Discrete", unit_mass=20,
                       unit_volume=20)

r11 = ContinuousResource(name="res11", class_of_supply=101, units="kg", type="Continuous", unit_mass=25.5,
                         unit_volume=20.0)
r12 = ContinuousResource(name="res12", class_of_supply=102, units="kg", type="Continuous",
                         unit_mass=200.50, unit_volume=120.1)
r13 = ContinuousResource(name="res13", class_of_supply=103, units="kg", type="Continuous", unit_mass=3.5,
                         unit_volume=20.9)
r14 = ContinuousResource(name="res14", class_of_supply=104, units="kg", type="Continuous", unit_mass=15.7,
                         unit_volume=10.0)
r15 = ContinuousResource(name="res15", class_of_supply=105, units="kg", type="Continuous", unit_mass=20.0,
                         unit_volume=20.0)
r16 = ContinuousResource(name="res16", class_of_supply=106, units="kg", type="Continuous", unit_mass=45.6,
                         unit_volume=55.455)
r17 = ContinuousResource(name="res17", class_of_supply=201, units="kg", type="Continuous", unit_mass=78.43,
                         unit_volume=68.0)
r18 = ContinuousResource(name="res18", class_of_supply=202, units="kg", type="Continuous", unit_mass=30.5,
                         unit_volume=35.4)
r19 = ContinuousResource(name="res19", class_of_supply=203, units="kg", type="Continuous", unit_mass=97.9,
                         unit_volume=88.5)
r20 = ContinuousResource(name="res20", class_of_supply=204, units="kg", type="Continuous", unit_mass=33.6,
                         unit_volume=45.7)

ResourceList = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17,
                r18, r19, r20]
if __name__ == '__main__':
    with open('resource_data.json', 'w') as f:
        json.dump([resource.dict() for resource in ResourceList], f, indent=2)

