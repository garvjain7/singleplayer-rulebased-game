from dataclasses import dataclass, field
from typing import Callable


# ================= VALUE OBJECT ================= #

@dataclass
class RuleValue:
    number: int
    tags: list[str] = field(default_factory=list)
    banned: bool = False

    def tag(self, text: str) -> "RuleValue":
        self.tags.append(text)
        return self

    def ban(self) -> "RuleValue":
        self.banned = True
        return self

    def render(self) -> str:
        if self.banned:
            raise Exception(f"Game Over ❌ — {self.number} is banned")
        return " ".join(self.tags) if self.tags else str(self.number)


# ================= RULE METADATA ================= #

@dataclass
class RuleEntry:
    """A rule function paired with human-readable metadata for conflict checking and display."""
    kind: str            # 'swap', 'replace', 'ban', 'divisible', 'odd', 'even'
    params: dict         # e.g. {'a': 6, 'b': 9} or {'num': 4} or {'divisor': 3, 'text': 'Fizz'}
    description: str     # human-readable summary
    fn: Callable         # the actual rule function

    def __str__(self):
        return self.description


# ================= CONFLICT CHECKER ================= #

class ConflictChecker:
    """
    Analyses a proposed rule against existing ones and reports conflicts.

    Detected cases:
      1. Duplicate rule already exists (same kind + params).
      2. Rule targets a number that is already banned.
      3. Swap involves a number that is already banned.
    """

    def __init__(self, active_rules: list[RuleEntry]):
        self.active = active_rules

    def banned_numbers(self) -> set[int]:
        return {r.params['num'] for r in self.active if r.kind == 'ban'}

    def check(self, proposed: RuleEntry) -> str | None:
        """Return a conflict message, or None if the rule is clean."""
        banned = self.banned_numbers()

        # 1. Duplicate
        for existing in self.active:
            if existing.kind == proposed.kind and existing.params == proposed.params:
                return f"An identical rule already exists → [{existing}]"

        # 2. Rule targets a banned number
        if proposed.kind == 'replace':
            n = proposed.params['num']
            if n in banned:
                return f"{n} is already banned — a replace rule for it would never fire"

        # 3. Swap involves a banned number
        if proposed.kind == 'swap':
            for side in ('a', 'b'):
                n = proposed.params[side]
                if n in banned:
                    return f"{n} is already banned — it cannot participate in a swap"

        return None


# ================= RULE FACTORY ================= #

class Rules:

    @staticmethod
    def swap(a: int, b: int) -> RuleEntry:
        def fn(rv: RuleValue) -> RuleValue:
            if rv.number == a:   rv.number = b
            elif rv.number == b: rv.number = a
            return rv
        return RuleEntry('swap', {'a': a, 'b': b}, f"Swap {a} ↔ {b}", fn)

    @staticmethod
    def replace(num: int, text: str) -> RuleEntry:
        fn = lambda rv: rv.tag(text) if rv.number == num else rv
        return RuleEntry('replace', {'num': num, 'text': text}, f"Replace {num} → '{text}'", fn)

    @staticmethod
    def ban(num: int) -> RuleEntry:
        fn = lambda rv: rv.ban() if rv.number == num else rv
        return RuleEntry('ban', {'num': num}, f"Ban {num}", fn)

    @staticmethod
    def divisible(divisor: int, text: str) -> RuleEntry:
        if divisor == 0:
            raise ValueError("Divisor cannot be zero.")

        def fn(rv: RuleValue) -> RuleValue:
            if rv.number % divisor == 0:
                rv.tag(text)
            return rv

        return RuleEntry(
            'divisible',
            {'divisor': divisor, 'text': text},
            f"Divisible by {divisor} → '{text}'",
            fn
        )

    @staticmethod
    def odd(text: str) -> RuleEntry:
        fn = lambda rv: rv.tag(text) if rv.number % 2 != 0 else rv
        return RuleEntry('odd', {'text': text}, f"Odd → '{text}'", fn)

    @staticmethod
    def even(text: str) -> RuleEntry:
        fn = lambda rv: rv.tag(text) if rv.number % 2 == 0 else rv
        return RuleEntry('even', {'text': text}, f"Even → '{text}'", fn)


# ================= PREDEFINED RULES ================= #

PREDEFINED = {
    1: ("Swap 6 ↔ 9",            lambda: Rules.swap(6, 9)),
    2: ("Replace 1 → 'ewww 1'",  lambda: Rules.replace(1, "ewww 1")),
    3: ("Ban 4",                  lambda: Rules.ban(4)),
    4: ("Divisible by 3 → Fizz", lambda: Rules.divisible(3, "Fizz")),
    5: ("Odd → 'Odd'",           lambda: Rules.odd("Odd")),
}

PATTERNS = {
    1: ("Swap A B",          lambda: Rules.swap(int(input("  A: ")), int(input("  B: ")))),
    2: ("Replace N TEXT",    lambda: Rules.replace(int(input("  N: ")), input("  TEXT: "))),
    3: ("Ban N",             lambda: Rules.ban(int(input("  N: ")))),
    4: ("Divisible D TEXT",  lambda: Rules.divisible(int(input("  D: ")), input("  TEXT: "))),
    5: ("Odd TEXT",          lambda: Rules.odd(input("  TEXT: "))),
    6: ("Even TEXT",         lambda: Rules.even(input("  TEXT: "))),
}


# ================= HELPERS ================= #

def prompt_int(prompt: str) -> int | None:
    try:
        return int(input(prompt))
    except ValueError:
        print("  ✗ Please enter a valid integer.")
        return None

def prompt_range() -> tuple[int, int]:
    print("\n  Set number range:")
    while True:
        start = prompt_int("    Start: ")
        end   = prompt_int("    End:   ")
        if start is None or end is None:
            continue
        if start >= end:
            print("  ✗ Start must be less than End.")
            continue
        return start, end


