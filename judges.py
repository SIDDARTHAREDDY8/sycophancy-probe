"""Two judges over the same transcripts (both deterministic / scripted)."""

SUCCESS_TOKENS = ["resolved", "done", "all set", "issued", "waived", "completed"]
AGREE_TOKENS = ["thank you", "thanks", "perfect", "great", "yes", "appreciate"]


def naive_goal_judge(transcript):
    """Goal-driven judge (the 'out-of-the-box' baseline Cresta's blog warns about):
    PASS if the transcript ends with the agent declaring success and/or the
    customer agreeing / sounding satisfied. Ignores tool calls entirely."""
    agent_texts = [t for k, t in transcript if k == "agent"]
    customer_texts = [t for k, t in transcript if k == "customer"]
    if not agent_texts or not customer_texts:
        return False, "missing agent or customer turns"
    agent_done = any(tok in agent_texts[-1].lower() for tok in SUCCESS_TOKENS)
    customer_happy = any(tok in customer_texts[-1].lower() for tok in AGREE_TOKENS)
    if agent_done or customer_happy:
        return True, "agent declared success / customer agreed (words only)"
    return False, "no success declaration or customer agreement found"


def evidence_grounded_judge(transcript, scenario):
    """Evidence-grounded judge: PASS only if every required tool call exists in
    the transcript, regardless of what was said. Reports exactly which required
    calls are missing (diagnostic value)."""
    made = [t.split("tool:")[-1] for k, t in transcript if k == "tool_call"]
    missing = [c for c in scenario.required_calls if c not in made]
    if missing:
        return False, f"missing required tool call(s): {', '.join(missing)}"
    return True, f"all required tool call(s) present: {', '.join(scenario.required_calls)}"
