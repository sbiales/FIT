#include <pthread.h>
#include <math.h>
#include <stdio.h>
//#include "carbon_user.h"
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <sys/timeb.h>

#define BILLION 1E9

typedef struct
{
   int         tid;
   int*        num_threads;
   double**    test_input;
   int*        test_output;
   double***   weights;
   double**    biases;
   int*        sizes;
   int         layers;
   double**    a;
   pthread_barrier_t* barrier;
} thread_arg_t;

//double feed_forward(double *weights, double *a, double biase, int size );
double int_layer_one(double *weights, double *a, double biase, int size );
double int_layer_two(double *weights, double *a, double biase, int size );
double output_layer(double *weights, double *a, double biase, int size );
double sigmoid(double z);
int get_index(double *a, int size);
void initialize(double ***weights, double **biases, int layers, int *sizes);
void call_feedforward(int test_index, thread_arg_t *thread_arg);
void* evaluate(void* arg);
void data_reading(double*** weights, double** biases, double **test_input, int *test_output, int layers, int* sizes);
double exponential(double x);

thread_arg_t thread_args[1024];
pthread_t thread_handles[1024];
pthread_mutex_t locks[1024];

const int test_size     = 100;
const int input_size    = 784;
const int output_size   = 10;

int main(int argc, char** argv){

   // Program Arguments //
   // const int num_threads = atoi(argv[1]);
   int index = 1;
   const int layers   = atoi(argv[index++]);   

   int* sizes = (int*) malloc((layers+1)*sizeof(int));
   for(int i = 0; i < layers + 1; i++){
      sizes[i] = atoi(argv[index++]);
   }

   int* num_threads = (int*) malloc(layers*sizeof(int));
   num_threads[0] = atoi(argv[index++]); 	//the last param

   for(int i = 1; i < layers; i++){			//starting at 2nd location in array, give max number of threads (per layer)
      if(sizes[i+1]>num_threads[0])			//if size of the next layer > num threads
         num_threads[i] = num_threads[0];	
      else
         num_threads[i] = sizes[i+1];		//give threads equal to size, if < num threads
      printf("%d\n", num_threads[i]);
   }



   printf("Testing Input Memory Allocation...\n");
   // Inputs of Test Data //   
   double** test_input = (double**) malloc(test_size*sizeof(double*));
   for(int i = 0; i < test_size; i++){
      test_input[i] = (double*) malloc(input_size*sizeof(double));
   }

   printf("Testing Output Memory Allocation...\n");
   // Outputs of Test  Data //  
   int* test_output = (int*) malloc(test_size*sizeof(int));



   printf("Weights Memory Allocation...\n");
   // Allocate memory space for weights //
   double*** weights = (double***) malloc(layers*sizeof(double**));
   double**  biases  = (double**)  malloc(layers*sizeof(double*));
   for(int i = 0; i < layers; i++ ){
      weights[i] = (double**) malloc(sizes[i+1]*sizeof(double*));
      biases[i]  = (double*)  malloc(sizes[i+1]*sizeof(double));
      for(int j = 0; j < sizes[i+1]; j++){
         weights[i][j] = (double*) malloc(sizes[i]*sizeof(double)); 
      }   
   }


   printf("Activation Memory Allocation...\n"); 
   // Memory space for Activations //  
   double** a = (double**) malloc((layers+1)*sizeof(double*));
   for(int i = 0; i < layers+1; i++){
      a[i] = (double*) malloc(sizes[i]*sizeof(double));
   }


   // Read the training inputs and outputs from the files //
   data_reading(weights, biases, test_input, test_output, layers, sizes); 


   pthread_barrier_t barrier; 
   pthread_barrier_init(&barrier, NULL, num_threads[0]); 
   for(int i=0; i<sizes[1]; i++)
      pthread_mutex_init(&locks[i], NULL);

   for (int i = 0; i < num_threads[0]; i++)
   {
      thread_args[i].tid         = i;				//thread id (each thread numbered 0-63)
      thread_args[i].num_threads = num_threads;
      thread_args[i].weights     = weights;			//the address to the first location of that 3D array
      thread_args[i].test_output = test_output;
      thread_args[i].test_input  = test_input;
      thread_args[i].biases      = biases;
      thread_args[i].sizes       = sizes;
      thread_args[i].layers      = layers;
      thread_args[i].a           = a;				//activation
      thread_args[i].barrier     = &barrier;
   }


   struct timespec requestStart, requestEnd;
   clock_gettime(CLOCK_REALTIME, &requestStart);

   printf("Creating the threads...\n");

   //CarbonEnableModels();

   for (int i = 1; i < num_threads[0]; i++){
      int ret = pthread_create(&thread_handles[i], NULL,evaluate, (void*)&thread_args[i]);
      if (ret != 0){
         fprintf(stderr, "ERROR spawning thread %i\n", i);
         exit(EXIT_FAILURE);
      }
   }
   evaluate((void*)&thread_args[0]);

#ifdef DEBUG
   fprintf(stderr, "Created Threads.\n");
#endif
   printf("done...\n");
   for (int i = 1; i < num_threads[0]; i++){
      pthread_join(thread_handles[i], NULL);			//as each thread finishes, continue

   } //now every evaluate is completed

   //CarbonDisableModels();

   clock_gettime(CLOCK_REALTIME, &requestEnd);
   double accum = ( requestEnd.tv_sec - requestStart.tv_sec ) + ( requestEnd.tv_nsec - requestStart.tv_nsec ) / BILLION;
   printf( "%lf\n", accum );


   return 0;

}