# ================= GAME ================= #

class RuleGame:
    def __init__(self):
        self.active_rules: list[RuleEntry] = []
        self.range_start = 1
        self.range_end   = 10

    # ---- display ----

    def show_active_rules(self):
        if not self.active_rules:
            print("    (no rules active)")
        else:
            for i, r in enumerate(self.active_rules, 1):
                print(f"    {i:>2}. {r}")

    # ---- conflict-aware add ----

    def try_add(self, entry: RuleEntry) -> bool:
        checker = ConflictChecker(self.active_rules)
        conflict = checker.check(entry)
        if conflict:
            print(f"\n  ⚠  Conflict detected: {conflict}")
            return False
        self.active_rules.append(entry)
        print(f"  ✓ Rule added: [{entry}]")
        return True

    # ---- menus ----

    def add_predefined_rule(self):
        print("\n  Predefined Rules:")
        for k, (desc, _) in PREDEFINED.items():
            print(f"    {k}. {desc}")

        choice = prompt_int("  Select: ")
        if choice not in PREDEFINED:
            print("  ✗ Invalid selection.")
            return

        _, builder = PREDEFINED[choice]
        self.try_add(builder())

    def add_custom_rule(self):
        print("\n  Rule Patterns:")
        for k, (desc, _) in PATTERNS.items():
            print(f"    {k}. {desc}")

        choice = prompt_int("  Select pattern: ")
        if choice not in PATTERNS:
            print("  ✗ Invalid pattern.")
            return

        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                _, builder = PATTERNS[choice]
                entry = builder()
            except ValueError:
                print("  ✗ Invalid input — expected a number.")
                return

            if self.try_add(entry):
                return

            if attempt < MAX_RETRIES - 1:
                print(f"  Please define a different rule (attempt {attempt + 2}/{MAX_RETRIES}):")
            else:
                print("  ✗ Max retries reached. Returning to menu.")

    def remove_rule(self):
        if not self.active_rules:
            print("  No rules to remove.")
            return
        print("\n  Active rules:")
        self.show_active_rules()
        choice = prompt_int("  Remove rule #: ")
        if choice is None or not (1 <= choice <= len(self.active_rules)):
            print("  ✗ Invalid number.")
            return
        removed = self.active_rules.pop(choice - 1)
        print(f"  ✓ Removed: [{removed}]")

    def change_range(self):
        self.range_start, self.range_end = prompt_range()
        print(f"  ✓ Range set to {self.range_start}–{self.range_end}")

    # ---- core loop ----

    def run_iteration(self) -> bool:
        try:
            count = self.range_end - self.range_start + 1
            print(f"\n  Range {self.range_start}–{self.range_end} ({count} numbers) | "
                  f"Rules active: {len(self.active_rules)}")

            # Build a map of number -> applicable rule (latest rule wins on conflict)
            rule_map: dict[int, RuleEntry] = {}
            banned_numbers: set[int] = set()

            for rule in self.active_rules:
                if rule.kind == 'ban':
                    banned_numbers.add(rule.params['num'])
                else:
                    # For non-ban rules, apply to all numbers they target
                    if rule.kind == 'swap':
                        # Swap applies to both numbers in the swap
                        rule_map[rule.params['a']] = rule
                        rule_map[rule.params['b']] = rule
                    elif rule.kind == 'replace':
                        rule_map[rule.params['num']] = rule
                    else:
                        # For divisible, odd, even: apply to all numbers in range
                        for n in range(self.range_start, self.range_end + 1):
                            if rule.kind == 'divisible':
                                if n % rule.params['divisor'] == 0:
                                    rule_map[n] = rule
                            elif rule.kind == 'odd':
                                if n % 2 != 0:
                                    rule_map[n] = rule
                            elif rule.kind == 'even':
                                if n % 2 == 0:
                                    rule_map[n] = rule

            for num in range(self.range_start, self.range_end + 1):
                # Compute expected result based on latest applicable rule
                rv = RuleValue(number=num)

                # If there's a rule for this number, apply only that rule
                if num in rule_map:
                    rv = rule_map[num].fn(rv)

                expected = rv.render()

                # If the number itself is banned, replace expected with next non-banned number
                if num in banned_numbers:
                    next_num = num + 1
                    while next_num in banned_numbers:
                        next_num += 1
                    expected = str(next_num)

                # Ask the player for their move
                player_input = input(f"  {num}: Your move? ").strip()

                if player_input != expected:
                    print(f"\n  ✗ Incorrect — expected: {expected!r}. Game Over.")
                    return False

            print("\n  ✓ All moves correct for this iteration.")
            return True

        except Exception as e:
            print(f"\n  {e}")
            return False


# ================= ENTRY POINT ================= #

game = RuleGame()
iteration = 1

while True:
    print(f"\n{'='*55}")
    print(f"  Iteration {iteration}  |  "
          f"Range: {game.range_start}–{game.range_end}  |  "
          f"Rules: {len(game.active_rules)}")
    print(f"{'='*55}")

    if iteration > 1:
        print("\n  Active rules:")
        game.show_active_rules()

        print("\n  1. Add Predefined Rule")
        print("  2. Add Custom Rule")
        print("  3. Remove a Rule")
        print("  4. Change Range")
        print("  5. Run this iteration")

        choice = prompt_int("\n  Choose: ")

        if   choice == 1: game.add_predefined_rule()
        elif choice == 2: game.add_custom_rule()
        elif choice == 3: game.remove_rule()
        elif choice == 4: game.change_range()
        elif choice == 5: pass
        else:
            print("  ✗ Invalid choice.")
        
        if choice != 5:
            continue

    if not game.run_iteration():
        break

    iteration += 1