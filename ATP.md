# Introduction #

ATP.ini contains all parameters specific to the ATP.


# Required Entries #
## [Settings](ATP.md) ##
Contains the general ATP Settings.
| Argument | Description |
|:---------|:------------|
| binary | Absolute path of the ATP binary |
| time | Time parameter of the ATP |
| problem  | Problem parameter of the ATP |
| strategy | How parameters are passed to the ATP. Choices are E,Leo,Satallax |
| default | Parameters that should always be passed to the ATP |

There are three different supported ways of encoding a strategy.
They are named after the ATP that require them.
| Leo | Parameters and their values are joined by a space. E.g. --ordering 3 |
|:----|:---------------------------------------------------------------------|
| E | Parameters and their values are joined by = if the parameter starts with --. Else the parameter is directly joined with its value. E.g. --ordering=3 -sine13|
| Satallax | The parameters are written in a new mode file modeFile. The ATP is then called with ATP -m modeFile.|

## [Parameters](Boolean.md) ##
Contains parameters that are either present or not present.
Due to python constraints, each parameter has to be followed by _= False_.

## List Parameters ##
Contains parameters with arbitrary arguments.
The arguments are listed after the = sign, separated by space.

# Example #
```
[ATP Settings]
binary = /scratch/kuehlwein/leo2/bin/leo
time = -t
problem =
strategy = Leo
default = --atp e=/scratch/kuehlwein/E1.7/PROVER/eprover --noslices

[Boolean Parameters]
--expand_exuni = False
--notReplLeibnizEQ = False
--notReplAndrewsEQ = False
--notUseChoice = False
--notExtuni = False
--notUseExtCnfCmbd = False
--unfolddefsearly = False
--unfolddefslate = False


[List Parameters]
--atptimeout = 0.2 0.5 1.0 2.0 4.0 8.0 16 32 64
--primsubst = 0 1 2 3 4
--relevancefilter = 0 1 2 3 4 5 6
--order = none naive
--translation = kerber fully-typed fof_experiment tff_experiment fof_full fof_experiment_erased
--unidepth = 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
```