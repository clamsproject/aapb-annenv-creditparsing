# Preliminary Adjudication/Assessment Report on Round2 and Round3 RFB
The term Adjudication or Assessment will be defined as an evaluation of the annotation data in the attempt to 
combine multiple annotations into an adjudicated raws dataset to be updated for public storage in [aapb-annotations](https://github.com/clamsproject/aapb-annotations).  

Please see the [`./README.md`](./README.md) for more information.  

Round 2 was created around date 231117, and is on a previous Annotation Guideline, probably around v3.5. 
Round 3 (old, early download) was created around date 240201, and is on Annotation Guideline v5.2. 
It only contained a few completed video instances from 20017(G) and 20019(J). 
Assumptively, this should be after the final redo, however, if that's the case, there are unusual small sets of frames from
some random videos that should be done by 20019(J). 
Round 3 (new) was created around date 240223, and is on the Annotation Guideline [v5.2](https://docs.google.com/document/d/1Kxa99JMfDuy-y2xFqmgPkuLnLqEGhNB8iMxBT3E1Tx4/edit) or v5.3.  
It is for sure done on the most recent redo of the data and is the most current. 
Thus these two rounds require scrutiny to update Round 2 to match Guidelines v5.3 and Round 3 raw data. 

## Contents R1
R1 ended up being practice and Guidelines were still under construction enough to not useful for developing annotations. 

Instances:  
Likely 20003 20004 20005 20006  

## Contents R2
Because the adjudication list of non-matches doesn't explicitly help for checking which images are the first one vs a duplicate, its possible 
that this should be looked into even after the adjud-raw is created from R2. 

A very large set was used for IAA for R2.   
Annotators for R2:   
20007 G - Annotator  
20008 D - IAA calc writer / Annotator  

Numbers of files/annotations ====  
Number of files without 'skip': 367  
Noskips from both annotators: 171 (might be 1 extra)  
No skip from the annotator which skipped less: 236  
total annotations:  3700  
Going thru it manually there is some concern also that there are some files where G/annotator1 did {skip:dup}, and D/annotator2 {skip:no-text}.  

## Contents R3
Annotators for IAA set:  
G 20017 - Annotator (20018 and 20019 are not yet started.)  
J 20019 20029 20039 - Annotation Manager  

The IAA Adjudication Set set forth by J is:   
Chyron set only, 20017 20019 as G has not started on slates nor credits. 
GUID    image #  
cpb-aacip-507-6t0gt5g28c (80)   
cpb-aacip-507-rj48p5w80b (108)  
cpb-aacip-507-154dn40c26 (300)
Total: 488 images 
However, we noticed that G's instance does not put then in the same order as J's. Therefore when R3 old 240201 was downloaded,
that dataset did not contain the same videos as finished for annotation.  

These are the other counts for the adjucation sets in slates and credits. 

J 20029 slate  
cpb-aacip-507-6t0gt5g28c (66)  
cpb-aacip-507-rj48p5w80b (56)  
cpb-aacip-507-154dn40c26 (84)  
subtot: 206  

J 20039 credits  
cpb-aacip-507-6t0gt5g28c (208)   
cpb-aacip-507-rj48p5w80b (184)  
cpb-aacip-507-154dn40c26 (186)  
subtot: 578  

tot: 1192 images - near 1200  
These are all annotated and ready for adjudication.  

### R3 old 240201 
RFB IAA numbers for chyrons: 20017 20019 (half-done by G, all done J)

py evaluation/src/rfb_agreement.py -i ./adjud-r3_eval  

Num of images annotated by G 20017: (This means G was only about 2 videos in when this set was downloaded).  
ls ./adjud-r3_eval/20017 -l | grep "^-" | wc -l  
317  
  
Num of images annotated by J 20019: (This is confirmed total image count of the 3 adjud set videos.)  
$ ls ./adjud-r3_eval/20019 -l | grep "^-" | wc -l  
488  
  
This should get the number of annotations without "skip" in them for G 20017. Out of 317, this number doesn't seem right.  
Note: This count code was used previously, and assumptively gave more realistic results in R2.  
$ echo "Number of files without 'skip' in content: $(grep -L 'skip' ./adjud-r3_eval/20017/* | wc -l)" Number of files without 'skip' in content:  
28  

Non-skip annotations for J 20019. Also feels low, but possible.  
Note: this is 59/488, so adding 180 to the denominator nearly doubled the non-skips?  
$ echo "Number of files without 'skip' in content: $(grep -L 'skip' ./adjud-r3_eval/20019/* | wc -l)" Number of files without 'skip' in content:  
59  

Total length of the mismatched annotations for non-skip. This doesn't make sense yet either. 
Perhaps the qualification for non-skip is different than mentally anticipated. It was expected couldn't be higher than 28. 
wc -l < adjud-r3_eval/r3_old_noskip_results.csv  
77  
  
This is apparently the number of no-skips to be evaluated...?   
wc -l < adjud-r3_eval/r3_skips_results.csv  
726  
this is with skips, this number doesnt add up/ (805 = 317+488). Its unclear what this count of annotations means.  

Investigation:
Main problem is that the starting set that G did is different from the starting set J did. I(J) suspect it only overlaps on one GUID in fact - cpb-aacip-507-6t0gt5g28c.
Continued investigation: The [./adjud-r3-240201-old-data_eval/r3_old_noskip_results.csv](./adjud-r3-240201-old-data_eval/r3_old_noskip_results.csv)
actually contains the 3 videos J did but also others that assumptively J did not. 
TODO: Look in visualizer at the results from link above. 

### [R3 new 240223](./r3_240223_new_data) 
This new pull of annotations also did not have the 3 adjudicated set. 

### Current Annotation Progress
G has prioritized and finished the 3 videos requested in 20017. 
The annotations should be curled from `http://julia-child.cs-i.brandeis.edu:44444/{insert_instance_num}`.  
Suggest, delete R3 new 240223 and look at the new curled set. 
