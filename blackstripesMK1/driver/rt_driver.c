#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <sys/mman.h>
#include <bcm2835.h>
#include <native/task.h>
#include <native/timer.h>

RT_TASK draw_task;

#define RIGHT_CLOCK RPI_GPIO_P1_05
#define RIGHT_DIR RPI_GPIO_P1_03
#define LEFT_CLOCK RPI_GPIO_P1_08
#define LEFT_DIR RPI_GPIO_P1_07
#define SOLENOID RPI_GPIO_P1_10

//scp rt_driver.c jed@192.168.1.12:/home/jed/GPIO_C_driver
//gcc -I/usr/xenomai/include -Ibcm2835-1.8/src bcm2835-1.8/src/bcm2835.c rt_driver.c -L/usr/xenomai/lib -lnative -lxenomai -o rt_driver
//export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/xenomai/lib

/* NOTE: error handling omitted. */

void draw_layer(void *arg)
{
 
    char **myFilenames;
    int filenameCount = 4;
    myFilenames = (char**)calloc(sizeof(char**),filenameCount);
    if (myFilenames == NULL) {
        printf("Error allocating filename array\n");
        exit(1);
    }
    
    myFilenames[0] = "layer0.dat";
    myFilenames[1] = "layer1.dat";
    myFilenames[2] = "layer2.dat";
    myFilenames[3] = "layer3.dat";
    
    int currentlayer = 0;
    
    for(currentlayer; currentlayer < filenameCount; currentlayer++){
        
        print("press any key to continue");
        getchr();
        printf("drawing : %s \n",myFilenames[currentlayer]);
        
        bcm2835_gpio_write(SOLENOID, HIGH);
    
        /*
         * Arguments: &task (NULL=self),
         *            start time,
         *            period (here: 1 s)
         */
        rt_task_set_periodic(NULL, TM_NOW, 80000);
        
        int delaytimes[41] = {19550, 19100, 18650, 18200, 17750, 17300, 16850, 16400, 15950, 15500, 15050, 14600, 14150, 13700, 13250, 12800, 12350, 11900, 11450, 11000, 10550, 10100, 9650, 9200, 8750, 8300, 7850, 7400, 6950, 6500, 6050, 5600, 5150, 4700, 4250, 3800, 3350, 2900, 2450, 2000, 2000};
        
        FILE    *infile;
        char    *buffer;
        long    numbytes;
        
        //read the file
        infile = fopen(myFilenames[currentlayer], "r");
        if(infile == NULL){
            printf("no input file");
        }
        fseek(infile, 0L, SEEK_END);
        numbytes = ftell(infile);
        fseek(infile, 0L, SEEK_SET);
        buffer = (char*)calloc(numbytes, sizeof(char));
        if(buffer == NULL){
            printf("mem error");
        }
        fread(buffer, sizeof(char), numbytes, infile);
        fclose(infile);
        
        char newl[] = "\n";
        char *line = NULL;
        char *end_str;
        line = strtok_r( buffer, newl , &end_str);
        
        int currentdelay = 19550;
        int leftdir = 0;
        int rightdir = 0;
        int linecounter = 0;
        
        while (line != NULL) {
            rt_task_wait_period(NULL);

            char delims[] = ",";
            char *result = NULL;
            char *end_token;
            result = strtok_r( line, delims ,&end_token);
            int poscounter = 0;
            
            int stepleft = 0;
            int stepright = 0;
            int solenoidstate = 0;
            
            while( result != NULL ) {
                if(poscounter == 0){
                    
                    stepleft = atoi(result);
                    
                    if(stepleft != leftdir){
                        if(stepleft < 0){
                            bcm2835_gpio_write(LEFT_DIR, LOW);
                        }else if(stepleft > 0){
                            bcm2835_gpio_write(LEFT_DIR, HIGH);
                        }
                        
                        leftdir = stepleft;
                        
                    }
                    
                }else if(poscounter == 1){
                    
                    stepright = atoi(result);
                    
                    if(stepright != rightdir){
                        if(stepright < 0){
                            bcm2835_gpio_write(RIGHT_DIR, HIGH);
                        }else if(stepright > 0){
                            bcm2835_gpio_write(RIGHT_DIR, LOW);
                        }
                        
                        rightdir = stepright;
                        
                    }
                    
                }else if(poscounter == 2){
                    
                    int solenoid = atoi(result);
                    if(solenoidstate != solenoid){
                        if(solenoid < 0){
                            bcm2835_gpio_write(SOLENOID, HIGH);
                        }else if(solenoid > 0){
                            bcm2835_gpio_write(SOLENOID, LOW);
                        }
                    }
                    solenoidstate = solenoid;
                    
                }else if(poscounter == 3){
                    
                    int index = atoi(result);
                    if(index < 40){
                        currentdelay = delaytimes[index];
                    }else{
                        currentdelay = 2000;
                    }
                    
                }
                
                result = strtok_r( NULL, delims,&end_token );
                poscounter ++;
                
                linecounter ++;
                
                
            }
     
            // sync the stepper steps //
            if (stepleft != 0) {
                bcm2835_gpio_write(LEFT_CLOCK, HIGH);
            }
            if (stepright != 0) {
                bcm2835_gpio_write(RIGHT_CLOCK, HIGH);
            }
            
            rt_task_sleep(100);
            
            if (stepleft != 0) {
                bcm2835_gpio_write(LEFT_CLOCK, LOW);
            }
            if (stepright != 0) {
                bcm2835_gpio_write(RIGHT_CLOCK, LOW);
            }
            
            line = strtok_r( NULL, newl,&end_str );
            
            poscounter = 0;
            
            rt_task_set_periodic(NULL, TM_NOW, 80000+((currentdelay-2000) *50));
            
        }
        
        free(buffer);
        
    }
    
    free(myFilenames);
    bcm2835_gpio_write(SOLENOID, HIGH);
}

void catch_signal(int sig)
{
}

int main(int argc, char* argv[])
{
    signal(SIGTERM, catch_signal);
    signal(SIGINT, catch_signal);
    
    /* Avoids memory swapping for this program */
    mlockall(MCL_CURRENT|MCL_FUTURE);
    
    
	if (!bcm2835_init()){
        printf("error");
        //return 1;
    }
    
	bcm2835_gpio_fsel(RIGHT_CLOCK, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(RIGHT_DIR, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(LEFT_CLOCK, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(LEFT_DIR, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(SOLENOID, BCM2835_GPIO_FSEL_OUTP);
    
	/*
     * Arguments: &task,
     *            name,
     *            stack size (0=default),
     *            priority,
     *            mode (FPU, start suspended, ...)
     */
    rt_task_create(&draw_task, "printerbot", 0, 99, 0);
    
    /*
     * Arguments: &task,
     *            task function,
     *            function argument
     */
    rt_task_start(&draw_task, &draw_layer, NULL);
    
    pause();
    
    rt_task_delete(&draw_task);
    
    bcm2835_gpio_write(SOLENOID, HIGH);
    
}
