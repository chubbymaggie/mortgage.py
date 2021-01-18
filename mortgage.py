"""
mortgage.py: a simple state-based mortgage calculator
"""

from decimal import Decimal

class PaymentEntry:
    """Record of one payment."""

    def __init__(self, principal, principal_paid, interest_paid,
                 other_costs, total_paid):
        """
        Fields:
        - `principal`:      principal remaining on loan
        - `principal_paid`: part of payment used to pay down principal
        - `interest_paid`:  part of payment used to pay down interest
        - `other_costs`:    other costs (e.g., closing costs)
        - `total_paid`:     total paid on loan so far
        """
        self.principal      = principal
        self.principal_paid = principal_paid
        self.interest_paid  = interest_paid
        self.other_costs    = other_costs
        self.total_paid     = total_paid

    def __str__(self):
        s = ('PaymentEntry({principal}, {principal_paid}, {interest_paid}, '
                          '{other_costs}, {total_paid})')
        return s.format(**self.__dict__)

class PaymentSchedule:
    """Table of payment records."""

    def __init__(self):
        self.data = []

    def append(self, period, entry):
        """Add a payment, timestamped by the period number."""
        self.data.append((period, entry))

    def format(self):
        """Show as a formatted table."""
        header = ('period', 'principal', 'principal_paid', 'interest_paid',
                  'other_costs', 'total_paid')
        # widths for each field
        width = {'period': self._width('period', (p for p, _ in self.data))}
        for h in header[1:]:
            width[h] = self._width(h, (e.__dict__[h] for _, e in self.data))
        # build header
        s = ' | '.join(h.replace('_', ' ').center(width[h]) for h in header)
        s += '\n' + '-+-'.join('-'*width[h] for h in header)
        # format for each record
        fmt = ('{}:>{}'.format(h, width[h]) for h in header)
        fmt = ' | '.join('{' + _ + '}' for _ in fmt)
        # process records
        for period, entry in self.data:
            d = {'period': period}
            d.update(entry.__dict__)
            s += '\n' + fmt.format(**d)
        return s

    @staticmethod
    def _width(name, values):
        """Formatted field width based on field name and values."""
        return max(len(name), max(len(str(value)) for value in values))

class Mortgage:
    """
    Stateful object encapsulating a mortgage loan.

    After initializing with the terms of the loan as specified by the principal,
    interest rate per period, and the number of periods, mortgage payments can
    be simulated for any number of periods by calling `go`. In between such
    runs, various operations are possible:
    - `refinance`:           refinance to a new loan
    - `pay_extra_one_time`:  pay extra principal (non-recurring)
    - `pay_extra_each_time`: pay extra principal each period
    - `pay_other_costs`:     pay other one-time costs (e.g., closing costs)

    By chaining these commands together, complicated mortgage payment schedules
    can be simulated and used to facilitate financing decisions. To see all
    payments made in the form of a formatted table, use `format`.

    Useful member variables:
    - `period`:          current period (from initial mortgage origination)
    - `principal`:       remaining principal
    - `interest_rate`:   interest rate per period
    - `nominal_payment`: payment per period based on loan terms
    - `payment`:         actual payment per period (including extra principal)
    - `total_paid`:      total paid so far
    """

    def __init__(self, principal, interest_rate, periods, other_costs=0):
        """
        Initialize loan. Inputs are internally stored in `Decimal` form and so
        can be input as strings to avoid floating point conversion.
        """
        self.period = 0
        self.table = PaymentSchedule()
        self.total_paid = 0
        self._setup(principal, interest_rate, periods, other_costs=other_costs)

    def _setup(self, principal, interest_rate, periods, other_costs=0):
        """Setup for a new loan."""
        self.principal = self.round(Decimal(principal))
        self.interest_rate = Decimal(interest_rate)
        self.payment = self.nominal_payment = \
            self.payment_per_period(self.principal, self.interest_rate, periods)
        self.total_paid += other_costs
        self._add_payment(other_costs=other_costs)

    @staticmethod
    def round(x):
        """Round to hundredths of a dollar (cents)."""
        return round(x, ndigits=2)

    @staticmethod
    def payment_per_period(P, r, N):
        """
        Nominal payment per period based on loan terms.

        Inputs:
        - `P`: principal
        - `r`: interest rate
        - `N`: periods
        """
        return Mortgage.round(P*r / (1 - (1+r)**(-N)))

    def _add_payment(self, principal_paid=0, interest_paid=0, other_costs=0):
        """Add a payment."""
        entry = PaymentEntry(self.principal, principal_paid, interest_paid,
                             other_costs, self.total_paid)
        self.table.append(self.period, entry)

    def go(self, periods=None):
        """
        Run mortgage for `periods` periods. If not specified (default), run
        until the loan closes.
        """
        end_period = self.period + periods if periods is not None else None
        while True:
            if self.period == end_period: break
            if self.principal == 0: break
            self.period += 1
            new_interest = self.round(self.principal * self.interest_rate)
            interest_paid = min(new_interest, self.payment)
            principal_paid = min(self.principal, self.payment - interest_paid)
            self.principal -= principal_paid
            self.total_paid += principal_paid + interest_paid
            self._add_payment(principal_paid=principal_paid,
                              interest_paid=interest_paid)

    def refinance(self, principal, interest_rate, periods, other_costs=0):
        """
        Refinance loan. The period is not reset, i.e., it counts from the start
        of the original mortgage.
        """
        self._setup(principal, interest_rate, periods, other_costs=other_costs)

    def pay_extra_one_time(self, extra_payment):
        """
        Make one-time (i.e., non-recurring) extra principal payment. This takes
        effect immediately during the current period.
        """
        extra_payment = min(extra_payment, self.principal)
        self.principal -= extra_payment
        self.total_paid += extra_payment
        self._add_payment(principal_paid=extra_payment)

    def pay_extra_each_time(self, extra_payment):
        """
        Pay extra principal each period. This sets the extra amount to pay
        beyond the nominal payment. It has no effect until the next period.
        """
        self.payment = self.nominal_payment + extra_payment

    def pay_other_costs(self, other_costs):
        """
        Pay other one-time (i.e., non-recurring) costs. This does not reduce the
        principal; it only adds to the running total paid. This call takes
        effect immediately during the current period.
        """
        self.total_paid += other_costs
        self._add_payment(other_costs=other_costs)

    def format(self):
        """Show as formatted table."""
        return self.table.format()

    def __str__(self, ndigits='8'):
        """
        Return string representation. Use `ndigits` to specify the number of
        digits after the decimal point to show for the interest rate.
        """
        fields = (self.period, self.principal, self.total_paid)
        width = max(len(str(_)) for _ in fields)
        ifmt = '{:>.' + ndigits + 'f}'
        width = max(width, len(ifmt.format(self.interest_rate)))
        fmt = str(width)
        ifmt = '{}.{}f'.format(width, ndigits)
        d = {'period': self.period,
             'fmt':    fmt,
             'ifmt':   ifmt}
        d.update(self.__dict__)
        s = """\
Mortgage:
  period:        {period:>{fmt}}
  principal:     {principal:>{fmt}}
  interest rate: {interest_rate:>{ifmt}}
  total paid:    {total_paid:>{fmt}}""".format(**d)
        return s
