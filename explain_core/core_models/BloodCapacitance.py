from explain_core.base_models.Capacitance import Capacitance


class BloodCapacitance(Capacitance):

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # do the cap actions
        super().calc_model()
