from explain_core.base_models.Capacitance import Capacitance


class Container(Capacitance):

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # calculate the volume of the container
        self.calc_volume()

        # do the cap actions
        super().calc_model()

    def calc_volume(self) -> None:
        pass
