// brent constants
static double brent_accuracy = 1e-6;
static double max_iterations = 100;
static double gas_constant = 62.36367;

// acidbase constants
static double kw = 0.000000000025119;
static double kc = 0.000794328235;
static double kd = 0.000000060255959;
static double alpha_co2p = 0.03067;
static double left_hp = 0.000015848931925;
static double right_hp = 0.000316227766017;
static double left_o2 = 0.01;
static double right_o2 = 1000.0;

static double tco2 = 0.0;
static double pco2 = 0.0;
static double hco3 = 0.0;
static double sid = 0.0;
static double albumin = 0.0;
static double phosphates = 0.0;
static double uma = 0.0;
static double dpg = 5;
static double hemoglobin = 8.0;
static double temp = 37;
static double to2 = 0.0;
static double ph = 0.0;
static double be = 0.0;
static double po2 = 0.0;
static double so2 = 0.0;
static double steps = 0.0;

// Function type definition for functions that take a double and return a double
typedef double (*DoubleFunction)(double);

typedef struct  {
    int valid_ab;
    int valid_o2;
    double po2;
    double so2;
    double ph;
    double pco2;
    double hco3;
    double be;
    double sid_app;
    double steps_ab;
    double steps_o2;
} bloodResult;

bloodResult GetBloodComposition(
        double _to2,
        double _tco2,
        double _sid,
        double _albumin,
        double _phosphates,
        double _uma,
        double _hemoglobin,
        double _dpg,
        double _temp);
double NetChargePlasma(double hp_estimate);
double OxygenContent(double po2Estimate);
double OxygenDissociationCurve(double po2Estimate);
void swap(double *a, double *b);
double BrentRootFinding(DoubleFunction f, double x0, double x1, int maxIter, double tolerance);
