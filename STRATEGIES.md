# Introduction #

Add your content here.


# Details #

Add your content here.  Format your content with:
  * Text in **bold** or _italic_
  * Headings, paragraphs, and lists
  * Automatic links to other wiki pages

> # Example #
```
[NewStrategy37279]
--definitional-cnf = 12
--delete-bad-limit = 1024000000
--destructive-er-aggressive = True
--forward-context-sr = True
--simul-paramod = True
--sine = gf120_h_gu_R02_F100_L20000
--split-clauses = 4
-F = 1
-G = invfreqconjmin
-H = '(10*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5),1*FIFOWeight(ConstPrio))'
-W = SelectNewComplexAHPExceptUniqMaxHorn
-c = 1
-t = KBO6
-w = invfreqrank

[NewStrategy30642]
--definitional-cnf = 24
--delete-bad-limit = 1024000000
--destructive-er = True
--destructive-er-aggressive = True
--forward-context-sr = True
--fp-index = FP7
--prefer-initial-clauses = True
--sine = gf500_h_gu_R04_F100_L20000
--split-aggressive = True
--split-clauses = 4
--split-reuse-defs = True
-F = 1
-G = invfreq
-H = '(10*ConjectureRelativeSymbolWeight(ConstPrio,0.5,100,100,100,50,1.5,1.5,1.5),1*FIFOWeight(ConstPrio))'
-W = SelectSmallestNegLit
-c = 4
-t = KBO6
-w = invaritysquaredmax0
-x = UseWatchlist
```