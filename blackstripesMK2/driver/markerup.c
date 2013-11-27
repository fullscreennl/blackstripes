#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <bcm2835.h>

//scp markerup.c rpi@192.168.0.102:/home/pi/Desktop/GPIO_C_driver
//gcc -o up -Ibcm2835-1.25 bcm2835-1.25/bcm2835.c markerup.c

#define RIGHT_CLOCK RPI_V2_GPIO_P1_11
#define RIGHT_DIR RPI_V2_GPIO_P1_12
#define LEFT_CLOCK RPI_V2_GPIO_P1_13
#define LEFT_DIR RPI_V2_GPIO_P1_15

#define SOLENOID_1 RPI_V2_GPIO_P1_16
#define SOLENOID_2 RPI_V2_GPIO_P1_18
#define SOLENOID_3 RPI_V2_GPIO_P1_22


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

    bcm2835_gpio_fsel(SOLENOID_1, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(SOLENOID_2, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(SOLENOID_3, BCM2835_GPIO_FSEL_OUTP);
    
    bcm2835_gpio_write(SOLENOID_1, HIGH);
    sleep(3);
    bcm2835_gpio_write(SOLENOID_2, HIGH);
    sleep(3);
    bcm2835_gpio_write(SOLENOID_3, HIGH);
    return 0;
}
