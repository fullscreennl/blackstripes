//
//  BSViewController.m
//  blackstripes
//
//  Created by johan ten broeke on 8/8/13.
//  Copyright (c) 2013 johan ten broeke. All rights reserved.
//

#import "BSViewController.h"
#import <ImageIO/ImageIO.h>
#import <MobileCoreServices/MobileCoreServices.h>
#import "GCDAsyncSocket.h"




@interface BSViewController ()

@end

@implementation BSViewController


struct pixel {
    unsigned char r, g, b, a;
};



- (void)viewDidLoad
{
    [super viewDidLoad];
    dispatch_queue_t mainQueue = dispatch_get_main_queue();
    [asyncSocket release];
	asyncSocket = [[GCDAsyncSocket alloc] initWithDelegate:self delegateQueue:mainQueue];
    
    neutralLevels = @[@217, @180, @144, @108, @72, @36];
    [neutralLevels retain];
    
    levels = [[NSMutableArray alloc] initWithArray:neutralLevels];
    
}

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

-(IBAction)takePhoto:(id)sender{
    if ([UIImagePickerController isSourceTypeAvailable: UIImagePickerControllerSourceTypeCamera]){
        // Has camera
        UIActionSheet *sheet = [[UIActionSheet alloc] initWithTitle:@"Select an image."
                                                           delegate:self
                                                  cancelButtonTitle:@"cancel"
                                             destructiveButtonTitle:nil
                                                  otherButtonTitles:@"photo roll",@"camera", nil];
        UIView *v = [UIApplication sharedApplication].delegate.window.rootViewController.view;
        [sheet showInView:v];
        [sheet release];
 
    }else{
        
        [self libraryAction:sender];
        
    }
}

-(void)camAction{
    UIImagePickerController *imPickerC = [[UIImagePickerController alloc] init];
    [imPickerC setSourceType:UIImagePickerControllerSourceTypeCamera];
    [imPickerC setAllowsEditing:YES];
    [imPickerC setDelegate:self];
    [self presentViewController:imPickerC animated:YES completion:nil];
    [imPickerC release];
}

-(void)libraryAction:(UIButton*)sender{
    UIImagePickerController *imPickerC = [[UIImagePickerController alloc] init];
    [imPickerC setAllowsEditing:YES];
    [imPickerC setDelegate:self];
    [self presentViewController:imPickerC animated:YES completion:nil];
    [imPickerC release];
}


-(void)dealloc{
    [levels release];
    [neutralLevels release];
    [blackstripesData release];
    [asyncSocket release];
    [super dealloc];
}

- (UIImage *) convertToGreyscale:(UIImage *)i {
    
    int kRed = 1;
    int kGreen = 2;
    int kBlue = 4;
    
    int colors = kGreen;
    int m_width = i.size.width;
    int m_height = i.size.height;
    
    uint32_t *rgbImage = (uint32_t *) malloc(m_width * m_height * sizeof(uint32_t));
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGContextRef context = CGBitmapContextCreate(rgbImage, m_width, m_height, 8, m_width * 4, colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaNoneSkipLast);
    CGContextSetInterpolationQuality(context, kCGInterpolationHigh);
    CGContextSetShouldAntialias(context, NO);
    CGContextDrawImage(context, CGRectMake(0, 0, m_width, m_height), [i CGImage]);
    CGContextRelease(context);
    CGColorSpaceRelease(colorSpace);
    
    // now convert to grayscale
    uint8_t *m_imageData = (uint8_t *) malloc(m_width * m_height);
    for(int y = 0; y < m_height; y++) {
        for(int x = 0; x < m_width; x++) {
            uint32_t rgbPixel=rgbImage[y*m_width+x];
            uint32_t sum=0,count=0;
            if (colors & kRed) {sum += (rgbPixel>>24)&255; count++;}
            if (colors & kGreen) {sum += (rgbPixel>>16)&255; count++;}
            if (colors & kBlue) {sum += (rgbPixel>>8)&255; count++;}
            m_imageData[y*m_width+x]=sum/count;
        }
    }
    free(rgbImage);
    
    // convert from a gray scale image back into a UIImage
    uint8_t *result = (uint8_t *) calloc(m_width * m_height *sizeof(uint32_t), 1);
    
    // process the image back to rgb
    for(int i = 0; i < m_height * m_width; i++) {
        result[i*4]=0;
        int val=m_imageData[i];
        result[i*4+1]=val;
        result[i*4+2]=val;
        result[i*4+3]=val;
    }
    
    // create a UIImage
    colorSpace = CGColorSpaceCreateDeviceRGB();
    context = CGBitmapContextCreate(result, m_width, m_height, 8, m_width * sizeof(uint32_t), colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaNoneSkipLast);
    CGImageRef image = CGBitmapContextCreateImage(context);
    CGContextRelease(context);
    CGColorSpaceRelease(colorSpace);
    UIImage *resultUIImage = [UIImage imageWithCGImage:image];
    CGImageRelease(image);
    
    free(m_imageData);
    
    // make sure the data will be released by giving it to an autoreleased NSData
    [NSData dataWithBytesNoCopy:result length:m_width * m_height];
    
    return resultUIImage;
}

