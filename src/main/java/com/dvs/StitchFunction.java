package com.dvs;

import org.apache.spark.api.java.function.Function;

public class StitchFunction implements Function<Task, String> {
    private String outputFilename;

    public StitchFunction(String outputFilename){
        this.outputFilename = outputFilename;
    }

    public String call(Task t) {
        DVStitcher dvStitcher = new DVStitcher(t);
        return dvStitcher.stitch();
    }
}
