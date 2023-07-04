from explain_core.base_models.TimeVaryingElastance import TimeVaryingElastance


class BloodTimeVaryingElastance(TimeVaryingElastance):

    def __init__(self, **args):
        # initialize the super class (capacitance and basemodel) which sets the mode properties
        super().__init__(**args)