- (UIImage *)imageWithImage:(UIImage *)image scaledToSize:(CGSize)newSize {
    UIGraphicsBeginImageContextWithOptions(newSize, NO, 0.0);
    [image drawInRect:CGRectMake(0, 0, newSize.width, newSize.height)];
    UIImage *newImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    return newImage;
}

-(IBAction)reprocessImage:(id)sender{
    
    int spacing = 36;
    int new_spacing = (int)round(spacing * [contrastSlider value]);
    int area = 5*new_spacing;
    int padding = (int)round((255-area) /2);
    
    int currentLevel;
    NSMutableArray *enhanced_levels = [[NSMutableArray alloc] init];
    currentLevel = 255-padding;
    for (int i=0;i<6;i++){
        [enhanced_levels addObject:[NSNumber numberWithInt:currentLevel]];
        currentLevel = currentLevel -= new_spacing;
    }
    
    float value = [brightnessSlider value] + 0.5;
    
    int numlevels = [enhanced_levels count];
    for(int i=0; i<numlevels;i++){
        int neutralValue = [enhanced_levels[i] intValue];
        int newValue = (int)round(neutralValue*value);
        [levels setObject:[NSNumber numberWithInt:newValue] atIndexedSubscript:i];
    }
    
    if(selectedImage != nil){
        [self generatePreview];
    }
    
    [enhanced_levels release];
    
}

-(void)generatePreview{
    
    UIImage *image = previewImage;
    
    int counter = 0;
        
    struct pixel* pixels = (struct pixel*) calloc(1, image.size.width * image.size.height * sizeof(struct pixel));
    struct pixel* firstpixel = pixels;
    
    if (pixels != nil)
    {
        
        CGContextRef context = CGBitmapContextCreate(
                                                     (void*) pixels,
                                                     image.size.width,
                                                     image.size.height,
                                                     8,
                                                     image.size.width * 4,
                                                     CGImageGetColorSpace(image.CGImage),
                                                     kCGImageAlphaPremultipliedLast
                                                     );
        
        if (context != NULL)
        {
            
            CGContextDrawImage(context, CGRectMake(0.0f, 0.0f, image.size.width, image.size.height), image.CGImage);
            
            NSUInteger numberOfPixels = image.size.width * image.size.height;
            
            while (numberOfPixels > 0) {
                
                if (pixels->r > [levels[0] intValue]){
                    pixels->r = 255;
                    pixels->g = 255;
                    pixels->b = 255;
                    pixels->a = 255;
                }else if (pixels->r > [levels[1] intValue]){
                    pixels->r = 220;
                    pixels->g = 220;
                    pixels->b = 220;
                    pixels->a = 255;
                }else if (pixels->r > [levels[2] intValue]){
                    pixels->r = 170;
                    pixels->g = 170;
                    pixels->b = 170;
                    pixels->a = 255;
                }else if (pixels->r > [levels[3] intValue]){
                    pixels->r = 255;
                    pixels->g = 100;
                    pixels->b = 100;
                    pixels->a = 255;
                }else if (pixels->r > [levels[4] intValue]){
                    pixels->r = 255;
                    pixels->g = 0;
                    pixels->b = 0;
                    pixels->a = 255;
                }else if (pixels->r > [levels[5] intValue]){
                    pixels->r = 80;
                    pixels->g = 30;
                    pixels->b = 30;
                    pixels->a = 255;
                }else{
                    pixels->r = 0;
                    pixels->g = 0;
                    pixels->b = 0;
                    pixels->a = 255;
                };
                pixels++;
                numberOfPixels--;
                counter++;
            }
            
            CGImageRef cgImage=CGBitmapContextCreateImage(context);
            
            UIImage * newimage = [UIImage imageWithCGImage:cgImage];
            CGImageRelease(cgImage);
            
            CGContextRelease(context);
            
            imageview.image = newimage;
        }
        
    }
    
    free(firstpixel);
}

- (void) processImage
{
        
    // 1 mpix image
    UIImage *image  = [self imageWithImage:selectedImage scaledToSize:CGSizeMake(1000.0, 1000.0)];
    image = [self convertToGreyscale:image];

    char buffer[1000000+6];
    int counter = 0;
    
    int numlevels = [levels count];
    for(int i=0; i<numlevels;i++){
        buffer[counter] = [levels[i] charValue];
        counter ++;
    }
        
    struct pixel* pixels = (struct pixel*) calloc(1, image.size.width * image.size.height * sizeof(struct pixel));
    struct pixel* firstpixel = pixels;
    
    if (pixels != nil)
    {
        
        CGContextRef context = CGBitmapContextCreate(
                                                     (void*) pixels,
                                                     image.size.width,
                                                     image.size.height,
                                                     8,
                                                     image.size.width * 4,
                                                     CGImageGetColorSpace(image.CGImage),
                                                     kCGImageAlphaPremultipliedLast
                                                     );
        
        if (context != NULL)
        {

            CGContextDrawImage(context, CGRectMake(0.0f, 0.0f, image.size.width, image.size.height), image.CGImage);
            
            NSUInteger numberOfPixels = image.size.width * image.size.height;
            
            while (numberOfPixels > 0) {
                buffer[counter] = pixels->r;
                pixels++;
                numberOfPixels--;
                counter++;
            }
            
            CGContextRelease(context);
            

        }
        
    }

    free(firstpixel);
    
    [blackstripesData release];
    blackstripesData = [[NSData dataWithBytes:buffer length:1000000+6] retain];
}

