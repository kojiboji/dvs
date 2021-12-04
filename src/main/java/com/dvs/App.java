package com.dvs;

import org.bytedeco.opencv.opencv_stitching.Stitcher;
import org.bytedeco.opencv.opencv_videoio.VideoCapture;

public class App {
    //arg 0 is the outputfile
    //arg 1 is time slices
    //one argument for each csv file
    public static void main(String[] args) {
        VideoCapture videoCapture1 = new VideoCapture("/tmp/pre/seoul_21_l000.mp4");
        VideoCapture videoCapture2 = new VideoCapture("~/seoul_21_l.mp4");
        System.out.println("God please");
        System.out.println(videoCapture1.isOpened());
        System.out.println(videoCapture2.isOpened());
        Stitcher stitcher = Stitcher.create();
    }
}
