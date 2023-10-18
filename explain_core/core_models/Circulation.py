from explain_core.base_models.BaseModel import BaseModel

class Circulation(BaseModel):
    # independent parameters
    

    def init_model(self, model: object) -> bool:
        # initialize the base model
        super().init_model(model)

        # signal that the ventilator model is initialized and return it
        self._is_initialized = True
        return self._is_initialized

    def change_pvr(self, factor):
        pass

    def change_svr(self, factor):
        pass

    def change_venpool(self, factor):
        pass

    def change_arterial_compliance(self, factor):
        pass

    def change_venous_compliance(self, factor):
        pass
    


