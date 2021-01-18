# mortgage.py

This is a very simple mortgage payment calculator, designed to help answer questions like:

- How much do I save by refinancing?
- What is the effect of making a large one-time payment?
- What about paying extra principal each month?

The intended target is the American mortgage, but it may well be used for other types of loans also.

There is really not much here other than the "innovation" that complicated mortgage payment schedules can be simulated relatively cleanly by representing the mortgage as a stateful object, whose state (e.g., how much to pay) can be modified from period to period.

An illustrative example will show the supported features.

## Demo

In this example, we simulate a mortgage that is:
- paid for a year according to its initial terms; then
- refinanced to different terms; then
- paid according to that for two months before making a large one-time payment, then again for another two months; and finally
- paying extra principal each month until close.

The details below should be self-explanatory:

```python
from mortgage import Mortgage
from decimal import Decimal  # avoid floating point conversion

# initial loan: $300K at 4% over 5 years (interest charged monthly)
principal = 300_000
interest_rate = Decimal('0.04') / 12  # monthly rate = 4% / 12
periods = 60                          # 5 years = 60 months
m = Mortgage(principal, interest_rate, periods)

# pay loan as usual for one year ...
m.go(12)

# ... then refinance to a better rate
principal = 245_000
interest_rate = Decimal('0.03') / 12
periods = 60
m.refinance(principal, interest_rate, periods, other_costs=2_000)

# go for two months
m.go(2)

# make a large one-time payment and go again
m.pay_extra_one_time(120_000)
m.go(2)

# pay extra each month and go until close
m.pay_extra_each_time(3_000)
m.go()

# see details of how much paid each month
print(m.format())
```

The output is:

```
period | principal | principal paid | interest paid | other costs | total paid
-------+-----------+----------------+---------------+-------------+-----------
     0 | 300000.00 |              0 |             0 |           0 |          0
     1 | 295475.04 |        4524.96 |       1000.00 |           0 |    5524.96
     2 | 290935.00 |        4540.04 |        984.92 |           0 |   11049.92
     3 | 286379.82 |        4555.18 |        969.78 |           0 |   16574.88
     4 | 281809.46 |        4570.36 |        954.60 |           0 |   22099.84
     5 | 277223.86 |        4585.60 |        939.36 |           0 |   27624.80
     6 | 272622.98 |        4600.88 |        924.08 |           0 |   33149.76
     7 | 268006.76 |        4616.22 |        908.74 |           0 |   38674.72
     8 | 263375.16 |        4631.60 |        893.36 |           0 |   44199.68
     9 | 258728.12 |        4647.04 |        877.92 |           0 |   49724.64
    10 | 254065.59 |        4662.53 |        862.43 |           0 |   55249.60
    11 | 249387.52 |        4678.07 |        846.89 |           0 |   60774.56
    12 | 244693.85 |        4693.67 |        831.29 |           0 |   66299.52
    12 | 245000.00 |              0 |             0 |        2000 |   68299.52
    13 | 241210.17 |        3789.83 |        612.50 |           0 |   72701.85
    14 | 237410.87 |        3799.30 |        603.03 |           0 |   77104.18
    14 | 117410.87 |         120000 |             0 |           0 |  197104.18
    15 | 113302.07 |        4108.80 |        293.53 |           0 |  201506.51
    16 | 109183.00 |        4119.07 |        283.26 |           0 |  205908.84
    17 | 102053.63 |        7129.37 |        272.96 |           0 |  213311.17
    18 |  94906.43 |        7147.20 |        255.13 |           0 |  220713.50
    19 |  87741.37 |        7165.06 |        237.27 |           0 |  228115.83
    20 |  80558.39 |        7182.98 |        219.35 |           0 |  235518.16
    21 |  73357.46 |        7200.93 |        201.40 |           0 |  242920.49
    22 |  66138.52 |        7218.94 |        183.39 |           0 |  250322.82
    23 |  58901.54 |        7236.98 |        165.35 |           0 |  257725.15
    24 |  51646.46 |        7255.08 |        147.25 |           0 |  265127.48
    25 |  44373.25 |        7273.21 |        129.12 |           0 |  272529.81
    26 |  37081.85 |        7291.40 |        110.93 |           0 |  279932.14
    27 |  29772.22 |        7309.63 |         92.70 |           0 |  287334.47
    28 |  22444.32 |        7327.90 |         74.43 |           0 |  294736.80
    29 |  15098.10 |        7346.22 |         56.11 |           0 |  302139.13
    30 |   7733.52 |        7364.58 |         37.75 |           0 |  309541.46
    31 |    350.52 |        7383.00 |         19.33 |           0 |  316943.79
    32 |      0.00 |         350.52 |          0.88 |           0 |  317295.19
```

which shows that the loan is paid off after 32 periods from the origination of the initial mortgage, with a total payment of $317,295.19 (vs. the original $300,000 loan). For each period, the data show:
- the remaining principal;
- the amount of that period's payment going toward the principal;
- the amount of that period's payment going toward interest;
- other costs (e.g., closing costs); and
- the total paid so far.
