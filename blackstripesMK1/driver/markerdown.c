#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <bcm2835.h>

//scp markerdown.c jed@192.168.1.33:/home/jed/GPIO_C_driver
//gcc -o markerdown -I bcm2835-1.8/src bcm2835-1.8/src/bcm2835.c markerdown.c


#define RIGHT_CLOCK RPI_GPIO_P1_05
#define RIGHT_DIR RPI_GPIO_P1_03
#define LEFT_CLOCK RPI_GPIO_P1_08
#define LEFT_DIR RPI_GPIO_P1_07
#define SOLENOID RPI_GPIO_P1_10


int main(void)
{
    if (!bcm2835_init()){
        printf("error");
        return 1;
    }
    
    bcm2835_gpio_fsel(RIGHT_CLOCK, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(RIGHT_DIR, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(LEFT_CLOCK, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(LEFT_DIR, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(SOLENOID, BCM2835_GPIO_FSEL_OUTP);
    
    bcm2835_gpio_write(SOLENOID, LOW);
    return 0;
}