#include <stdlib.h>
#include <float.h>
#include <time.h>
double fRand(double fMin, double fMax);
double inject(int r, double i);
double error_rate = .1;

class sRandInitializer {
public: 
  sRandInitializer() {
    srand(time(NULL));
  }
};

static sRandInitializer *aVar = new sRandInitializer();

double inject(int r, double i)
{
  double rate = error_rate*r/100;
  if((double)rand() / RAND_MAX * 100 <rate){
      return fRand(DBL_MIN, DBL_MAX);
    }
  else{
      return i;
      }
}

double fRand(double fMin, double fMax)
  {
      double f = (double)rand() / RAND_MAX;
      double random = fMin + f * (fMax - fMin);
      return random;
  }