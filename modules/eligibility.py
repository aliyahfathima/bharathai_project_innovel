from .models import EligibilityResult

def evaluate_eligibility(profile, source_text: str) -> EligibilityResult:
    """
    Conservative rule comparison. It only marks conditions when the retrieved text
    explicitly contains a recognisable condition. Unclear language goes to verification.
    """
    text = (source_text or "").lower()
    satisfied, not_satisfied, missing, verify = [], [], [], []

    if profile.age is None:
        missing.append("Age")
    else:
        # Detect simple age bounds only; complex rules are not auto-decided.
        import re
        age_ranges = re.findall(r"(?:age|aged|between)\D{0,15}(\d{1,3})\s*(?:to|-|and)\s*(\d{1,3})", text)
        age_max = re.search(r"(?:below|under|less than|up to)\s*(\d{1,3})\s*years?", text)
        age_min = re.search(r"(?:above|over|at least|minimum age)\s*(\d{1,3})\s*years?", text)
        if age_ranges:
            lo, hi = map(int, age_ranges[0])
            (satisfied if lo <= profile.age <= hi else not_satisfied).append(
                f"Age {profile.age}: source indicates age range {lo}–{hi}"
            )
        elif age_max:
            n = int(age_max.group(1))
            (satisfied if profile.age < n else not_satisfied).append(
                f"Age {profile.age}: source mentions below {n} years"
            )
        elif age_min:
            n = int(age_min.group(1))
            (satisfied if profile.age >= n else not_satisfied).append(
                f"Age {profile.age}: source mentions minimum age {n}"
            )
        else:
            verify.append("Age condition needs manual confirmation from the official scheme rules.")

    if profile.annual_income is None:
        missing.append("Annual family income")
    else:
        income_match = re.search(r"(?:annual family income|family income|annual income|income limit|income should not exceed)[^\d₹]{0,30}(?:rs\.?|inr|₹)?\s*([\d,]+)", text)
        if income_match:
            limit = float(income_match.group(1).replace(",", ""))
            if profile.annual_income <= limit:
                satisfied.append(f"Annual income ₹{profile.annual_income:,.0f} is within the stated ₹{limit:,.0f} limit")
            else:
                not_satisfied.append(f"Annual income ₹{profile.annual_income:,.0f} exceeds the stated ₹{limit:,.0f} limit")
        else:
            verify.append("Income limit was not reliably identified in the retrieved text.")

    if profile.state:
        if profile.state.lower() in text:
            satisfied.append(f"Your state ({profile.state}) appears in the source text.")
        else:
            verify.append("State/residency eligibility needs confirmation.")

    if not_satisfied:
        status = "Potential Mismatch"
    elif missing:
        status = "More Information Required"
    elif verify:
        status = "Possible Match"
    else:
        status = "Potential Match"

    explanation = {
        "Potential Match": "The conditions we could identify appear to match. Confirm all rules on the official portal before applying.",
        "Possible Match": "Some details appear relevant, but one or more conditions require official verification.",
        "More Information Required": "Please provide the missing profile details to improve this assessment.",
        "Potential Mismatch": "At least one identifiable condition appears not to match. Check the official rules because exceptions may apply."
    }[status]
    return EligibilityResult(
        status=status, satisfied=satisfied, not_satisfied=not_satisfied,
        missing=missing, needs_verification=verify, explanation=explanation
    )
