#include <stdlib.h>
#include <float.h>
#include <time.h>
#include <stdio.h>
double fRand(double fMin, double fMax);
double inject(double i);
double error_rate = 50;

class sRandInitializer {
public: 
  sRandInitializer() {
    srand(time(NULL));
  }
};

static sRandInitializer *aVar = new sRandInitializer();

double inject(double i)
{
  if((double)rand() / RAND_MAX * 100 <error_rate){
      printf("Perturbed\n");
      return fRand(DBL_MIN, DBL_MAX);
    }
  else{
    printf("Not Perturbed\n");
      return i;
      }
}

double fRand(double fMin, double fMax)
  {
      double f = (double)rand() / RAND_MAX;
      double random = fMin + f * (fMax - fMin);
      return random;
  }