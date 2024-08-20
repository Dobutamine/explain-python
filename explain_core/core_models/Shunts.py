import math


class Shunts:
    # static properties
    model_type: str = "Shunts"
    model_interface: list = []

    def __init__(self, model_ref: object, name: str = ""):
        # independent properties
        self.name: str = name
        self.description: str = ""
        self.is_enabled: bool = False
        self.dependencies: list = []
        self.viscosity = 6.0
        self.fo_enabled = True
        self.fo = "FO"
        self.fo_diameter = 3.0
        self.fo_length = 2.0
        self.fo_res_backflow_factor = 10.0
        self.fo_res_forwardflow_factor = 1.0
        self.fo_r_k = 1000
        self.vsd = "VSD"
        self.vsd_enabled = False
        self.vsd_diameter = 2.0
        self.vsd_length = 2.0
        self.vsd_res_backflow_factor = 1.0
        self.vsd_r_k = 1000
        self.da = "DA"
        self.da_in = "DA_IN"
        self.da_out = "DA_OUT"
        self.da_enabled = True
        self.da_vol = 0.0002
        self.da_u_vol = 0.0002
        self.da_el_base = 100000
        self.da_el_k = 1000.0
        self.da_diameter = 0.1
        self.da_length = 10.0
        self.da_in_res = 300
        self.da_in_res_backflow_factor = 1.0
        self.da_in_r_k = 1000
        self.da_out_res = 10000000
        self.da_out_res_backflow_factor = 1.0
        self.da_out_r_k = 1000
        self.ips_enabled = True
        self.ips = "IPS"
        self.ips_res = 30719
        self.ips_res_factor = 1.0
        self.ips_r_k = 1000
        self.ips_res_backflow_factor = 1.0

        # dependent properties
        self.da_vol = 0.0
        self.da_in_res = 300
        self.da_out_res = 10000000

        self.da_flow = 0.0
        self.da_velocity = 0.0

        self.ips_flow = 0.0
        self.ips_velocity = 0.0
        self.fo_flow = 0.0
        self.fo_velocity = 0.0
        self.fo_res = 10000000
        self.vsd_flow = 0.0
        self.vsd_velocity = 0.0
        self.vsd_res = 10000000

        # local properties
        self._model_engine: object = model_ref
        self._is_initialized: bool = False
        self._t: float = model_ref.modeling_stepsize
        self._ips = None
        self._da = None
        self._da_in = None
        self._da_out = None
        self._vsd = None
        self._fo = None
        self._shunts = []

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # build the shunts
        self.init_da()
        self.init_fo()
        self.init_ips()
        self.init_vsd()

        # flag that the model is initialized
        self._is_initialized = True

    # this method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # actual model calculations are done here
    def calc_model(self):
        # set the enabled flows
        self._da_in.no_flow = not self.da_enabled
        self._da_out.no_flow = not self.da_enabled
        self._da_in.is_enabled = self.da_enabled
        self._da_out.is_enabled = self.da_enabled
        self._da.is_enabled = self.da_enabled

        self._ips.is_enabled = self.ips_enabled
        self._ips.no_flow = not self.ips_enabled

        self._vsd.is_enabled = self.vsd_enabled
        self._vsd.no_flow = not self.vsd_enabled

        self._fo.is_enabled = self.fo_enabled
        self._fo.no_flow = not self.fo_enabled

        if self._model_engine.models["Blood"]:
            self.viscosity = self._model_engine.models["Blood"].viscosity

        # set the shunts properties
        if self.da_enabled:
            self.da_out_res = self.calc_resistance(
                self.da_diameter, self.da_length, self.viscosity
            )
            self._da.el_base = self.da_el_base
            self._da.u_vol = self.da_u_vol
            self._da.el_k = self.da_el_k
            self._da_in.r_for = self.da_in_res
            self._da_in.r_back = self.da_in_res
            self._da_in.r_k = self.da_in_r_k
            self._da_out.r_for = self.da_out_res
            self._da_out.r_back = self.da_out_res
            self._da.r_k = self.da_out_r_k
        else:
            self._da.flow = 0.0
            self.da_velocity = 0.0

        if self.fo_enabled:
            self.fo_res = self.calc_resistance(
                self.fo_diameter, self.fo_length, self.viscosity
            )
            self._fo.r_for = self.fo_res * self.fo_res_forwardflow_factor
            # RA -> LA
            self._fo.r_back = self.fo_res * self.fo_res_backflow_factor
            # LA -> RA
            self._fo.r_k = self.fo_r_k
        else:
            self._fo.flow = 0.0
            self.fo_velocity = 0.0

        if self.vsd_enabled:
            self.vsd_res = self.calc_resistance(
                self.vsd_diameter, self.vsd_length, self.viscosity
            )
            self._vsd.r_for = self.vsd_res
            self._vsd.r_back = self.vsd_res * self.vsd_res_backflow_factor
            self._vsd.r_k = self.vsd_r_k
        else:
            self._vsd.flow = 0.0
            self.vsd_velocity = 0.0

        if self.ips_enabled:
            self._ips_r_for = self.ips_res
            self._ips.r_back = self.ips_res
            self._ips.r_for_factor = self.ips_res_factor
            self._ips.r_back_factor = self.ips_res_backflow_factor
            self._ips.r_k = self.ips_r_k
        else:
            self._ips.flow = 0.0

        self.da_flow = self._da_out.flow
        # calculate the velocity = flow_rate (in m^3/s) / (pi * radius^2) in m/s
        da_area = math.pow((self.da_diameter * 0.001) / 2.0, 2.0) * math.pi
        # in m^2
        # flow is in l/s
        if da_area > 0:
            self.da_velocity = ((self.da_flow * 0.001) / da_area) * 1.4

        self.ips_flow = self._ips.flow

        self.fo_flow = self._fo.flow
        # calculate the velocity = flow_rate (in m^3/s) / (pi * radius^2) in m/s
        fo_area = math.pow((self.fo_diameter * 0.001) / 2.0, 2.0) * math.pi
        # in m^2
        # flow is in l/s
        if fo_area > 0:
            self.fo_velocity = (self.fo_flow * 0.001) / fo_area

        self.vsd_flow = self._vsd.flow
        # calculate the velocity = flow_rate (in m^3/s) / (pi * radius^2) in m/s
        vsd_area = math.pow((self.vsd_diameter * 0.001) / 2.0, 2.0) * math.pi
        # in m^2
        # flow is in l/s
        if vsd_area > 0:
            self.vsd_velocity = (self.vsd_flow * 0.001) / vsd_area

    def init_da(self):
        # define a blood capacitance which represents the ductus arteriosus
        self._da = self._model_engine.models[self.da]
        self._da.is_enabled = self.da_enabled
        self._da.fixed_composition = False
        self._da.vol = self.da_vol
        self._da.u_vol = self.da_u_vol
        self._da.el_base = self.da_el_base
        self._da.el_k = self.da_el_k

        # set the electrolytes
        self._da.solutes = {**self._model_engine.models["AA"].solutes}
        self._da.aboxy = {**self._model_engine.models["AA"].aboxy}
        # calculate the starting pressure
        self._da.calc_model()
        # add the shunt to the list
        self._shunts.append(self._da)

        # connect the ductus
        self._da_in = self._model_engine.models[self.da_in]
        self._da_in.is_enabled = self.da_enabled
        self._da_in.no_flow = False
        self._da_in.no_back_flow = False
        self._da_in.r_for = self.da_in_res
        self._da_in.r_back = self.da_in_res * self.da_in_res_backflow_factor
        self._da_in.r_k = self.da_in_r_k
        # add the shunt to the list
        self._shunts.append(self._da_in)

        self._da_out = self._model_engine.models[self.da_out]
        self._da_out.is_enabled = self.da_enabled
        self._da_out.no_flow = False
        self._da_out.no_back_flow = False
        self._da_out.r_for = self.da_out_res
        self._da_out.r_back = self.da_out_res * self.da_out_res_backflow_factor
        self._da_out.r_k = self.da_out_r_k
        # add the shunt to the list
        self._shunts.append(self._da_out)

    def init_fo(self):
        self._fo = self._model_engine.models[self.fo]
        self._fo.is_enabled = self.fo_enabled
        self._fo.no_flow = False
        self._fo.no_back_flow = False
        self._fo.r_for = self.fo_res
        self._fo.r_back = self.fo_res * self.fo_res_backflow_factor
        self._fo.r_k = self.ips_r_k
        # add the shunt to the list
        self._shunts.append(self._fo)

    def init_vsd(self):
        self._vsd = self._model_engine.models[self.vsd]
        self._vsd.is_enabled = self.vsd_enabled
        self._vsd.no_flow = False
        self._vsd.no_back_flow = False
        self._vsd.r_vsdr = self.vsd_res
        self._vsd.r_back = self.vsd_res * self.vsd_res_backflow_factor
        self._vsd.r_k = self.ips_r_k
        # add the shunt to the list
        self._shunts.append(self._vsd)

    def init_ips(self):
        self._ips = self._model_engine.models[self.ips]
        self._ips.is_enabled = self.ips_enabled
        self._ips.no_flow = False
        self._ips.no_back_flow = False
        self._ips.r_for = self.ips_res * self.ips_res_factor
        self._ips.r_back = self.ips_res * self.ips_res_backflow_factor
        self._ips.r_k = self.ips_r_k
        # add the shunt to the list
        self._shunts.append(self._ips)

    def calc_resistance(self, diameter, length, viscosity=6.0):
        if diameter > 0.0 and length > 0.0:
            # resistance is calculated using Poiseuille's Law : R = (8 * n * L) / (PI * r^4)

            # we have to watch the units carefully where we have to make sure that the units in the formula are
            # resistance is in mmHg * s / l
            # L = length in meters from millimeters
            # r = radius in meters from millimeters
            # n = viscosity in centiPoise

            # convert viscosity from centiPoise to Pa * s
            n_pas = viscosity / 1000.0

            # convert the length to meters
            length_meters = length / 1000.0

            # calculate radius in meters
            radius_meters = diameter / 2 / 1000.0

            # calculate the resistance    Pa *  / m3
            res = (8.0 * n_pas * length_meters) / (math.pi * math.pow(radius_meters, 4))

            # convert resistance of Pa/m3 to mmHg/l
            res = res * 0.00000750062
            return res
        else:
            return 100000000
