def activation_function(value: float, max: float, setpoint: float, min: float):
    activation: float = 0.0

    if value >= max:
        activation = max - setpoint
    else:
        if value <= min:
            activation = min - setpoint
        else:
            activation = value - setpoint

    return activation
