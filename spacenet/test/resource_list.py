from spacenet.schemas.Resource import DiscreteResource, ContinuousResource, ResourceType, ClassOfSupply
import json

r1 = DiscreteResource(id=1, name="res1", cos=101, units="kg", type="discrete", unitmass=20, unitvolume=20)
r2 = DiscreteResource(id=2, name="res2", cos=102, units="kg", type="discrete", unitmass=40, unitvolume=30)
r3 = DiscreteResource(id=3, name="res3", cos=103, units="kg", type="discrete", unitmass=20, unitvolume=20)
r4 = DiscreteResource(id=4, name="res4", cos=104, units="kg", type="discrete", unitmass=2, unitvolume=5)
r5 = DiscreteResource(id=5, name="res5", cos=105, units="kg", type="discrete", unitmass=20, unitvolume=20)
r6 = DiscreteResource(id=6, name="res6", cos=106, units="kg", type="discrete", unitmass=100, unitvolume=50)
r7 = DiscreteResource(id=7, name="res7", cos=201, units="kg", type="discrete", unitmass=20, unitvolume=20)
r8 = DiscreteResource(id=8, name="res8", cos=202, units="kg", type="discrete", unitmass=6, unitvolume=8)
r9 = DiscreteResource(id=9, name="res9", cos=203, units="kg", type="discrete", unitmass=20, unitvolume=20)
r10 = DiscreteResource(id=10, name="res10", cos=204, units="kg", type="discrete", unitmass=20, unitvolume=20)

r11 = ContinuousResource(id=11, name="res11", cos=101, units="kg", type="continuous", unitmass=25.5, unitvolume=20.0)
r12 = ContinuousResource(id=12, name="res12", cos=102, units="kg", type="continuous", unitmass=200.50, unitvolume=120.1)
r13 = ContinuousResource(id=13, name="res13", cos=103, units="kg", type="continuous", unitmass=3.5, unitvolume=20.9)
r14 = ContinuousResource(id=14, name="res14", cos=104, units="kg", type="continuous", unitmass=15.7, unitvolume=10.0)
r15 = ContinuousResource(id=15, name="res15", cos=105, units="kg", type="continuous", unitmass=20.0, unitvolume=20.0)
r16 = ContinuousResource(id=16, name="res16", cos=106, units="kg", type="continuous", unitmass=45.6, unitvolume=55.455)
r17 = ContinuousResource(id=17, name="res17", cos=201, units="kg", type="continuous", unitmass=78.43, unitvolume=68.0)
r18 = ContinuousResource(id=18, name="res18", cos=202, units="kg", type="continuous", unitmass=30.5, unitvolume=35.4)
r19 = ContinuousResource(id=19, name="res19", cos=203, units="kg", type="continuous", unitmass=97.9, unitvolume=88.5)
r20 = ContinuousResource(id=20, name="res20", cos=204, units="kg", type="continuous", unitmass=33.6, unitvolume=45.7)

ResourceList = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20]

jsonlist = json.dumps(ResourceList)

with open('resource_data.json', 'w') as f:
    json.dump(jsonlist, f)
