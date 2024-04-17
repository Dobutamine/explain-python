import math
from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance

class IntrinsicPump(BaseModel):
    # independent variables
    duration: float = 2.0       # duration of contraction
    freq: float = 10.0           # frequency
    el_rest: float = 20.0      # elastance at rest

    # dependent variables
    el_con: float = 0.0         # variable elastance simulating contraction
    el_tot: float = 0.0         # total elastance

    total_time: float = 0.0
    #_model_comp_to: Capacitance = {}

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized
   
    def calc_model(self) -> None:
        self.total_time += self._t    

        for targets in self.targets:
            if self._model.models[targets].pacemaker == True:
                t_start = 1
                self._model.models[targets].t_start = t_start
                #self.amp = 35

                # next_C = self._model.models[targets].comp_to
                # self._model_comp_to = self._model.models[next_C]
                # next_R = self._model.models[targets].next_resistor
                # self._next_resistor = self._model.models[next_R]

            else:
                act = self._model.models[targets].activator
                t_start = self._model.models[act].t_start + 0.5
                self._model.models[targets].t_start = t_start
                #self.amp = 10

            el_rest = self._model.models[targets].el_rest
            self._model.models[targets].contraction_interval = 60 / self.freq

            if self.total_time >= t_start:
                self._model.models[targets].interval_running = True
                
                # if timer exceeds contraction duration refractory period starts
                if self._model.models[targets].contraction_timer > self.duration:
                    self._model.models[targets].contraction_timer = 0.0
                    self._model.models[targets].contraction_running = False                
                # if timer exceeds interval, new interval starts
                if self._model.models[targets].interval_timer > self._model.models[targets].contraction_interval:
                    self._model.models[targets].interval_timer = 0.0
                    self._model.models[targets].contraction_running = True 

                # amplitude dependent on transmural pressure
                # if self._model.models[targets].pacemaker == True and self._model.models[targets].interval_timer == 0.0:
                    # self.amp_ptm = 3*math.sin((1/3)*math.pi + 3*self._model.models[targets].pres) + 1
                    # if self.amp_ptm <= 1:
                    #     self.amp_ptm = 1
                
                    #self.amp_f = - 10000*self._next_resistor.flow + 5

                    #self.amp_pout = -0.5 * self._model_comp_to.pres + 4

                    #self.amp = self.amp_ptm + self.amp_f + self.amp_pout
                    #self._model.models[targets].amp = self.amp  

                    # self.freq_ptm = 2 * self._model.models[targets].pres + 1
                    # if self.freq_ptm <= 1:
                    #     self.freq_ptm = 1
                    # elif self.freq_ptm >= 10:
                    #     self.freq_ptm = 10
                    
                    #self.freq_f = -15000* self._next_resistor.flow + 6

                    #self.freq_pout = 0.5 * self._model_comp_to.pres +1
                    
                    #self.freq = self.freq_ptm + self.freq_f + self.freq_pout
                    #self._model.models[targets].freq = self.freq 
                    # self._model.models[targets].contraction_interval = 60 / self.freq                   
                
                # else:
                #     act = self._model.models[targets].activator
                #     self.amp = self._model.models[act].amp
                #     if self._model.models[targets].interval_timer == 0.0:
                #         self.freq = self._model.models[act].freq
                #         self._model.models[targets].contraction_interval = 60 / self.freq

                amp = self._model.models[targets].amp
                el_con = amp * (0.5 * (1 - math.cos(2*math.pi/(self.duration)*self._model.models[targets].contraction_timer)))
                #el_con = amp * math.sin(2*math.pi/(2*self.duration) * (self._model.models[targets].contraction_timer))
                self._model.models[targets].el_con = el_con
                el_tot = el_rest + el_con
                self._model.models[targets].el_base = el_tot      

            # increase the timers
            if self._model.models[targets].interval_running == True:
                self._model.models[targets].interval_timer += self._t
            if self._model.models[targets].contraction_running == True:
                self._model.models[targets].contraction_timer += self._t   
            
           
                            
                       
                


                
        
   
        
