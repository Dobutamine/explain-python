import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.core_models.BloodCapacitance import BloodCapacitance
from explain_core.core_models.BloodResistor import BloodResistor
from explain_core.core_models.BloodPump import BloodPump


class ArtificialWhomb(BaseModel):
    # independent parameters
    umb_art_diameter: float = 0.0   # diameter of a single umbilical artery
    umb_art_length: float = 0.0     # length of a single umbilical artery
    umb_vein_diameter: float = 0.0  # diameter of the umbilical vein
    umb_vein_length: float = 0.0    # length of the umbilical vein
    viscosity: float = 6.0          # blood viscosity in cP

    fetal_plac_vol: float = 0.0     # volume of the fetal placenta
    fetal_plac_u_vol: float = 0.0   # unstressed volume of the fetal placenta
    fetal_plac_el: float = 0.0      # elastance of the fetal placenta

    # dependent parameters
    umb_art_flow: float = 0.0       # umbilical artery flow in l/min
    umb_art_velocity: float = 0.0   # umbilical artery velocity in m/s
    umb_ven_flow: float = 0.0       # umbilical vein flow in l/min
    umb_ven_velocity: float = 0.0   # umbilical vein velocity in m/s

    # objects
    fetal_plac = {}                 # capacitance representing the fetal part of the placenta
    fetal_art = {}                  # capacitance from where the umbilical artery originates (mostly AD)
    fetal_ve = {}                   # capacitance to where the umbilical vein drans (mostly IVCE)
    fetal_ua = {}                   # bloodresistor representing the umbilical arteries
    fetal_uv = {}                   # bloodresistor representing the umbilical vein

    mat_plac = {}                   # capaciltance representing the maternal part of the placenta
    mat_art = {}                    # capacitance representing the maternal arterial system
    mat_ven = {}                    # capacitance representing the maternal venous system
    mat_ua = {}                     # maternal uterine arteries
    mat_uv = {}                     # maternal uterine veins

    def init_model(self, model: object) -> bool:
        super().init_model(model)

    def calc_model(self):
        pass
   
    


    