-(IBAction)connect:(id)sender{
            
    if(selectedImage == nil){
        
        NSString *title = @"Blackstripes wants input";
        NSString *message = @"Blackstripes needs an image please select an image first.";
        
        UIAlertView *alert = [[UIAlertView alloc] initWithTitle:title
                                                        message:message
                                                       delegate:self
                                              cancelButtonTitle:@"OK"
                                              otherButtonTitles:nil];
        [alert show];
        [alert release];
        return;
        
    }
    
    NSError *error = nil;
    if (![asyncSocket connectToHost:@"192.168.0.102" onPort:20001 withTimeout:3.0 error:&error])
    {
        NSLog(@"ERROR %@",error);
        [asyncSocket disconnect];
    }else{
        NSLog(@"OK trying to connect");
    }
}

- (void)socket:(GCDAsyncSocket *)sock didWriteDataWithTag:(long)tag{
      [asyncSocket disconnect];
}

- (void)socketDidDisconnect:(GCDAsyncSocket *)sock withError:(NSError *)err{
    
    NSString *title;
    NSString *message;
    if([err code] == 61){
        title = @"Blackstripes is busy";
        message = @"Blackstripes is busy drawing, please wait.";
    }else if([err code] == 7){
        title = @"Blackstripes";
        message = @"Blackstripes received your drawing, thanks!";
    }else if([err code] == 0){
        title = @"Blackstripes is busy";
        message = @"Please try again!";
    }else{
        title = @"Blackstripes is busy";
        message = @"Blackstripes has encountered an error, please try again.";
    }
    
    UIAlertView *alert = [[UIAlertView alloc] initWithTitle:title
                                                    message:message
                                                   delegate:self
                                          cancelButtonTitle:@"OK"
                                          otherButtonTitles:nil];
    [alert show];
    [alert release];
    return;
}

- (void)socket:(GCDAsyncSocket *)sock didConnectToHost:(NSString *)host port:(UInt16)port
{
	
    
    if(selectedImage != nil){
        [self processImage];
        [self writeBlackstripes:blackstripesData];
        NSData* term = [@"EOF" dataUsingEncoding:[NSString defaultCStringEncoding]];
        [self writeBlackstripes:term];
        
    }else{
        
        NSString *title = @"Blackstripes wants input";
        NSString *message = @"Blackstripes needs an image please select an image first.";
        
        UIAlertView *alert = [[UIAlertView alloc] initWithTitle:title
                                                        message:message
                                                       delegate:self
                                              cancelButtonTitle:@"OK"
                                              otherButtonTitles:nil];
        [alert show];
        [alert release];
        return;
        
    }
    
}


// the server wil shut down after this and the machine will start drawing
// socketDidDisconnect will trigger with error code 7
-(void)writeBlackstripes:(NSData *)data{
    [asyncSocket writeData:data withTimeout:-1 tag:3];
}

- (void)actionSheet:(UIActionSheet *)actionSheet clickedButtonAtIndex:(NSInteger)buttonIndex{
    if(buttonIndex==0){
        [self libraryAction:nil];
    }else if(buttonIndex==1){
        [self camAction];
    }
}



- (void)imagePickerController:(UIImagePickerController *)picker didFinishPickingMediaWithInfo:(NSDictionary *)info{

    
    NSString* mediaType = [info objectForKey:UIImagePickerControllerMediaType];
    UIImage* picture = nil;
    
    if (CFStringCompare((CFStringRef) mediaType, kUTTypeImage, 0) == kCFCompareEqualTo) {
        picture = [info objectForKey:UIImagePickerControllerEditedImage];
        if (!picture)
            picture = [info objectForKey:UIImagePickerControllerOriginalImage];
        
    }
    
    [self dismissViewControllerAnimated:YES completion:nil];
    
    //cache de selected image
    UIImage *newImage = [picture retain];
    [selectedImage release];
    selectedImage = newImage;
    
    //and a preview image (retina 560x560)
    UIImage *newPreviewImage  = [self imageWithImage:selectedImage scaledToSize:CGSizeMake(560.0, 560.0)];
    newPreviewImage = [[self convertToGreyscale:newPreviewImage] retain];
    [previewImage release];
    previewImage = newPreviewImage;
    
    [self generatePreview];
    
}


@end
