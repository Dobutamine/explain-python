import math
from explain_core.base_models.BaseModel import BaseModel


class Blood(BaseModel):
    # set the brent root finding properties
    brent_accuracy = 1e-8
    max_iterations = 100.0
    steps = 0

    # acidbase constants
    kw = math.pow(10.0, -13.6) * 1000.0
    kc = math.pow(10.0, -6.1) * 1000.0
    kd = math.pow(10.0, -10.22) * 1000.0
    alpha_co2p = 0.03067
    left_hp = math.pow(10.0, -7.8) * 1000.0
    right_hp = math.pow(10.0, -6.5) * 1000.0

    # acidbase
    sid = 41.6
    albumin = 30
    phosphates = 1.8
    uma = 4

    # oxygenation constants
    left_o2 = 0.01
    right_o2 = 100
    alpha_o2p = 0.0095
    mmoltoml = 22.2674

    # oxygenation
    dpg = 5
    hemoglobin = 10
    temp = 37

    # local parameters
    _update_interval = 0.015
    _update_counter = 0.0

    def init_model(self, model: object) -> bool:
        super().init_model(model)

        # find all models containing blood and set it's solutes
        for model in self._model.models.values():
            if model.model_type == "BloodCapacitance" or model.model_type == "BloodTimeVaryingElastance":
                # fill the solutes
                model.solutes = {**self.solutes}
                model.acidbase = {**self.acidbase}
                model.oxy = {**self.oxy}

        return self._is_initialized

    def calc_acidbase_from_tco2(self, comp):
        # calculate the apparent strong ion difference (SID) in mEq/l
        # comp.sid = comp.sodium + comp.potassium + 2 * comp.calcium + 2 * \
        #     comp.magnesium - comp.chloride - comp.lactate - comp.urate

        # get the total co2 concentration in mmol/l
        self.tco2 = comp.solutes['tco2']

        # store the apparent SID
        self.sid = comp.acidbase['sid']

        # get the albumin concentration in g/l
        self.albumin = comp.acidbase['albumin']

        # get the inorganic phosphates concentration in mEq/l
        self.phosphates = comp.acidbase['phosphates']

        # get the unmeasured anions in mEq/l
        self.uma = comp.acidbase['uma']

        # # get the hemoglobin concentration in mmol/l
        self.hemoglobin = comp.oxy['hemoglobin']

        # now try to find the hydrogen concentration at the point where the net charge of the plasma is zero within limits of the brent accuracy
        hp = self.brent_root_finding(
            self.net_charge_plasma, self.left_hp, self.right_hp, self.max_iterations, self.brent_accuracy)

        # if this hydrogen concentration is found then store it inside the compartment
        if (hp > 0):
            # calculate the pH and store it inside the compartment
            comp.acidbase['ph'] = (-math.log10(hp / 1000))
            comp.acidbase['pco2'] = self.pco2
            comp.acidbase['hco3'] = self.hco3
            comp.acidbase['be'] = self.be

    def net_charge_plasma(self, hp_estimate):
        # calculate the ph based on the current hp estimate
        ph = -math.log10(hp_estimate / 1000.0)

        # we do know the total co2 concentration but we now have to find out the distribution of the co2 where tco2 = cco2 + hco3 + cco3

        # cco2 = plasma concentration of co2 -> charge neutral
        # hco3 = plasma concentration of bicarbonate -> charge 1-
        # cco3 = plasma concentration of carbonate -> charge 2-

        # the distribution is described by
        # pH = pKc * HCO3 + log10(hco3 / cco2)
        # pH = pKd + log10(cco3 / hco3)

        # calculate the plasma co2 concentration based on the total co2 in the plasma, hydrogen concentration and the constants Kc and Kd
        cco2p = self.tco2 / (1.0 + self.kc / hp_estimate +
                             (self.kc * self.kd) / math.pow(hp_estimate, 2.0))

        # calculate the plasma hco3(-) concentration (bicarbonate)
        hco3p = (self.kc * cco2p) / hp_estimate

        # calculate the plasma co3(2-) concentration (carbonate)
        co3p = (self.kd * hco3p) / hp_estimate

        # calculate the plasma OH(-) concentration (water dissociation)
        ohp = self.kw / hp_estimate

        # calculate the pco2 of the plasma
        pco2p = cco2p / self.alpha_co2p

        # calculate the weak acids (albumin and phosphates)
        # Clin Biochem Rev 2009 May; 30(2): 41-54
        a_base = self.albumin * (0.123 * ph - 0.631) + \
            self.phosphates * (0.309 * ph - 0.469)
        # alb_base = self.albumin * (0.378 / (1.0 + math.pow(10, 7.1 - ph)))
        # phos_base = self.phosphates / (1.0 + math.pow(10, 6.8 - ph))

        # calculate the net charge of the plasma. If the netcharge is zero than the current hp_estimate is the correct one.
        netcharge = hp_estimate + self.sid - hco3p - 2.0 * co3p - ohp - a_base - self.uma

        # calculate the base excess according to the van Slyke equation
        self.be = (hco3p - 24.4 + (2.3 * self.hemoglobin + 7.7)
                   * (ph - 7.4)) * (1.0 - 0.023 * self.hemoglobin)

        # calculate the pco2 and store the plasma hco3
        self.pco2 = pco2p
        self.hco3 = hco3p
        self.cco3 = co3p
        self.cco2 = cco2p

        # return the net charge to the brent function
        return netcharge

    def calc_oxygenation_from_to2(self, comp):
        # get the for the oxygenation independent parameters from the component
        self.to2 = comp.solutes['to2']
        self.ph = comp.acidbase['ph']
        self.be = comp.acidbase['be']
        self.dpg = comp.oxy['dpg']
        self.hemoglobin = comp.oxy['hemoglobin']
        self.temp = comp.oxy['temp']

        # calculate the po2 from the to2 using a brent root finding function and oxygen dissociation curve
        self.po2 = self.brent_root_finding(
            self.oxygen_content, self.left_o2, self.right_o2, self.max_iterations, self.brent_accuracy)

        # if a po2 is found then store the po2 and so2 into the component
        if (self.po2 > 0):
            # convert the po2 to mmHg
            comp.oxy['po2'] = self.po2 / 0.1333
            comp.oxy['so2'] = self.so2 * 100

    def oxygen_content(self, po2_estimate):
        # calculate the saturation from the current po2 from the current po2 estimate
        self.so2 = self.oxygen_dissociation_curve(po2_estimate)

        # calculate the to2 from the current po2 estimate
        # convert the hemoglobin unit from mmol/l to g/dL
        # convert the po2 from kPa to mmHg
        # convert to output from ml O2/dL blood to ml O2/l blood
        to2_new_estimate = (0.0031 * (po2_estimate / 0.1333) +
                            1.36 * (self.hemoglobin / 0.6206) * self.so2) * 10.0

        # convert the ml O2/l to mmol/l
        to2_new_estimate = to2_new_estimate / self.mmoltoml

        # calculate the difference between the real to2 and the to2 based on the new po2 estimate and return it to the brent root finding function
        dto2 = self.to2 - to2_new_estimate

        return dto2

    def oxygen_dissociation_curve(self, po2):
        # calculate the saturation from the po2 depending on the ph,be, temperature and dpg level.
        a = 1.04 * (7.4 - self.ph) + 0.005 * self.be + 0.07 * (self.dpg - 5.0)
        b = 0.055 * (self.temp + 273.15 - 310.15)
        y0 = 1.875
        x0 = 1.875 + a + b
        h0 = 3.5 + a
        k = 0.5343
        x = math.log(po2, math.e)
        y = x - x0 + h0 * math.tanh(k * (x - x0)) + y0

        # return the o2 saturation
        return 1.0 / (math.pow(math.e, -y) + 1.0)

    def brent_root_finding(self, f, x0, x1, max_iter, tolerance):
        steps = 0

        fx0 = f(x0)
        fx1 = f(x1)

        if (fx0 * fx1) > 0:
            return -1

        if abs(fx0) < abs(fx1):
            x0, x1 = x1, x0
            fx0, fx1 = fx1, fx0

        x2, fx2 = x0, fx0

        mflag = True
        steps_taken = 0

        while steps_taken < max_iter and abs(x1 - x0) > tolerance:
            fx0 = f(x0)
            fx1 = f(x1)
            fx2 = f(x2)

            if fx0 != fx2 and fx1 != fx2:
                L0 = (x0 * fx1 * fx2) / ((fx0 - fx1) * (fx0 - fx2))
                L1 = (x1 * fx0 * fx2) / ((fx1 - fx0) * (fx1 - fx2))
                L2 = (x2 * fx1 * fx0) / ((fx2 - fx0) * (fx2 - fx1))
                new = L0 + L1 + L2

            else:
                new = x1 - ((fx1 * (x1 - x0)) / (fx1 - fx0))

            if ((new < ((3 * x0 + x1) / 4) or new > x1) or
                    (mflag == True and (abs(new - x1)) >= (abs(x1 - x2) / 2)) or
                    (mflag == False and (abs(new - x1)) >= (abs(x2 - d) / 2)) or
                    (mflag == True and (abs(x1 - x2)) < tolerance) or
                    (mflag == False and (abs(x2 - d)) < tolerance)):
                new = (x0 + x1) / 2
                mflag = True

            else:
                mflag = False

            fnew = f(new)
            d, x2 = x2, x1

            if (fx0 * fnew) < 0:
                x1 = new
            else:
                x0 = new

            if abs(fx0) < abs(fx1):
                x0, x1 = x1, x0

            steps_taken += 1

        if (steps_taken >= max_iter):
            return -1
        else:
            steps = steps_taken
            return x1
