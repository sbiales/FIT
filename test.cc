#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{{
  // this is for test purposes
	double z = 0;
  double y = 0;
	for(int i = 0; i < 10 ; i++){
      //also for test purposes
      z += i;
	}
      y += 872; //for test purposes
	printf("z should be 45\n");
	printf("z is: %lf\n", z);
}
}

void test() {
  double x = 12;

  /*
  for(int i = 0; i < 10 ; i++)
  {
    q += WRONG;
  }
  */
  for(int i = 0; i < 10 ; i++)
  {
    x += i;
}}