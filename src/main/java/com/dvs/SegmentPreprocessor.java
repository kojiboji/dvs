package com.dvs;

import com.opencsv.bean.CsvToBeanBuilder;

import javax.validation.constraints.NotNull;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.util.ArrayList;

public class SegmentPreprocessor {
    public static ArrayList<ArrayList<Segment>> makeSegments(String @NotNull [] csvFiles) throws FileNotFoundException {
        ArrayList<ArrayList<Segment>> segmentLists = new ArrayList<>(csvFiles.length);
        for (String csvFile : csvFiles) {
            segmentLists.add(new ArrayList<>(new CsvToBeanBuilder<Segment>(new FileReader(csvFile)).withType(Segment.class).build().parse()));
        }
        return segmentLists;
    }
}
