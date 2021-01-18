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
