from explain_core.base_models.BaseModel import BaseModel
from explain_core.base_models.TimeVaryingElastance import TimeVaryingElastance


class Heart(BaseModel):
    # independent variables
    pq_time: float = 0.0
    qrs_time: float = 0.0
    qt_time: float = 0.0

    # dependent variables
    cqt_time: float = 0.0

    # local variables
    _la: TimeVaryingElastance = {}
    _lv: TimeVaryingElastance = {}
    _ra: TimeVaryingElastance = {}
    _rv: TimeVaryingElastance = {}

    def init_model(self, model: object) -> bool:
        # init the parent class
        super().init_model(model)

        # get a reference to the heart models
        self._la = self._model.models[self.left_atrium]
        self._ra = self._model.models[self.right_atrium]
        self._lv = self._model.models[self.left_ventricle]
        self._rv = self._model.models[self.right_ventricle]

    def calc_model(self) -> None:
        return super().calc_model()
