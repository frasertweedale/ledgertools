# This file is part of ledgertools
# Copyright (C) 2011 Fraser Tweedale
#
# ledgertools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtkchartlib.ringchart

RCI = gtkchartlib.ringchart.RingChartItem

# show only accounts in credit or debit, or both
SHOW_ALL = 0
SHOW_CREDIT = 1
SHOW_DEBIT = 2


def balance_to_ringchart_items(balance, account='', show=SHOW_CREDIT):
    """Convert a balance data structure into RingChartItem objects."""
    show = show if show else SHOW_CREDIT  # cannot show all in ring chart
    rcis = []
    for item in balance:
        subaccount = item['account_fragment'] if not account \
            else ':'.join((account, item['account_fragment']))
        ch = balance_to_ringchart_items(item['children'], subaccount, show)
        amount = item['balance'] if show == SHOW_CREDIT else -item['balance']
        if amount < 0:
            continue  # omit negative amounts
        wedge_amount = max(amount, sum(map(float, ch)))
        rci = gtkchartlib.ringchart.RingChartItem(
            wedge_amount,
            tooltip='{}\n{}'.format(subaccount, wedge_amount),
            items=ch
        )
        rcis.append(rci)
    return rcis