/* This function is used by evaluate() function
 * to obtain the index of largest prediction in 
 * the output vector of Neural Network */
int get_index(double *a, int size){

   double temp = 0.0;
   int index = 0;

   for(int i = 0; i < size; i++){

      if(a[i] > temp){ temp = a[i]; index = i; }

   }

   return index;

}


/* This function is to calculate the output of each neron for given
 * inputs, weights and biase. */

/*double feed_forward(double *weights, double *a, double biase, int size ){

  double z = 0.0;

  for(int i = 0; i < size ; i++){

  z += weights[i]*a[i];
  }

  z += biase;

  return sigmoid(z);

  }*/

double int_layer_one(double *weights, double *a, double biase, int size ){

double z = 0.0;

   for(int i = 0; i < size ; i++){

      z += weights[i]*a[i]; 
   }
   
   z += biase;
   double result = 1.0/(1.0 + exponential(-z));
   return result;

}

double int_layer_two(double *weights, double *a, double biase, int size ){

  double z = 0.0;

   for(int i = 0; i < size ; i++){
     
       z += weights[i]*a[i];
       
   }
   
   z += biase;
   double result = 1.0/(1.0 + exponential(-z));
   return result;
}

double output_layer(double *weights, double *a, double biase, int size ){

   double z = 0.0;

   for(int i = 0; i < size ; i++){
     
       z += weights[i]*a[i];
       
   }
   
   z += biase;
   double result = 1.0/(1.0 + exponential(-z));
   return result;
}

/* This function to evaluate the effectiveness of the training, it calls the function return_output() 
 * to calculate the output of the Neural Network for each test data. For each test data obtained result
 * then compared with the desired output.
 */
