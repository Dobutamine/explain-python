import math

from explain_core.helpers.BloodComposition import set_blood_composition
from explain_core.helpers.GasComposition import set_gas_composition


class Ecls:
    # static properties
    model_type: str = "Ecls"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.pres_atm = 760.0
        self.ecls_running = False
        self.ecls_clamped = False
        self.fio2_gas_baseline = 0.205
        self.fio2_gas = 0.205
        self.fico2_gas_baseline = 0.000392
        self.fico2_gas = 0.000392
        self.co2_gas_flow = 0.4
        self.temp_gas = 37.0
        self.humidity_gas = 1.0
        self.sweep_gas = 1.0
        self.drainage_site = "RA"
        self.return_site = "AAR"
        self.drainage_cannula_length = 0.011
        self.drainage_cannula_size = 12
        self.drainage_cannula_diameter = 0.3
        self.return_cannula_length = 0.011
        self.return_cannula_size = 10
        self.return_cannula_diameter = 0.3
        self.tubing_size = 0.25
        self.tubing_elastance = 11600
        self.tubing_diameter = 0.3
        self.tubing_in_length = 1.0
        self.tubing_out_length = 1.0
        self.diff_o2 = 0.001
        self.diff_o2_factor = 1.0
        self.diff_co2 = 0.001
        self.diff_co2_factor = 1.0
        self.pump_volume = 0.8
        self.oxy_volume = 0.8
        self.oxy_resistance = 1000
        self.oxy_resistance_factor = 1.0
        self.inlet_res = 20000.0
        self.inlet_res_factor = 1.0
        self.outlet_res = 20000.0
        self.outlet_res_factor = 1.0
        self.pump_rpm = 0.0

        # dependent properties
        self.pre_oxy_ph = 0.0
        self.pre_oxy_po2 = 0.0
        self.pre_oxy_pco2 = 0.0
        self.pre_oxy_hco3 = 0.0
        self.pre_oxy_be = 0.0
        self.pre_oxy_so2 = 0.0

        self.post_oxy_ph = 0.0
        self.post_oxy_po2 = 0.0
        self.post_oxy_pco2 = 0.0
        self.post_oxy_hco3 = 0.0
        self.post_oxy_be = 0.0
        self.post_oxy_so2 = 0.0

        self.ven_pres = 0.0
        self.pre_oxy_pres = 0.0
        self.post_oxy_pres = 0.0
        self.tmp_pres = 0.0
        self.blood_flow = 0.0
        self.gas_flow = 0.0

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self.drainage_cannula = None
        # bloodresistor
        self._tubing_in = None
        # bloodcapacitance
        self._tubing_in_pump = None
        # bloodresistor
        self._pump = None
        # bloodpump
        self._pump_bridge = None
        # bloodresistor
        self._bridge = None
        self._bridge_oxy = None
        # bloodresistor
        self._oxy = None
        # bloodcapacitance
        self._oxy_tubing_out = None
        # bloodresistor
        self._tubing_out = None
        # bloodcapacitance
        self._return_cannula = None
        # bloodresistor

        self._gas_in = None
        # gascapacitance
        self._gas_in_oxy = None
        # gasresistor
        self._gas_oxy = None
        # gascapacitance
        self._gas_oxy_out = None
        # gasresistor
        self._gas_out = None
        # gascapacitance

        self._gasex = None
        # gasexchanger
        self._ecls_parts = []

        self._update_counter = 0.0
        self._update_interval = 1.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # build the ecls system

        self.build_blood_part()
        self.build_gas_part()
        self.build_gasexchanger()

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized and self.ecls_running:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # set the number of rotations of the pump
        self._pump.pump_rpm = self.pump_rpm

        # check if ecls is clamped
        self._drainage_cannula.no_flow = self.ecls_clamped
        self._return_cannula.no_flow = self.ecls_clamped

        # get the dependent parameters
        self.blood_flow = self._oxy_tubing_out.flow_lmin_avg
        self.gas_flow = self._gas_oxy_out.flow * 60.0
        self.ven_pres = self._tubing_in.pres
        self.pre_oxy_pres = self._bridge.pres
        self.post_oxy_pres = self._tubing_out.pres
        self.tmp_pres = self.pre_oxy_pres - self.post_oxy_pres

        # calculate the pre and post oxygenator bloodgasses
        if self._update_counter > self._update_interval:
            self._update_counter = 0.0
            set_blood_composition(self._tubing_in)
            set_blood_composition(self._tubing_out)

            self.pre_oxy_ph = self._tubing_in.ph
            self.pre_oxy_po2 = self._tubing_in.po2
            self.pre_oxy_pco2 = self._tubing_in.pco2
            # self.pre_oxy_hco3 = self._tubing_in.aboxy.hco3
            # self.pre_oxy_be = self._tubing_in.aboxy.be
            self.pre_oxy_so2 = self._tubing_in.so2

            self.post_oxy_ph = self._tubing_out.ph
            self.post_oxy_po2 = self._tubing_out.po2
            self.post_oxy_pco2 = self._tubing_out.pco2
            # self.post_oxy_hco3 = self._tubing_out.aboxy.hco3
            # self.post_oxy_be = self._tubing_out.aboxy.be
            self.post_oxy_so2 = self._tubing_out.so2

            # calculate the tubing diameter from the tubing size
            self.tubing_diameter = self.tubing_size * 0.0254

            # calculate the drainage cannula diameter
            self.drainage_cannula_diameter = (
                self.drainage_cannula_size * 0.33
            ) / 1000.0

            # calculate the return cannula diameter (1 Fr is 0.33 mm)
            self.return_cannula_diameter = (self.return_cannula_size * 0.33) / 1000.0

            # calculate the resistance of these cannulas depending on the length and diameter
            drainage_res = self.calc_resistance_tube(
                self.drainage_cannula_diameter, self.drainage_cannula_length
            )

            self._drainage_cannula.r_for = drainage_res * self.inlet_res_factor
            self._drainage_cannula.r_back = drainage_res * self.inlet_res_factor

            return_res = self.calc_resistance_tube(
                self.return_cannula_diameter, self.return_cannula_length
            )

            self._return_cannula.r_for = return_res * self.outlet_res_factor
            self._return_cannula.r_back = return_res * self.outlet_res_factor

            # calculate the oxgenator resistance
            self._oxy_tubing_out.r_for = (
                self.oxy_resistance * self.oxy_resistance_factor
            )
            self._oxy_tubing_out.r_back = (
                self.oxy_resistance * self.oxy_resistance_factor
            )

            # set the resistance of the inspiration valve for the sweep gas flow
            if self.sweep_gas > 0.0:
                self._gas_in_oxy.r_for = (self._gas_in.pres - self.pres_atm) / (
                    self.sweep_gas / 60.0
                )

            # set the diffusion coeeficients of the oxygenator
            self._gasex.dif_o2 = self.diff_o2 * self.diff_o2_factor
            self._gasex.dif_co2 = self.diff_co2 * self.diff_co2_factor

        self._update_counter += self._t

    def build_tubing_in(self):
        # define a blood capacitance which represents the tubing on the inlet side
        self._tubing_in = self._model_engine.models["ECLS_TUBIN"]

        # calculate the tubing diameter from the tubing size
        self.tubing_diameter = self.tubing_size * 0.0254

        # we need to calculate the unstressed volume of the tubing depending on the length and diameter
        tubing_in_uvol = self.calc_volume(self.tubing_in_length, self.tubing_diameter)

        self._tubing_in.init_model(
            is_enabled=False,
            fixed_composition=False,
            vol=tubing_in_uvol,
            u_vol=tubing_in_uvol,
            el_base=self.tubing_elastance,
        )

        # set the electrolytes
        self._tubing_in.solutes = {**self._model_engine.models["AA"].solutes}
        self._tubing_in.aboxy = {**self._model_engine.models["AA"].aboxy}

        # calculate the starting pressure
        self._tubing_in.calc_model()

        # add the tubing in to the ecls parts list
        self._ecls_parts.append(self._tubing_in)

    def build_tubing_out(self):
        # define a blood capacitance which represents the tubing on the inlet side
        self._tubing_out = self._model_engine.models["ECLS_TUBOUT"]

        # calculate the tubing diameter from the tubing size
        self.tubing_diameter = self.tubing_size * 0.0254

        # we need to calculate the unstressed volume of the tubing depending on the length and diameter
        tubing_out_uvol = self.calc_volume(self.tubing_out_length, self.tubing_diameter)

        self._tubing_out.init_model(
            is_enabled=False,
            fixed_composition=False,
            vol=tubing_out_uvol,
            u_vol=tubing_out_uvol,
            el_base=self.tubing_elastance,
        )

        # set the electrolytes
        self._tubing_out.solutes = {**self._model_engine.models["AA"].solutes}
        self._tubing_out.aboxy = {**self._model_engine.models["AA"].aboxy}

        # calculate the starting pressure
        self._tubing_out.calc_model()

        # add the tubing in to the ecls parts list
        self._ecls_parts.append(self._tubing_out)

    def build_oxy(self):
        # define a blood capacitance which represents the tubing between the pump and oxygenator
        self._bridge = self._model_engine.models["ECLS_BRIDGE"]

        # calculate the tubing diameter from the tubing size
        self.tubing_diameter = self.tubing_size * 0.0254

        # we need to calculate the unstressed volume of the tubing depending on the length and diameter
        bridge_uvol = self.calc_volume(
            self.tubing_in_length / 2.0, self.tubing_diameter
        )

        # define a blood capacitance which represents the tubing between the pump and oxygenator
        self._bridge.init_model(
            is_enabled=False,
            fixed_composition=False,
            vol=bridge_uvol,
            u_vol=bridge_uvol,
            el_base=self.tubing_elastance,
        )

        # set the electrolytes
        self._bridge.solutes = {**self._model_engine.models["AA"].solutes}
        self._bridge.aboxy = {**self._model_engine.models["AA"].aboxy}

        # calculate the starting pressure
        self._bridge.calc_model()
        # add the tubing in to the ecls parts list
        self._ecls_parts.append(self._bridge)

        # define a blood capacitance which represents the tubing on the inlet side
        self._oxy = self._model_engine.models["ECLS_OXY"]
        self._oxy.init_model(
            is_enabled=False,
            fixed_composition=False,
            vol=self.oxy_volume,
            u_vol=self.oxy_volume,
            el_base=10000,
        )

        # set the electrolytes
        self._oxy.solutes = {**self._model_engine.models["AA"].solutes}
        self._oxy.aboxy = {**self._model_engine.models["AA"].aboxy}

        # calculate the starting pressure
        self._oxy.calc_model()
        # add the tubing in to the ecls parts list
        self._ecls_parts.append(self._oxy)

    def init_pump(self):
        # define a blood capacitance which represents the tubing on the inlet side
        self._pump.init_model(
            is_enabled=False,
            fixed_composition=False,
            vol=self.pump_volume,
            u_vol=self.pump_volume,
            el_base=self.tubing_elastance,
            inlet=self._tubing_in_pump,
            outlet=self._bridge_oxy,
        )
        # set the electrolytes
        self._pump.solutes = {**self._model_engine.models["AA"].solutes}
        self._pump.aboxy = {**self._model_engine.models["AA"].aboxy}
        # calculate the starting pressure
        self._pump.calc_model()

        # add the tubing in to the ecls parts list
        self._ecls_parts.append(self._pump)

    def build_blood_part(self):
        self.build_tubing_in()
        self.build_tubing_out()
        self.build_oxy()

        # define a blood pump but don't initialize it because the connectors have not been built yet
        self._pump = self._model_engine.models["ECLS_PUMP"]

        # calculate the drainage cannula diameter
        self.drainage_cannula_diameter = (self.drainage_cannula_size * 0.33) / 1000.0

        # calculate the return cannula diameter (1 Fr is 0.33 mm)
        self.return_cannula_diameter = (self.return_cannula_size * 0.33) / 1000.0

        # calculate the resistance of this cannula depending on the length and diameter
        drainage_res = self.calc_resistance_tube(
            self.drainage_cannula_diameter, self.drainage_cannula_length
        )

        return_res = self.calc_resistance_tube(
            self.return_cannula_diameter, self.return_cannula_length
        )

        # connect the parts
        self._drainage_cannula = self._model_engine.models["ECLS_DR"]
        self._drainage_cannula.init_model(
            is_enabled=False,
            no_flow=False,
            no_back_flow=False,
            comp_from=self._model_engine.models[self.drainage_site],
            comp_to=self._tubing_in,
            r_for=drainage_res,
            r_back=drainage_res,
            r_k=0.0,
        )

        # add the resistor to the list
        self._ecls_parts.append(self._drainage_cannula)

        self._tubing_in_pump = self._model_engine.models["ECLS_TUBIN_PUMP"]
        self._tubing_in_pump.init_model(
            is_enabled=False,
            no_flow=False,
            no_back_flow=False,
            comp_from=self._tubing_in,
            comp_to=self._pump,
            r_for=50.0,
            r_back=50.0,
            r_k=0.0,
        )

        # add the resistor to the list
        self._ecls_parts.append(self._tubing_in_pump)

        self._pump_bridge = self._model_engine.models["ECLS_PUMP_BRIDGE"]
        self._pump_bridge.init_model(
            is_enabled=False,
            no_flow=False,
            no_back_flow=False,
            comp_from=self._pump,
            comp_to=self._bridge,
            r_for=50.0,
            r_back=50.0,
            r_k=0.0,
        )

        # add the resistor to the list
        self._ecls_parts.append(self._pump_bridge)

        self._bridge_oxy = self._model_engine.models["ECLS_BRIDGE_OXY"]
        self._bridge_oxy.init_model(
            is_enabled=False,
            no_flow=False,
            no_back_flow=False,
            comp_from=self._bridge,
            comp_to=self._oxy,
            r_for=50.0,
            r_back=50.0,
            r_k=0.0,
        )

        # add the resistor to the list
        self._ecls_parts.append(self._bridge_oxy)

        self._oxy_tubing_out = self._model_engine.models["ECLS_OXY_TUBOUT"]
        self._oxy_tubing_out.init_model(
            is_enabled=False,
            no_flow=False,
            no_back_flow=False,
            comp_from=self._oxy,
            comp_to=self._tubing_out,
            r_for=50.0,
            r_back=50.0,
            r_k=0.0,
        )

        # add the resistor to the list
        self._ecls_parts.append(self._oxy_tubing_out)

        self._return_cannula = self._model_engine.models["ECLS_RE"]

        self._return_cannula.init_model(
            is_enabled=False,
            no_flow=False,
            no_back_flow=False,
            comp_from=self._tubing_out,
            comp_to=self.return_site,
            r_for=return_res,
            r_back=return_res,
            r_k=0.0,
        )

        # add the resistor to the list
        self._ecls_parts.append(self._return_cannula)

        # initialize the pump
        self.init_pump()

    def set_rpm(self, new_rpm):
        if new_rpm > 0.0:
            self.pump_rpm = new_rpm

    def set_sweep_gas(self, new_sweep_gas):
        self.sweep_gas = new_sweep_gas

    def set_fio2(self, new_fio2):
        self.fio2_gas = new_fio2
        set_gas_composition(
            self._gas_in, self.fio2_gas, self.temp_gas, self.humidity_gas
        )

    def set_co2_flow(self, new_co2_flow):
        if new_co2_flow > 0.0:
            self.co2_gas_flow = new_co2_flow
            self.fico2_gas = (new_co2_flow * 0.001) / self.sweep_gas
        else:
            self.co2_gas_flow = self.fico2_gas_baseline * 1000
            self.fico2_gas = self.fico2_gas_baseline

        set_gas_composition(
            self._gas_in,
            self.fio2_gas,
            self.temp_gas,
            self.humidity_gas,
            self.fico2_gas,
        )

    def set_fico2(self, new_fico2):
        # calculate the co2 with normal fico2 of 0.000392
        # when sweep gas is 1 l/min then the co2_flow is = 0.000392 * 1 = 0.000392 l/min

        # calculate the ml
        self.fico2_gas = new_fico2

    def reconnect_drainage(self, comp):
        if self._model_engine.models[comp]:
            self.drainage_site = comp
            self._drainage_cannula.reconnect(comp, "ECLS_TUBIN")

    def reconnect_return(self, comp):
        if self._model_engine.models[comp]:
            self.return_site = comp
            self._return_cannula.reconnect("ECLS_TUBOUT", comp)

    def build_gas_part(self):
        self._gas_in = self._model_engine.models["ECLS_GASIN"]
        self._gas_in.init_model(
            is_enabled=False,
            fixed_composition=True,
            vol=5.4,
            u_vol=5.0,
            el_base=1000.0,
            el_k=0.0,
            pres_atm=self.pres_atm,
        )
        # calculate the current pressure
        self._gas_in.calc_model()
        # set the gas composition
        set_gas_composition(
            self._gas_in, self.fio2_gas, self.temp_gas, self.humidity_gas
        )
        # add to the vent parts array
        self._ecls_parts.append(self._gas_in)

        self._gas_oxy = self._model_engine.models["ECLS_GASOXY"]
        self._gas_oxy.init_model(
            is_enabled=False,
            fixed_composition=False,
            vol=0.1,
            u_vol=0.1,
            el_base=10000.0,
            el_k=0.0,
            pres_atm=self.pres_atm,
        )
        # calculate the current pressure
        self._gas_oxy.calc_model()
        # set the gas composition
        set_gas_composition(
            self._gas_oxy, self.fio2_gas, self.temp_gas, self.humidity_gas
        )
        # add to the vent parts array
        self._ecls_parts.append(self._gas_oxy)

        self._gas_out = self._model_engine.models["ECLS_GASOUT"]
        self._gas_out.init_model(
            is_enabled=False,
            fixed_composition=True,
            vol=5.0,
            u_vol=5.0,
            el_base=1000.0,
            el_k=0.0,
            pres_atm=self.pres_atm,
        )
        # calculate the current pressure
        self._gas_out.calc_model()
        # set the gas composition
        set_gas_composition(self._gas_out, 0.205, 20.0, 0.5)
        # add to the vent parts array
        self._ecls_parts.append(self._gas_out)

        # connect the parts
        self._gas_in_oxy = self._model_engine.models["ECLS_GASIN_OXY"]
        self._gas_in_oxy.init_model(
            is_enabled=False,
            no_flow=False,
            no_back_flow=False,
            comp_from=self._gas_in,
            comp_to=self._gas_oxy,
            r_for=2000.0,
            r_back=2000.0,
            r_k=0.0,
        )
        self._ecls_parts.append(self._gas_in_oxy)

        self._gas_oxy_out = self._model_engine.models["ECLS_OXY_GASOUT"]
        self._gas_oxy_out.init_model(
            is_enabled=False,
            no_flow=False,
            no_back_flow=False,
            comp_from=self._gas_oxy,
            comp_to=self._gas_out,
            r_for=50.0,
            r_back=50.0,
            r_k=0.0,
        )
        self._ecls_parts.append(self._gas_oxy_out)

    def build_gasexchanger(self):
        self._gasex = self._model_engine.models["ECLS_GASEX"]
        self._gasex.init_model(
            is_enabled=False,
            comp_blood=self._oxy,
            comp_gas=self._gas_oxy,
            dif_o2=self.diff_o2,
            dif_co2=self.diff_co2,
        )
        self._ecls_parts.append(self._gasex)

    def switch_ecls(self, state):
        # turn all on
        for ecls_part in self._ecls_parts:
            ecls_part.is_enabled = state

        # rebuild execution list
        self._model_engine.rebuildExecutionListFlag = True

        # turn ecls on
        self.ecls_running = state

        self._drainage_cannula.no_flow = not state
        self._return_cannula.no_flow = not state

    def switch_clamp(self, state):
        self.ecls_clamped = state

    def calc_volume(self, length, diameter):
        # return the volume in liters
        return math.pi * math.pow(0.5 * diameter, 2) * length * 1000.0

    def calc_resistance_tube(self, diameter, length, viscosity=6.0):
        # 1 Fr= 0.33 mm

        # resistance is calculated using Poiseuille's Law : R = (8 * n * L) / (PI * r^4)

        # we have to watch the units carefully where we have to make sure that the units in the formula are
        # resistance is in mmHg * s / l
        # L = length in meters from millimeters
        # r = radius in meters from millimeters
        # n = viscosity in centiPoise

        # convert viscosity from centiPoise to Pa * s
        n_pas = viscosity / 1000.0

        # convert the length to meters
        length_meters = length

        # calculate radius in meters
        radius_meters = diameter / 2

        # calculate the resistance    Pa *  / m3
        res = (8.0 * n_pas * length_meters) / (math.pi * math.pow(radius_meters, 4))

        # convert resistance of Pa/m3 to mmHg/l
        res = res * 0.00000750062
        return res
