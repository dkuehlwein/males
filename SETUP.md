# Introduction #

The setup.ini configures the general behaviour of MaLeS, in dependent of the ATP.


# Details #

Add your content here.  Format your content with:
  * Text in **bold** or _italic_
  * Headings, paragraphs, and lists
  * Automatic links to other wiki pages


# Example #

```
[Settings]
TPTP = /scratch/kuehlwein/TPTP-v5.4.0
TmpDir = /scratch/kuehlwein/males/tmp
Cores = 31
ResultsDir = /scratch/kuehlwein/males/resultsLeo
ResultsPickle = /scratch/kuehlwein/males/tmp/resultsLeo.pickle
TmpResultsDir = /scratch/kuehlwein/males/resultsLeoTmp
TmpResultsPickle = /scratch/kuehlwein/males/tmp/resultsLeoTmp.pickle
Clear = False
LogToFile = False
LogFile = /scratch/kuehlwein/males/tmp/leo.log
THFSine = False

[Search]
Time = 10
Problems = /scratch/kuehlwein/males/CASC24TrainingServer
FullTime = False
TryWithNewDefaultTime = False
Walks = 50
WalkLength = 4

[Learn]
Time = 10
MaxTime = 300
Features = TPTP
FeaturesFile = /scratch/kuehlwein/males/tmp/features.pickle
StrategiesFile = /scratch/kuehlwein/males/tmp/strategies.pickle
ModelsFile = /scratch/kuehlwein/males/tmp/models.pickle
RegularizationGrid = 0.25,0.5,1,2,4,8,16,32,64
KernelGrid = 0.125,0.25,0.5,1,2,4,8,16,32,64
CrossValidate = True
CrossValidationFolds = 10
StartStrategies = 20
StartStrategiesTime = 0.5
CPU Bias = 0.3
Tolerance = 0.1
```