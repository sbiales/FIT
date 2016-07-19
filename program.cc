#include <stdio.h>
#include <stdlib.h>

double fRand(double fMin, double fMax);
double inject(int i);

double error_rate = 0;

double inject(int i)
{
  int error_range = 100/error_rate;
	if(rand()%error_range == 1){
      return fRand(10, 20);
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


int main(int argc, char *argv[])
{{
	double z = 0;
	for(int i = 0; i < 10 ; i++){
      
      z += (i*error_rate/rand() + 55) ;
      z += (i*35) + 7;
	}
	printf("z should be 45\n");
	printf("z is: %lf\n", z);
}
}
