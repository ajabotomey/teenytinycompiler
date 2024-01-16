#include <stdio.h>
#include <time.h>
#include <stdlib.h>
int main(void){
float a;
float b;
a = 0;
b = 1;
if (a>b) {
printf("a is bigger\n");
}
srand(time(0));
int w = rand() % 100 + 1;
return 0;
}
