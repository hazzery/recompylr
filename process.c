#include <math.h>
#include <semaphore.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

typedef double MathFunc_t(double);

static sem_t numFreeChildren;
static size_t numCurrentChildren = 0;

void childCompletedSignalHandler(int _) {
  numCurrentChildren--;
  sem_post(&numFreeChildren);
}

double gaussian(double x) { return exp(-(x * x) / 2) / (sqrt(2 * M_PI)); }

double chargeDecay(double x) {
  if (x < 0) {
    return 0;
  } else if (x < 1) {
    return 1 - exp(-5 * x);
  } else {
    return exp(-(x - 1));
  }
}

// Integrate using the trapezoid method.
double integrateTrap(MathFunc_t *func, double rangeStart, double rangeEnd,
                     size_t numSteps) {
  double rangeSize = rangeEnd - rangeStart;
  double dx = rangeSize / numSteps;

  double area = 0;
  for (size_t i = 0; i < numSteps; i++) {
    double smallx = rangeStart + i * dx;
    double bigx = rangeStart + (i + 1) * dx;

    // Would be more efficient to multiply area by dx once at the end.
    area += dx * (func(smallx) + func(bigx)) / 2;
  }

  return area;
}

bool getValidInput(MathFunc_t **func, char *funcName, double *start,
                   double *end, size_t *numSteps) {
  memset(funcName, '\0', 10); // Clear funcName. Magic number used because
                              // format strings are annoying.

  // Read input numbers and place them in the given addresses:
  size_t numRead = scanf("%9s %lf %lf %zu", funcName, start, end, numSteps);

  if (strcmp(funcName, "sin") == 0) {
    *func = &sin;
  } else if (strcmp(funcName, "gauss") == 0) {
    *func = &gaussian;
  } else if (strcmp(funcName, "decay") == 0) {
    *func = &chargeDecay;
  } else {
    *func = NULL;
  }

  // Return whether the given func and range is valid:
  return (numRead == 4 && *func != NULL && *end >= *start && *numSteps > 0);
}

int main(void) {
  double rangeStart;
  double rangeEnd;
  size_t numSteps;
  MathFunc_t *func;
  char funcName[10] = {'\0'};

  sem_init(&numFreeChildren, 0, MAX_CHILDREN);
  signal(SIGCHLD, &childCompletedSignalHandler);

  printf("Query format: [func] [start] [end] [numSteps]\n");

  while (getValidInput(&func, funcName, &rangeStart, &rangeEnd, &numSteps)) {
    sem_wait(&numFreeChildren);

#ifdef LOGGING
    printf("Begining computation of function \"%s\" in range %g to %g with %zu "
           "steps\n",
           funcName, rangeStart, rangeEnd, numSteps);
#endif

    numCurrentChildren++;
    if (!fork()) {
      double area = integrateTrap(func, rangeStart, rangeEnd, numSteps);

      printf("The integral of function \"%s\" in range %g to %g is %.10g\n",
             funcName, rangeStart, rangeEnd, area);

      _exit(0);
    }
  }

  while (numCurrentChildren > 0) {
    wait(NULL);
  }

  _exit(0); // Forces more immediate exit than normal - **Use this to exit
            // processes throughout the assignment!**
}
