//
//  BSViewController.h
//  blackstripes
//
//  Created by johan ten broeke on 8/8/13.
//  Copyright (c) 2013 johan ten broeke. All rights reserved.
//

#import <UIKit/UIKit.h>

@class GCDAsyncSocket;

@interface BSViewController : UIViewController <UINavigationControllerDelegate,UIActionSheetDelegate ,UIImagePickerControllerDelegate>{
    IBOutlet UIImageView *imageview;
    GCDAsyncSocket *asyncSocket;
    NSData *blackstripesData;
    UIImage *selectedImage;
    UIImage *previewImage;
    NSArray *neutralLevels;
    NSMutableArray *levels;
    
    IBOutlet UISlider *brightnessSlider;
    IBOutlet UISlider *contrastSlider;
}



@end
