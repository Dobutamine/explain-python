# include "blood_composition.h"
# include <stdlib.h>
# include <math.h>
#include <stdbool.h>


void swap(double *ax, double *bx) {
    double temp = *ax;
    *ax = *bx;
    *bx = temp;
}

double BrentRootFinding(DoubleFunction f, double x0, double x1, int maxIter, double tolerance) {
    double fx0 = f(x0);
    double fx1 = f(x1);

    if (fx0 * fx1 > 0)
        return -1;

    if (fabs(fx0) < fabs(fx1)) {
        swap(&x0, &x1);
        swap(&fx0, &fx1);
    }

    double x2 = x0;
    double fx2 = fx0;
    double d = 0;
    double fnew = 0;

    bool mflag = true;
    int stepsTaken = 0;

    while (stepsTaken < maxIter) {
        if (fabs(fx0) < fabs(fx1)) {
            swap(&x0, &x1);
        }
        
        fx0 = f(x0);
        fx1 = f(x1);
        fx2 = f(x2);

        double L0, L1, L2, newPoint;
        if (fx0 != fx2 && fx1 != fx2) {
            L0 = x0 * fx1 * fx2 / ((fx0 - fx1) * (fx0 - fx2));
            L1 = x1 * fx0 * fx2 / ((fx1 - fx0) * (fx1 - fx2));
            L2 = x2 * fx1 * fx0 / ((fx2 - fx0) * (fx2 - fx1));
            newPoint = L0 + L1 + L2;
        }
        else {
            newPoint = x1 - (fx1 * (x1 - x0) / (fx1 - fx0));
        }

        if (newPoint < (3 * x0 + x1) / 4 || newPoint > x1 ||
            (mflag && fabs(newPoint - x1) >= fabs(x1 - x2) / 2) ||
            (!mflag && fabs(newPoint - x1) >= fabs(x2 - d) / 2) ||
            (mflag && fabs(x1 - x2) < tolerance) ||
            (!mflag && fabs(x2 - d) < tolerance)) {
            newPoint = (x0 + x1) / 2;
            mflag = true;
        }
        else {
            mflag = false;
        }

        fnew = f(newPoint);
        d = x2;
        x2 = x1;

        if ((fx0 * fnew) < 0) {
            x1 = newPoint;
        }
        else {
            x0 = newPoint;
        }

        stepsTaken++;

        if (fabs(fnew) < tolerance) {
            return newPoint;
        }

    }

    return -1; // Failed to find a root within the maximum number of iterations
}

bloodResult GetBloodComposition(
                    double _to2,
                    double _tco2,
                    double _sid,
                    double _albumin,
                    double _phosphates,
                    double _uma,
                    double _hemoglobin,
                    double _dpg,
                    double _temp) {
    // declare a struct holding the result
    bloodResult result;

    // set the valid flag to false;
    result.valid_o2 = 0;
    result.valid_ab = 0;

    // get the independent parameters for the acidbase routine
    tco2 = _tco2;
    sid=_sid;
    albumin = _albumin;
    phosphates =  _phosphates;
    uma = _uma;

    // now try to find the hydrogen concentration at the point where the net charge of the plasma is zero within limits of the brent accuracy
    double hp = BrentRootFinding(NetChargePlasma, left_hp, right_hp, max_iterations, brent_accuracy);

    // check whether there is a valid result
    if (hp > 0) {
        result.valid_ab = 1;
        // process the result
        ph = (-log10(hp / 1000));
        result.ph = ph;
        result.pco2 = pco2;
        result.hco3 = hco3;
        result.be = be;
        result.steps_ab = steps;
    } else {
        // as the acidbase is not valid try to calculate the po2 and so2 assuming normal acidbase values
        result.valid_ab = 0;
        ph = 7.40;
        pco2 = 40.0;
        hco3 = 25.0;
        be = 0.0;
    }

    // get the independent parameters for the oxygenation routine
    to2 = _to2;
    hemoglobin = _hemoglobin;
    dpg = _dpg;
    temp =  _temp;

    // calculate the po2 from the to2 using a brent root finding function and oxygen dissociation curve
    po2 = BrentRootFinding(OxygenContent, left_o2, right_o2, max_iterations, brent_accuracy);

    result.steps_o2 = steps;
    if (po2 > 0) {
        result.valid_o2 = 1;
        result.po2 = po2;
        result.so2 = so2 * 100.0;

    };

    return result;
}

double NetChargePlasma(double hp_estimate) {
    // Calculate the pH based on the current hp estimate
    double ph = -log10(hp_estimate / 1000.0);

    // Calculate the plasma co2 concentration based on the total co2 in the plasma, hydrogen concentration, and the constants Kc and Kd
    double cco2p = tco2 / (1.0 + kc / hp_estimate + (kc * kd) / pow(hp_estimate, 2.0));

    // Calculate the plasma hco3(-) concentration (bicarbonate)
    double hco3p = (kc * cco2p) / hp_estimate;

    // Calculate the plasma co3(2-) concentration (carbonate)
    double co3p = (kd * hco3p) / hp_estimate;

    // Calculate the plasma OH(-) concentration (water dissociation)
    double ohp = kw / hp_estimate;

    // Calculate the pco2 of the plasma
    double pco2p = cco2p / alpha_co2p;

    // Calculate the weak acids (albumin and phosphates)
    double a_base = albumin * (0.123 * ph - 0.631) +
                    phosphates * (0.309 * ph - 0.469);

    // Calculate the net charge of the plasma
    double netcharge = hp_estimate + sid - hco3p - 2.0 * co3p - ohp - a_base - uma;

    // Calculate the base excess according to the van Slyke equation
    be = (hco3p - 25.1 + (2.3 * hemoglobin + 7.7) * (ph - 7.4)) * (1.0 - 0.023 * hemoglobin);

    // Store the calculated values
    pco2 = pco2p;
    hco3 = hco3p;

    // Return the net charge
    return netcharge;
}

double OxygenContent(double po2Estimate) {
    // calculate the saturation from the current po2 from the current po2 estimate
    so2 = OxygenDissociationCurve(po2Estimate);

    // calculate the to2 from the current po2 estimate
    // INPUTS: po2 in mmHg, so2 in fraction, hemoglobin in mmol/l
    // convert the hemoglobin unit from mmol/l to g/dL  (/ 0.6206)
    // convert to output from ml O2/dL blood to ml O2/l blood (* 10.0)
    double to2_new_estimate = (0.0031 * po2Estimate + 1.36 * (hemoglobin / 0.6206) * so2) * 10.0;

    // conversion factor for converting ml O2/l to mmol/l
    double mmol_to_ml = (gas_constant * (273.15 + temp)) / 760.0;

    // convert the ml O2/l to mmol/l
    to2_new_estimate = to2_new_estimate / mmol_to_ml;

    // calculate the difference between the real to2 and the to2 based on the new po2 estimate and return it to the brent root finding function
    double dto2 = to2 - to2_new_estimate;

    return dto2;
}

double OxygenDissociationCurve(double po2Estimate) {
    // calculate the saturation from the po2 depending on the ph,be, temperature and dpg level.
    double a = 1.04 * (7.4 - ph) + 0.005 * be + 0.07 * (dpg - 5.0);
    double b = 0.055 * (temp + 273.15 - 310.15);
    double x0 = 1.875 + a + b;
    double h0 = 3.5 + a;
    double x = log((po2Estimate * 0.1333));  // po2 in kPa
    double y = x - x0 + h0 * tanh(0.5343 * (x - x0)) + 1.875;

    // return the o2 saturation in fraction so 0.98
    return 1.0 / (exp(-y) + 1.0);
}