void *evaluate(void *arg){

   thread_arg_t* thread_arg = (thread_arg_t*) arg;

   int         tid            = thread_arg->tid;
   int*        num_threads    = thread_arg->num_threads;
   double**    test_input     = thread_arg->test_input;
   int*        test_output    = thread_arg->test_output;
   double***   weights        = thread_arg->weights;
   double**    biases         = thread_arg->biases;
   int*        sizes          = thread_arg->sizes;
   int         layers         = thread_arg->layers;
   double**    a              = thread_arg->a;

   int counter;

   if(tid == 0){
      counter = 0;
   } 

   for(int k = 0; k < test_size; k++){    

      for(int i = 1; i < layers+1; i++){
         
         if(i == 1){
           // printf("layer %d, tid %d\n", i, tid);
            //for (int j = start; j < stop; j++){
            for (int j = tid; j < sizes[i]; j=j+num_threads[i-1]){

               a[i][j] = int_layer_one(weights[i-1][j], test_input[k], biases[i-1][j], sizes[i-1]); 
              //a[i][j] = feed_forward(weights[i-1][j], test_input[k], biases[i-1][j], sizes[i-1]); 

            }
            pthread_barrier_wait(thread_arg->barrier);
         }

         else if (i == 2){
           // printf("layer %d, tid %d\n", i, tid);
            for (int j = tid; j < sizes[i]; j=j+num_threads[i-1]){

               a[i][j] = int_layer_two(weights[i-1][j], a[i-1], biases[i-1][j], sizes[i-1]);
               //a[i][j] = feed_forward(weights[i-1][j], a[i-1], biases[i-1][j], sizes[i-1]);

            }
            pthread_barrier_wait(thread_arg->barrier);
         }
         else {
            //for (int j = start; j < stop; j++){
           // printf("layer %d, tid %d\n", i, tid);
            for (int j = tid; j < sizes[i]; j=j+num_threads[i-1]){

               a[i][j] = output_layer(weights[i-1][j], a[i-1], biases[i-1][j], sizes[i-1]);
               //a[i][j] = feed_forward(weights[i-1][j], a[i-1], biases[i-1][j], sizes[i-1]);

            }
            pthread_barrier_wait(thread_arg->barrier); 
         }	       
         // }

         }

         if(get_index(a[layers], sizes[layers]) == test_output[k] && tid == 0) {
            counter++;
         }
      }

      if(tid == 0){
         printf("%d : %d\n", counter, test_size);
         printf("%lf%%\n", 100.0*counter/test_size);
      }

   }



   /* Reading the Training and Test Data and parsing training output data */
   void data_reading(double*** weights, double** biases, double **test_input, int *test_output, int layers, int* sizes){

      int rv;
      FILE *file;

      file = fopen("data/weights", "r");
      if (file == NULL) {
         printf("ERROR: Unable to open file '%s'.\n", "weights");
         exit(1);
      }

      for(int i = 0 ; i < layers; i++){
         for(int j = 0 ; j < sizes[i+1]; j++){
            for(int k = 0; k < sizes[i]; k++){
               rv = fscanf(file, "%lf", &weights[i][j][k]); //weights[current layer][output neurons][input neurons]
               //weights[i][j][k] = drand48();
            }
         }
      }


      file = fopen("data/biases", "r"); 
      if (file == NULL) {
         printf("ERROR: Unable to open file '%s'.\n", "biases");
         exit(1);
      }   
      for(int i = 0 ; i < layers; i++){
         for(int j = 0 ; j < sizes[i+1]; j++){
            rv = fscanf(file, "%lf", &biases[i][j]);
            //biases[i][j] = drand48();
         }
      }


      printf("Reading the Test Input...\n");
      file = fopen("data/test_input", "r");
      if (file == NULL) {
         printf("ERROR: Unable to open file '%s'.\n", "test_input");
         exit(1);
      }
      for(int i = 0; i < test_size; i++){
         for (int j=0; j< input_size; j++) {
            rv = fscanf(file, "%lf", &test_input[i][j]);
         }
      }
      fclose(file);


      printf("Reading the Test Output...\n");
      file = fopen("data/test_output", "r");
      if (file == NULL) {
         printf("ERROR: Unable to open file '%s'.\n", "test_output");
         exit(1);
      } 
      for(int i = 0; i < test_size; i++){
         rv = fscanf(file, "%d", &test_output[i]);
      } 
      fclose(file);

      printf("Data parsing is done...\n");
   }


   /* Sigmoid function and its derivative*/
   double sigmoid(double z){
      return 1.0/(1.0 + exponential(-z));
   }

   double exponential(double x)
   {
      double sum = 1.0f; // initialize sum of series

      for (int i = 100 - 1; i > 0; --i )
         sum = 1 + x * sum / i;

      return sum;
   }

   void read_parameters(double*** weights, double** biases, int layers, int* sizes){
      int rv;
      FILE *file;

      file = fopen("weights", "r");

      if(file == NULL)
      {
         printf( "Error openning file 'weights' !\n");
         exit(1);
      }

      for(int i = 0; i < layers; i++){
         for (int j=0; j< sizes[i+1]; j++) {
            for(int k = 0; k < sizes[i]; k++){
               rv = fscanf(file, "%lf", &weights[i][j][k]);
            }
         }
      }
      fclose(file);


      file = fopen("biases", "r");

      if(file == NULL)
      {
         printf("Error openning file 'weights' !\n");
         exit(1);
      }

      for(int i = 0; i < layers; i++){
         for (int j=0; j< sizes[i+1]; j++) {
            rv = fscanf(file, "%lf", &biases[i][j]);
         }
      }

   }


   void write_parameters(double*** weights, double** biases, int layers, int* sizes){

      FILE *file = fopen("weights", "w");

      if(file == NULL)
      {
         printf("Error openning file 'weights' !\n");
         exit(1);
      }


      for(int i = 0; i < layers; i++){
         for(int j = 0; j < sizes[i+1]; j++){
            for(int k = 0; k < sizes[i]; k++){

               fprintf(file,"%lf\t", weights[i][j][k]);

            }
         }
      }
      fclose(file);

      file = fopen("biases", "w");

      if(file == NULL)
      {
         printf("Error openning file 'biases' !\n");
         exit(1);
      }

      for(int i = 0 ; i < layers; i++){
         for(int j = 0 ; j < sizes[i+1]; j++){
            fprintf(file, "%lf\t", biases[i][j]);
         }
      }

      fclose(file);
   }
