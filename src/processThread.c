#include <math.h>
#include <pthread.h>
#include <semaphore.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

typedef double MathFunc_t(double);

typedef struct {
  MathFunc_t *func;
  double rangeStart;
  double rangeEnd;
  size_t numSteps;
  pthread_mutex_t *resultLock;
  double *result;
} threadData_t;

static sem_t numFreeChildren;

static inline double minimum(double a, double b) { return a > b ? b : a; }

void childCompletedSignalHandler(int signalNumber) {
  (void)signalNumber; // Ignore the signal number parameter

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

void *integrateTrap(void *threadDataPointer) {
  threadData_t *threadData = threadDataPointer;

  double rangeSize = threadData->rangeEnd - threadData->rangeStart;
  double dx = rangeSize / threadData->numSteps;

  double area = 0;

  for (size_t i = 0; i < threadData->numSteps; i++) {
    double smallx = threadData->rangeStart + i * dx;
    double bigx = threadData->rangeStart + (i + 1) * dx;

    area += (threadData->func(smallx) + threadData->func(bigx)) / 2;
  }

  area *= dx;

  pthread_mutex_lock(threadData->resultLock);
  *threadData->result += area;
  pthread_mutex_unlock(threadData->resultLock);

  return NULL;
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

  threadData_t threadData[NUMBER_OF_THREADS] = {0};
  pthread_t threads[NUMBER_OF_THREADS] = {0};

  sem_init(&numFreeChildren, 0, MAX_CHILDREN);

  struct sigaction childCompleted = {0};
  childCompleted.sa_handler = &childCompletedSignalHandler;
  sigaction(SIGCHLD, &childCompleted, NULL);

  printf("Query format: [func] [start] [end] [numSteps]\n");

  while (getValidInput(&func, funcName, &rangeStart, &rangeEnd, &numSteps)) {
    sem_wait(&numFreeChildren);

#ifdef LOGGING
    printf("Begining computation of function \"%s\" in range %g to %g with %zu "
           "steps\n",
           funcName, rangeStart, rangeEnd, numSteps);
#endif

    if (!fork()) {
      double increment = (rangeEnd - rangeStart) / NUMBER_OF_THREADS;

      double area = 0;
      pthread_mutex_t areaLock = PTHREAD_MUTEX_INITIALIZER;

      for (int i = 0; i < NUMBER_OF_THREADS; i++) {
        threadData[i] = (threadData_t){
            .rangeStart = rangeStart + i * increment,
            .rangeEnd = minimum(rangeStart + (i + 1) * increment, rangeEnd),
            .numSteps = numSteps / NUMBER_OF_THREADS,
            .func = func,
            .result = &area,
            .resultLock = &areaLock,
        };

        pthread_create(&threads[i], NULL, &integrateTrap, &threadData[i]);
      }

      for (int i = 0; i < NUMBER_OF_THREADS; i++) {
        pthread_join(threads[i], NULL);
      }

      printf("The integral of function \"%s\" in range %g to %g is %.10g\n",
             funcName, rangeStart, rangeEnd, area);

      _exit(0);
    }
  }

  _exit(0); // Forces more immediate exit than normal - **Use this to exit
            // processes throughout the assignment!**
}
