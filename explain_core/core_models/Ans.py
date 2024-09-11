class Ans:
    # Static properties
    model_type = "Ans"
    model_interface = [
        {
            "target": "is_enabled",
            "caption": "is enabled",
            "type": "boolean",
            "default": True,
        },
        {
            "target": "ans_active",
            "caption": "ans active",
            "type": "boolean",
            "default": True,
        },
    ]

    def __init__(self, model_ref, name=""):
        # Independent properties
        self.name = name
        self.description = ""
        self.is_enabled = False
        self.dependencies = []
        self.ans_active = True

        # Sensory inputs
        self.pathways = []

        # Local properties
        self._model_engine = model_ref
        self._t = model_ref.modeling_stepsize
        self._is_initialized = False
        self._pathways = {}
        self._update_window = 0.015
        self._update_counter = 0.0

    def init_model(self, **args: dict[str, any]):
        # set the values of the independent properties
        for key, value in args.items():
            setattr(self, key, value)

        # Initialize the pathways with references to the necessary models
        for pathway in self.pathways:
            self._pathways[pathway["name"]] = {
                "sensor": self._model_engine.models[pathway["sensor"]],
                "effector": self._model_engine.models[pathway["effector"]],
                "active": pathway["active"],
                "effect_weight": pathway["effect_weight"],
                "pathway_activity": 0.0,
            }

        # Flag that the model is initialized
        self._is_initialized = True

    # This method is called during every model step by the model engine
    def step_model(self):
        if self.is_enabled and self._is_initialized:
            self.calc_model()

    # Actual model calculations are done here
    def calc_model(self):
        self._update_counter += self._t
        if self._update_counter >= self._update_window:
            self._update_counter = 0.0

            # Connect the sensor with the effector
            for pathway_name, pathway in self._pathways.items():
                if pathway["active"]:
                    pathway["effector"].update_effector(
                        pathway["sensor"].firing_rate,
                        pathway["effect_weight"]
                    )
