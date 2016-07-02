#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
	char *buffer;
	size_t buffsize = 128;
	//size_t characters;

	buffer = (char *)malloc(buffsize * sizeof(char));
	if( buffer == NULL)
    {
        perror("Unable to allocate buffer");
        return 1;
    }

	FILE* file = NULL; 
    //char buff[100];
    //memset(buff,0,sizeof(buff));
    file = fopen("program.cc","r+"); 
    if(NULL == file)
    { 
        printf("\n fopen() Error!!!\n"); 
        return 1;
    }
    printf("\n File opened successfully through fopen()\n");

    while(strstr(buffer, "int main") == NULL){
    //for(int i=0; i<10; i++){
    	//characters = getline(&buffer, &buffsize, file);
    	fgets(buffer, buffsize, file);
    	printf("Current line: '%s'\n", buffer);
	}
	printf("Main function found: '%s'\n",buffer);
	//fprintf(file, "Test");

    fclose(file);

    return 0;
}