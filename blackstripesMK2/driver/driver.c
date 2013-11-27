#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <sys/mman.h>
#include <bcm2835.h>
#include <native/task.h>
#include <native/timer.h>

RT_TASK draw_task;

#define RIGHT_CLOCK RPI_V2_GPIO_P1_11
#define RIGHT_DIR RPI_V2_GPIO_P1_12
#define LEFT_CLOCK RPI_V2_GPIO_P1_13
#define LEFT_DIR RPI_V2_GPIO_P1_15
#define SOLENOID_1 RPI_V2_GPIO_P1_16
#define SOLENOID_2 RPI_V2_GPIO_P1_18
#define SOLENOID_3 RPI_V2_GPIO_P1_22

char motiondata[21];
char image[21];
int easeTableOffset = 500;

//scp driver.c rpi@192.168.0.102:/home/rpi/blackstripes
//scp spiral.bin rpi@192.168.0.102:/home/rpi/blackstripes
//gcc -I/usr/xenomai/include -Ibcm2835-1.25 bcm2835-1.25/bcm2835.c driver.c -L/usr/xenomai/lib -lnative -lxenomai -o driver
//export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/xenomai/lib
//pw:linuxcnc

void draw_layer(void *arg)
{
    bcm2835_gpio_write(SOLENOID_1, HIGH);
    bcm2835_gpio_write(SOLENOID_2, HIGH);
    bcm2835_gpio_write(SOLENOID_3, HIGH);

    /*
     * Arguments: &task (NULL=self),
     *            start time,
     *            period (here: 1 s)
     */
    
    
    int delaytimes[1000] = {

    1299468, 1290435, 1281465, 1272557, 1263711, 1254926, 1246203, 1237540, 1228938, 1220395, 1211912, 1203487, 1195121, 1186814, 1178564, 1170371, 1162235, 1154156, 1146133, 1138166, 1130254, 1122398, 1114595, 1106847, 1099153, 1091513, 1083925, 1076391, 1068908, 1061478, 1054099, 1046772, 1039495, 1032269, 1025094, 1017968, 1010892, 1003865, 996886, 989957, 983075, 976242, 969455, 962716, 956024, 949379, 942779, 936225, 929717, 923255, 916837, 910464, 904135, 897850, 891608, 885411, 879256, 873144, 867074, 861047, 855061, 849118, 843215, 837354, 831533, 825753, 820013, 814312, 808652, 803031, 797448, 791905, 786400, 780934, 775505, 770114, 764761, 759445, 754166, 748923, 743717, 738547, 733414, 728315, 723253, 718225, 713232, 708274, 703351, 698462, 693606, 688785, 683997, 679242, 674521, 669832, 665176, 660552, 655960, 651400, 646872, 642375, 637910, 633476, 629072, 624699, 620357, 616045, 611762, 607510, 603287, 599093, 594928, 590793, 586686, 582608, 578558, 574536, 570542, 566576, 562638, 558727, 554843, 550986, 547156, 543352, 539575, 535825, 532100, 528401, 524728, 521080, 517458, 513861, 510289, 506742, 503219, 499721, 496248, 492798, 489372, 485971, 482592, 479238, 475906, 472598, 469313, 466051, 462811, 459594, 456399, 453226, 450076, 446947, 443840, 440755, 437691, 434649, 431627, 428627, 425647, 422689, 419750, 416833, 413935, 411058, 408200, 405363, 402545, 399747, 396968, 394208, 391468, 388747, 386044, 383361, 380696, 378050, 375422, 372812, 370221, 367647, 365091, 362553, 360033, 357531, 355045, 352577, 350126, 347692, 345276, 342875, 340492, 338125, 335775, 333441, 331123, 328821, 326535, 324265, 322011, 319773, 317550, 315343, 313151, 310974, 308812, 306665, 304534, 302417, 300314, 298227, 296154, 294095, 292051, 290021, 288005, 286003, 284014, 282040, 280080, 278133, 276199, 274279, 272373, 270479, 268599, 266732, 264878, 263037, 261208, 259392, 257589, 255799, 254021, 252255, 250501, 248760, 247031, 245314, 243608, 241915, 240233, 238563, 236905, 235258, 233623, 231999, 230386, 228785, 227194, 225615, 224047, 222489, 220943, 219407, 217881, 216367, 214863, 213369, 211886, 210413, 208951, 207498, 206056, 204623, 203201, 201788, 200386, 198993, 197609, 196236, 194872, 193517, 192172, 190836, 189509, 188192, 186884, 185585, 184295, 183014, 181741, 180478, 179223, 177978, 176740, 175512, 174292, 173080, 171877, 170682, 169496, 168318, 167148, 165986, 164832, 163686, 162548, 161418, 160296, 159182, 158075, 156977, 155885, 154802, 153726, 152657, 151596, 150542, 149496, 148456, 147424, 146400, 145382, 144371, 143368, 142371, 141382, 140399, 139423, 138454, 137491, 136535, 135586, 134644, 133708, 132778, 131855, 130939, 130029, 129125, 128227, 127336, 126451, 125572, 124699, 123832, 122971, 122116, 121267, 120424, 119587, 118756, 117930, 117111, 116297, 115488, 114685, 113888, 113097, 112310, 111530, 110754, 109984, 109220, 108461, 107707, 106958, 106215, 105476, 104743, 104015, 103292, 102574, 101861, 101153, 100450, 99751, 99058, 98369, 97685, 97006, 96332, 95662, 94997, 94337, 93681, 93030, 92383, 91741, 91104, 90470, 89841, 89217, 88597, 87981, 87369, 86762, 86159, 85560, 84965, 84374, 83788, 83205, 82627, 82053, 81482, 80916, 80353, 79795, 79240, 78689, 78142, 77599, 77060, 76524, 75992, 75464, 74939, 74418, 73901, 73387, 72877, 72371, 71867, 71368, 70872, 70379, 69890, 69404, 68922, 68443, 67967, 67494, 67025, 66559, 66097, 65637, 65181, 64728, 64278, 63831, 63387, 62947, 62509, 62074, 61643, 61214, 60789, 60366, 59947, 59530, 59116, 58705, 58297, 57892, 57490, 57090, 56693, 56299, 55908, 55519, 55133, 54750, 54369, 53991, 53616, 53243, 52873, 52506, 52141, 51778, 51418, 51061, 50706, 50353, 50003, 49656, 49311, 48968, 48627, 48289, 47954, 47620, 47289, 46961, 46634, 46310, 45988, 45668, 45351, 45036, 44723, 44412, 44103, 43796, 43492, 43190, 42889, 42591, 42295, 42001, 41709, 41419, 41131, 40845, 40561, 40279, 40000,
    //linear mode
    1299468,1296944,1294420,1291896,1289372,1286848,1284324,1281800,1279276,1276752,1274228,1271704,1269180,1266656,1264132,1261608,1259084,1256560,1254036,1251512,1248988,1246464,1243940,1241416,1238892,1236368,1233844,1231320,1228796,1226272,1223748,1221224,1218701,1216177,1213653,1211129,1208605,1206081,1203557,1201033,1198509,1195985,1193461,1190937,1188413,1185889,1183365,1180841,1178317,1175793,1173269,1170745,1168221,1165697,1163173,1160649,1158125,1155601,1153077,1150553,1148029,1145505,1142981,1140457,1137933,1135409,1132885,1130361,1127837,1125313,1122789,1120265,1117741,1115217,1112693,1110169,1107645,1105121,1102597,1100073,1097549,1095025,1092501,1089977,1087453,1084929,1082405,1079881,1077357,1074833,1072309,1069785,1067261,1064737,1062214,1059690,1057166,1054642,1052118,1049594,1047070,1044546,1042022,1039498,1036974,1034450,1031926,1029402,1026878,1024354,1021830,1019306,1016782,1014258,1011734,1009210,1006686,1004162,1001638,999114,996590,994066,991542,989018,986494,983970,981446,978922,976398,973874,971350,968826,966302,963778,961254,958730,956206,953682,951158,948634,946110,943586,941062,938538,936014,933490,930966,928442,925918,923394,920870,918346,915822,913298,910774,908250,905727,903203,900679,898155,895631,893107,890583,888059,885535,883011,880487,877963,875439,872915,870391,867867,865343,862819,860295,857771,855247,852723,850199,847675,845151,842627,840103,837579,835055,832531,830007,827483,824959,822435,819911,817387,814863,812339,809815,807291,804767,802243,799719,797195,794671,792147,789623,787099,784575,782051,779527,777003,774479,771955,769431,766907,764383,761859,759335,756811,754287,751763,749239,746716,744192,741668,739144,736620,734096,731572,729048,726524,724000,721476,718952,716428,713904,711380,708856,706332,703808,701284,698760,696236,693712,691188,688664,686140,683616,681092,678568,676044,673520,670996,668472,665948,663424,660900,658376,655852,653328,650804,648280,645756,643232,640708,638184,635660,633136,630612,628088,625564,623040,620516,617992,615468,612944,610420,607896,605372,602848,600324,597800,595276,592752,590229,587705,585181,582657,580133,577609,575085,572561,570037,567513,564989,562465,559941,557417,554893,552369,549845,547321,544797,542273,539749,537225,534701,532177,529653,527129,524605,522081,519557,517033,514509,511985,509461,506937,504413,501889,499365,496841,494317,491793,489269,486745,484221,481697,479173,476649,474125,471601,469077,466553,464029,461505,458981,456457,453933,451409,448885,446361,443837,441313,438789,436265,433741,431218,428694,426170,423646,421122,418598,416074,413550,411026,408502,405978,403454,400930,398406,395882,393358,390834,388310,385786,383262,380738,378214,375690,373166,370642,368118,365594,363070,360546,358022,355498,352974,350450,347926,345402,342878,340354,337830,335306,332782,330258,327734,325210,322686,320162,317638,315114,312590,310066,307542,305018,302494,299970,297446,294922,292398,289874,287350,284826,282302,279778,277254,274731,272207,269683,267159,264635,262111,259587,257063,254539,252015,249491,246967,244443,241919,239395,236871,234347,231823,229299,226775,224251,221727,219203,216679,214155,211631,209107,206583,204059,201535,199011,196487,193963,191439,188915,186391,183867,181343,178819,176295,173771,171247,168723,166199,163675,161151,158627,156103,153579,151055,148531,146007,143483,140959,138435,135911,133387,130863,128339,125815,123291,120767,118244,115720,113196,110672,108148,105624,103100,100576,98052,95528,93004,90480,87956,85432,82908,80384,77860,75336,72812,70288,67764,65240,62716,60192,57668,55144,52620,50096,47572,45048,42524,40000};

    rt_task_set_periodic(NULL, TM_NOW, delaytimes[0+easeTableOffset]);
    
    //////////////////////////
    // read the motion data //
    //////////////////////////

    FILE *source;
    
    long numbytes;
    long num_records;
    int recordLength = 4;
    
    unsigned long *data;

    source = fopen(motiondata, "rb");
    if (source == NULL) {
        printf("ERROR: could not open motiondata.\n");
        exit(1);
    }
    fseek(source, 0L, SEEK_END);
    numbytes = ftell(source);
    fseek(source, 0L, SEEK_SET);
    data = (long*)calloc(numbytes/recordLength, recordLength);
    if(data == NULL){
        printf("mem error\n");
    }
    fread(data, recordLength, numbytes, source);
    fclose(source);

    ////////////////////
    // read the image //
    ////////////////////

    FILE *imageSource;

    long numImagebytes;
    int pixelLength = 1;
    
    unsigned char *imageData;

    int imageDataOffset = 6;
    //the image data contains a 6 byte header
    //these are the threshold levels
    //this used to be fixed (36 spacing)
    //int levels[6] = {217, 180, 144, 108, 72, 36};
    
    imageSource = fopen(image, "rb");
    if (imageSource == NULL) {
        printf("ERROR: could not open imagedata.\n");
        exit(1);
    }
    fseek(imageSource, 0L, SEEK_END);
    numImagebytes = ftell(imageSource);
    fseek(imageSource, 0L, SEEK_SET);
    imageData = (char*)calloc(numImagebytes, pixelLength);
    if(imageData == NULL){
        printf("mem error\n");
    }
    fread(imageData, pixelLength, numImagebytes, imageSource);
    fclose(imageSource);

    //start
    int currentdelay = delaytimes[0+easeTableOffset];
    int leftdir = 1;
    int rightdir = 1;
    int linecounter = 0;
    
    num_records = numbytes / recordLength;
    
    int stepleft = 0;
    int stepright = 0;
    int solenoidstate1 = 0;
    int solenoidstate2 = 0;
    int solenoidstate3 = 0;
    int solenoid1 = 0;
    int solenoid2 = 0;
    int solenoid3 = 0;
    int speed = 0;
    
    int mask = 1610612736; //0b1100000000000000000000000000000
    int speed_mask = 511;  //0b0000000000000000000000111111111

    unsigned long solenoidPixel_1;
    unsigned long solenoidPixel_2;
    unsigned long solenoidPixel_3;
    
    long i;
    unsigned long record;
    unsigned long counter = 1;

    unsigned int pixelValue1;
    unsigned int pixelValue2;
    unsigned int pixelValue3;

    // long SPIRAL_START = 14033;
    // long SPIRAL_END = 8158089;

    long IMAGE_BOUNDS = 1000000-1; //1000x1000 image

    int p1,p2,p3;   //marker policy (1=image lookup, 0=don't draw, 2=draw)
    int even;       //for halftoning

    for(i=0;i<num_records;i+=4){
        
        rt_task_wait_period(NULL);

        record = data[i];
        
        stepleft = (record & mask) >> 29;
        stepright = (record & mask >> 2) >> 27;
        p1 = (record & mask >> 4) >> 25;
        p2 = (record & mask >> 6) >> 23;
        p3 = (record & mask >> 8) >> 21;
        even = (record & mask >> 10) >> 19;

        solenoidPixel_1 = data[i+1];
        solenoidPixel_2 = data[i+2];
        solenoidPixel_3 = data[i+3];

        // if(counter >= SPIRAL_START && counter <= SPIRAL_END){

            if(p1 == 0 || solenoidPixel_1 > IMAGE_BOUNDS){
                solenoid1 = 0;
            }else if(p1 == 2){
                solenoid1 = 2;
            }else{
                pixelValue1 = imageData[solenoidPixel_1+imageDataOffset];
                if (pixelValue1 < imageData[0+even]){
                    solenoid1 = 2;
                }else{
                    solenoid1 = 0;
                }
            }

            if(p2 == 0 || solenoidPixel_2 > IMAGE_BOUNDS){
                solenoid2 = 0;
            }else if(p2 == 2){
                solenoid2 = 2;
            }else{
                pixelValue2 = imageData[solenoidPixel_2+imageDataOffset];
                if (pixelValue2 < imageData[2+even]){
                    solenoid2 = 2;
                }else{
                    solenoid2 = 0;
                }
            }

            if(p3 == 0 || solenoidPixel_3 > IMAGE_BOUNDS){
                solenoid3 = 0;
            }else if(p3 == 2){
                solenoid3 = 2;
            }else{
                pixelValue3 = imageData[solenoidPixel_3+imageDataOffset];
                if (pixelValue3 < imageData[4+even]){
                    solenoid3 = 2;
                }else{
                    solenoid3 = 0;
                }
            }

        // }else{

        //     solenoid1 = 0;
        //     solenoid2 = 0;
        //     solenoid3 = 0;

        // }

        speed = (record & speed_mask);

        if(stepleft != leftdir){
            if(stepleft < 1){
                bcm2835_gpio_write(LEFT_DIR, HIGH);
            }else if(stepleft > 1){
                bcm2835_gpio_write(LEFT_DIR, LOW);
            }
            
            leftdir = stepleft;
            
        }
        
        if(stepright != rightdir){
            if(stepright < 1){
                bcm2835_gpio_write(RIGHT_DIR, HIGH);
            }else if(stepright > 1){
                bcm2835_gpio_write(RIGHT_DIR, LOW);
            }
            
            rightdir = stepright;
            
        }

        if(solenoidstate1 != solenoid1){
            if(solenoid1 < 1){
                bcm2835_gpio_write(SOLENOID_1, HIGH);
            }else if(solenoid1 > 1){
                bcm2835_gpio_write(SOLENOID_1, LOW);
            }
        }
        
        if(solenoidstate2 != solenoid2){
            if(solenoid2 < 1){
                bcm2835_gpio_write(SOLENOID_2, HIGH);
            }else if(solenoid2 > 1){
                bcm2835_gpio_write(SOLENOID_2, LOW);
            }
        }
        
        if(solenoidstate3 != solenoid3){
            if(solenoid3 < 1){
                bcm2835_gpio_write(SOLENOID_3, HIGH);
            }else if(solenoid3 > 1){
                bcm2835_gpio_write(SOLENOID_3, LOW);
            }
        }
        
        solenoidstate1 = solenoid1;
        solenoidstate2 = solenoid2;
        solenoidstate3 = solenoid3;
        
        currentdelay = delaytimes[speed+easeTableOffset];

 
        // sync the stepper steps //
        if (stepleft != 1) {
            bcm2835_gpio_write(LEFT_CLOCK, HIGH);
        }
        if (stepright != 1) {
            bcm2835_gpio_write(RIGHT_CLOCK, HIGH);
        }
        
        rt_task_sleep(100);
        //rt_task_set_periodic(NULL, TM_NOW, currentdelay);
        
        if (stepleft != 1) {
            bcm2835_gpio_write(LEFT_CLOCK, LOW);
        }
        if (stepright != 1) {
            bcm2835_gpio_write(RIGHT_CLOCK, LOW);
        }
        
        rt_task_set_periodic(NULL, TM_NOW, currentdelay);

        counter ++;
        
    }
    
    free(data);
    free(imageData);
    
    bcm2835_gpio_write(SOLENOID_1, HIGH);
    bcm2835_gpio_write(SOLENOID_2, HIGH);
    bcm2835_gpio_write(SOLENOID_3, HIGH);

    alarm(1);
    
}

void catch_signal(int sig)
{
}

int main(int argc, char* argv[])
{

    if ( argc != 3 ){  
        printf( "usage: %s: please supply motiondata and image source.\n", argv[0] );
        return -1;
    }else{
        strcpy(motiondata, argv[1]);  
        strcpy(image, argv[2]);   
    }

    signal(SIGTERM, catch_signal);
    signal(SIGINT, catch_signal);
    signal(SIGALRM, catch_signal);
    
    /* Avoids memory swapping for this program */
    mlockall(MCL_CURRENT|MCL_FUTURE);

	if (!bcm2835_init()){
        printf("error\n");
        //return 1;
    }
    
	bcm2835_gpio_fsel(RIGHT_CLOCK, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(RIGHT_DIR, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(LEFT_CLOCK, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(LEFT_DIR, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(SOLENOID_1, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(SOLENOID_2, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(SOLENOID_3, BCM2835_GPIO_FSEL_OUTP);
    
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
    
    bcm2835_gpio_write(SOLENOID_1, HIGH);
    bcm2835_gpio_write(SOLENOID_2, HIGH);
    bcm2835_gpio_write(SOLENOID_3, HIGH);

    popen("python server.py","r");

    return 0;
    
}
