def brent_root_finding(f, x0, x1, max_iter, tolerance) -> float:
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
    d = 0
    fnew = 0

    while steps_taken < max_iter:
        if abs(fx0) < abs(fx1):
            x0, x1 = x1, x0

        fx0 = f(x0)
        fx1 = f(x1)
        fx2 = f(x2)

        if fx0 != fx2 and fx1 != fx2:
            L0 = x0 * fx1 * fx2 / ((fx0 - fx1) * (fx0 - fx2))
            L1 = x1 * fx0 * fx2 / ((fx1 - fx0) * (fx1 - fx2))
            L2 = x2 * fx1 * fx0 / ((fx2 - fx0) * (fx2 - fx1))
            new = L0 + L1 + L2
        else:
            new = x1 - (fx1 * (x1 - x0) / (fx1 - fx0))

        if (new < (3 * x0 + x1) / 4 or new > x1 or
            (mflag and abs(new - x1) >= abs(x1 - x2) / 2) or
            (not mflag and abs(new - x1) >= abs(x2 - d) / 2) or
            (mflag and abs(x1 - x2) < tolerance) or
                (not mflag and abs(x2 - d) < tolerance)):
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

        steps_taken += 1

        if abs(fnew) < tolerance:
            return new

    return -1  # Failed to find a root within the maximum number of iterations
