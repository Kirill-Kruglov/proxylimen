# B2.3 Local kNN Mechanism Diagnostic

Exploratory diagnostic only. True coordinates are used outside learner path.
Core B2.3 decision artifacts are not modified.

## Metric at crossover

| metric | n=1000,d=130 | n=5000,d=24 | ratio n5000/n1000 | within 1.0±0.2? |
|---|---:|---:|---:|---:|
| global pairwise distance CV | 0.051842 | 0.122557 | 2.364 | false |
| relative contrast k=10 | 0.056174 | 0.176349 | 3.139 | false |
| random-pair shared-neighbor P>1 k=10 | 0.028323 | 0.003965 | 0.140 | false |
| edge-pair shared-neighbor P>1 k=10 | 0.679220 | 0.770894 | 1.135 | true |
| relative contrast k=15 | 0.065135 | 0.203694 | 3.127 | false |
| random-pair shared-neighbor P>1 k=15 | 0.092183 | 0.010850 | 0.118 | false |
| edge-pair shared-neighbor P>1 k=15 | 0.806673 | 0.860988 | 1.067 | true |
| relative contrast k=20 | 0.071889 | 0.224019 | 3.116 | false |
| random-pair shared-neighbor P>1 k=20 | 0.200950 | 0.022817 | 0.114 | false |
| edge-pair shared-neighbor P>1 k=20 | 0.894022 | 0.917810 | 1.027 | true |

## Cell table, k=15

| n | d | global CV | relative contrast k=15 | random-pair shared P>1 | edge-pair shared P>1 |
|---:|---:|---:|---:|---:|---:|
| 1000 | 120 | 0.054053 | 0.068447 | 0.091460 | 0.811710 |
| 1000 | 129 | 0.052127 | 0.065764 | 0.091065 | 0.806253 |
| 1000 | 130 | 0.051842 | 0.065135 | 0.092183 | 0.806673 |
| 1000 | 131 | 0.051757 | 0.064821 | 0.090603 | 0.805447 |
| 1000 | 140 | 0.050052 | 0.062294 | 0.094727 | 0.803260 |
| 5000 | 22 | 0.128147 | 0.220003 | 0.010760 | 0.875649 |
| 5000 | 23 | 0.125239 | 0.211173 | 0.010810 | 0.867751 |
| 5000 | 24 | 0.122557 | 0.203694 | 0.010850 | 0.860988 |
| 5000 | 25 | 0.119969 | 0.195936 | 0.010825 | 0.854192 |
| 5000 | 26 | 0.117593 | 0.189731 | 0.010700 | 0.847402 |

## One-paragraph conclusion

The local metric that best unifies the two crossover points is: edge-pair shared-neighbor P>1 k=15.
