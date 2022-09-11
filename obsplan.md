# Observations Plan Files for OCA observatory

## Objectives

After evaluationg pros and cons, we decided to introduce new file format for observation plans, which will be used by the new (2022+) OCA observatory software.
As, in some simplification, observations plan is a sequence of command, the format of observations plan file is basically a syntax of kind of programming language.
Because we want the new format to be human-readable, -editable and -managable, we decide to introduce new language instead of using e.g. JSON syntax. 
New format should be somehow similar to ols obsplan files for the **IRIS** and **V16** telescopes and in general to be readable and understandable by astronomers without 
need to RTFM (*read the fantastic manual*).

We want to keep the syntax well-defined and intuitively but uniquely transformable to python dictionary object (and therefore to JSON, YAML etc).
Moreover we want to provide any developers with python package for parsing anf formatting those files.

## The Syntax

We will introduce the proposed syntax step by step showing how to fulfill collection of specific demands

### Simplicity - Single Command
We want the new language to act as internal language of the software, so the simplest form is just single command to be executed rather than full-fledged observation plan.
E.g. we want following text to be proper "program":
```
  WAIT t=20
```
or, a bit more complicated single command
```
  OBJECT HD193901 20:23:35.8 -21:22:14.0 seq = 5/I/60,5/V/70
```
Both of single command lines are understandable for OCA astronomers 
(wait for 20 seconds, make photos of object HD193901 and ra/dec coordinates 20:23:35.8 -21:22:14.0 five times for 50 seconds with filter *I* 
and five times for 70 seconds with filter *V*). Syntactical break down of the last command goes as follows:
* command: `OBJECT`
* positional arguments: `HD193901`, `20:23:35.8`, `-21:22:14.0` - some from the tail may be optional
* keyword arguments: argument named `sequence` of value `5/I/60,5/V/70`. all keyword arguments can be optional

One may say, that it would be more familiar to write just `OBJECT HD193901 20:23:35.8 -21:22:14.0 5/I/60,5/V/70`, indeed 
it's simpler, but we propose coordinates arguments to be optional (we have database of filed position) so one could also write just
```
  OBJECT HD193901 sequence = 5/I/60,5/V/70
```
but we can consider another semantics of the `OBJECT` command.


## Sequences
Sequence is a number of commands each written in unique, single line e.g:
```
WAIT ut=16:00
ZERO seq=15/I/0
DARK seq=10/V/300,10/I/200
DOMEFLAT seq=7/V/20,7/I/20
DOMEFLAT seq=10/str_u/100 domeflat_lamp=0.7
WAIT sunset=-12
SKYFLAT alt=60:00:00 az=270:00:00  seq=10/I/20,10/V/30 
SKYFLAT seq=10/I/0,10/V/0 skyflat_adu=30
WAIT t=600
FOCUS NG31 12:12:12 20:20:20
OBJECT HD193901 20:23:35.8 -21:22:14.0 seq=1/V/300
OBJECT FF_Aql 18:58:14.75 17:21:39.29 seq=5/I/60,5/V/70
OBJECT V496_Aql 19:08:20.77 -07:26:15.89 seq=1/V/20 focus=+30
```

Sometimes, more often than we would like, we have to ask telescope to (re)start sequence from specific instruction 
instead of from the beginning. For such situation, we need some method to refer to this instruction. We see two simplest methods:
we can refer to particular line number, or we can introduce explicit labels. As we want to keep labels optional,
we will use semicolon at the end of the label to avoid confusion label with command. 

The previous example rewritten with sample labels for each line:
```
START: WAIT ut=16:00
00100: ZERO seq=15/I/0
00110: DARK seq=10/V/300,10/I/200
00120: DOMEFLAT seq=7/V/20,7/I/20
00130: DOMEFLAT seq=10/str_u/100 domeflat_lamp=0.7
SUNSET: WAIT sunset=-12
00150: SKYFLAT alt=60:00:00 az=270:00:00  seq=10/I/20,10/V/30 
00160: SKYFLAT seq=10/I/0,10/V/0 skyflat_adu=30
00170: WAIT t=600
00100: FOCUS NG31 12:12:12 20:20:20
OB01:  OBJECT HD193901 20:23:35.8 -21:22:14.0 seq=1/V/300
OB02:  OBJECT FF_Aql 18:58:14.75 17:21:39.29 seq=5/I/60,5/V/70
OB03:  OBJECT V496_Aql 19:08:20.77 -07:26:15.89 seq=1/V/20 focus=+30
```

Introduction of labels brings as to something like below as an syntax of single command:
In general the syntax of single command line should be like that:
```
    [LABEL:] <COMMAND> [<POSITIONAL_ARG1> [<POSITIONAL_ARG1>...]] [KW_ARG1_NAME=KW_ARG1_VAL [KW_ARG2_NAME=KW_ARG2_VAL]...]
```

