from explain_core.base_models.TimeVaryingElastance import TimeVaryingElastance
from explain_core.base_models.Capacitance import Capacitance


class BloodTimeVaryingElastance(TimeVaryingElastance):

    # override the calc_model method as the blood capacitance has some specific actions
    def calc_model(self) -> None:
        # do the cap actions
        super().calc_model()

    # override the volume_in method as all the blood solutes have to be changed to
    def volume_in(self, dvol: float, model_from: Capacitance) -> None:
        super().volume_in(dvol)
