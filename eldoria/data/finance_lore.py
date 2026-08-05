"""Real-world facts woven into the game: personal finance at the Bank, and history from Mr. Wright.

Every fact here is a genuine, checkable claim, not flavor invented to sound
plausible -- the finance facts are standard personal-finance literacy, and
the Wright Brothers facts were verified against the National Park Service,
the Smithsonian National Air and Space Museum, and the FAA (see the session
that added this file for the actual research). The point is to teach
something real while playing, the same way a good MUD teaches its own world.
"""
from __future__ import annotations

FINANCE_TIPS: tuple[str, ...] = (
    "Compound interest is interest earned on interest -- the earlier you start saving, the more time your money has to snowball.",
    "The Rule of 72: divide 72 by an interest rate (as a percent) to estimate how many periods it takes money to double. At 6%, that's about 12 periods.",
    "Simple interest is calculated only on your original principal, every time. Compound interest is calculated on your principal PLUS all interest already earned -- which is why it grows faster the longer it's left alone.",
    "Diversification means spreading savings or investments across different things instead of one, so a single loss doesn't sink you.",
    "Inflation quietly shrinks what money can buy over time -- gold sitting idle under a mattress is worth less next year than it is today.",
    "Opportunity cost is what you give up by choosing one thing over another -- spending gold now on a sword means that same gold isn't earning interest at the bank.",
    "An APR (annual percentage rate) states a yearly interest rate; APY (annual percentage yield) accounts for compounding, so APY is usually the more honest number for what you'll actually earn.",
    "A withdrawal or transaction fee, even a tiny one, adds up if you move money around often -- small costs compound too, just against you.",
    "An emergency fund is money set aside before you need it, specifically so a bad surprise doesn't force you into debt.",
    "Paying yourself first means setting aside savings before spending on anything else, rather than saving only what's left over.",
    "Debt is compound interest working against you instead of for you -- the same math that grows a bank balance also grows what's owed.",
    "Liquidity means how quickly something can become usable cash without losing value -- coin in your pocket is liquid; wealth locked in a rare artifact is not.",
)

MAGIC_EFFECT_NOTES: dict[str, str] = {
    "Diversified Guard": "Diversification: spreading risk across several things instead of betting everything on one.",
    "Bull Market Vigor": "A 'bull market' is a period of rising prices and optimism -- a bull attacks by thrusting its horns upward.",
    "Bear Market Dread": "A 'bear market' is a period of falling prices and pessimism -- a bear swipes its paws downward, the opposite of a bull's charge.",
    "Liquid Assets": "Liquidity: how fast something converts to usable cash without losing value.",
    "Frozen Assets": "'Frozen' assets can't be quickly accessed or sold -- the opposite of liquidity.",
    "Compounding Focus": "Compound interest: growth calculated on your full balance, including interest already earned, not just the original amount.",
}

WRIGHT_FACTS: tuple[str, ...] = (
    "\"Point of fact,\" he adds, \"the first flight was just twelve seconds and a hundred twenty feet -- Kitty Hawk, North Carolina, December seventeenth, 1903. Orville was at the controls that time.\"",
    "\"Wilbur and I ran a bicycle shop back in Dayton, Ohio,\" he muses. \"Funny thing -- the same know-how for chains and spokes is what got this Flyer off the ground.\"",
    "\"Best flight of that first day went eight hundred fifty-two feet in fifty-nine seconds,\" he says proudly. \"That one was Wilbur's turn at the stick.\"",
    "\"We picked Kitty Hawk for the wind and the soft sand,\" he explains. \"Good lift, forgiving landings -- important, that second part, when you're still figuring it out.\"",
    "\"Took the better part of four years -- gliders, wind-tunnel tests, more crashes than I care to count -- before she ever left the ground under her own power,\" he says, patting the wing.",
)
