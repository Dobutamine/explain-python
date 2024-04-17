from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.Capacitance import Capacitance

class Starling(BaseModel):
    # do some custom model initialization
    # independent variables:
    L: float = 0.9788e-9    # hydraulic conductivity
    S: float = 50.0         # capillary surface area
    sigma: float = 0.7      # osmotic reflection coefficient

    i : float = 1.0         # van 't Hoff's factor, 1 for plasma
    R: float = 0.08206      # ideal gass constant [L*atm/mol*K]
    T: float = 37           # temperature in degrees Celcius
    mm: float = 66500       # molar mass in g/mol

    #PSt = 0.0202        # permeability surface product albumin [ml/s]
    #alphaLP = 0.05
    #alphaSP = 0.6

    # dependent variables:
    flow: float = 0.0
    
    #sol_flux: float = 0.0
    #flux_dif: float = 0.0
    #flux_convLP: float = 0.0
    #flux_convSP: float = 0.0
    #conc_new: float = 0.0

    # define object which hold references to a Capacitance or TimeVaryingElastance
    _model_comp_from: Capacitance = {}
    _model_comp_to: Capacitance = {}


    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # get a reference to the model components which are connected by this resistor
        if type(self.comp_from) is str:
            self._model_comp_from = self._model.models[self.comp_from]
        else:
            self._model_comp_from = self.comp_from

        if type(self.comp_to) is str:
            self._model_comp_to = self._model.models[self.comp_to]
        else:
            self._model_comp_to = self.comp_to


        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def calc_model(self) -> None:
        # do some cystom model work
        # hydrostatic pressure
        hP1 = self._model_comp_from.pres
        hP2 = self._model_comp_to.pres
        # calculate oncotic pressure
        oP1: float = (self.i * (self._model_comp_from.aboxy["albumin"]/self.mm) * self.R * (273.15 + self.T)) * 760 # concentration albumin in g/L to mol/L, multiply by 760 from atmosphere to mmHg
        oP2: float = (self.i * (self._model_comp_to.aboxy["albumin"]/self.mm) * self.R * (273.15 + self.T)) * 760 

        self._model_comp_from.pres_osm = oP1
        self._model_comp_to.pres_osm = oP2

        # for target_from in self.target_from:
        #     self._model.models[target_from].pres_osm = oP1
        # for target_to in self.target_to:
        #     self._model.models[target_to].pres_osm = oP2


        # calculate transcapillary flow
        self.flow = self.L * self.S * ((hP1-hP2) - self.sigma * (oP1-oP2))

        self.flow_h = self.L * self.S * (hP1-hP2)
        self.flow_o = -(self.L * self.S * self.sigma * (oP1-oP2))

#        # update solutes etc. (flux from capillary to interstitium is positive)
#        self.flux_dif = self.PSt * (self._model_comp_from.aboxy["albumin"] - self._model_comp_to.aboxy["albumin"])
#        if self.flow > 0:
#            self.flux_convLP = (1 - self.sigma) * self.flow * self.alphaLP * self._model_comp_from.aboxy["albumin"]
#            self.flux_convSP = (1 - self.sigma) * self.flow * self.alphaSP * self._model_comp_from.aboxy["albumin"]
#        if self.flow < 0:
#            self.flux_convLP = (1 - self.sigma) * self.flow * self.alphaLP * self._model_comp_to.aboxy["albumin"]
#            self.flux_convSP = (1 - self.sigma) * self.flow * self.alphaSP * self._model_comp_to.aboxy["albumin"]
        
#        self.sol_flux = self.flux_dif + self.flux_convLP + self.flux_convSP

        # concentration solutes in transported water
#        self.conc_new = self.sol_flux / self.flow
        
        

        # update volumes
        if self.flow > 0:
            # flow is from comp_from to comp_to
            vol_not_removed: float = self._model_comp_from.volume_out(
                self.flow * self._t
            )

            self._model_comp_to.volume_in(
                (self.flow * self._t) - vol_not_removed, self._model_comp_from
            )
            return

        if self.flow < 0:
            # flow is from comp_to to comp_from
            vol_not_removed: float = self._model_comp_to.volume_out(
                -self.flow * self._t
            )

            self._model_comp_from.volume_in(
                (-self.flow * self._t) - vol_not_removed, self._model_comp_to
            )
            return
        


        