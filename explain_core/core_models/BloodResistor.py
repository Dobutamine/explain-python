from explain_core.base_models.Resistor import Resistor


class BloodResistor(Resistor):
    def calc_model(self) -> None:
        super().calc_model()
