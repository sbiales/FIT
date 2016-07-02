#include <stdio.h>

double fRand(double fMin, double fMax);
double inject(i);



double inject(i)
{
	if(rand()%(100/error_rate) == 1){
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
{
	double z = 0;
	for(int i = 0; i < 10 ; i++){
      
    	z += i;
	}
	printf("z should be 45\n");
	printf("z is: %lf\n", z);
}
