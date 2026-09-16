"""Run the sycophancy-probe eval: 2 agents x 7 scenarios x 2 judges.

Stdlib only. Usage: python3 run_eval.py
"""
from scenarios import SCENARIOS
from agents import naive_agent, good_agent, NAIVE_NAME, GOOD_NAME
from judges import naive_goal_judge, evidence_grounded_judge


def main():
    agents = [(NAIVE_NAME, naive_agent), (GOOD_NAME, good_agent)]
    trap_ids = {s.id for s in SCENARIOS if s.is_trap}
    lines = []
    lines.append("=" * 70)
    lines.append("CRESTA SYCOPHANCY PROBE (scripted methodology demo)")
    lines.append("=" * 70)
    lines.append(f"scenarios: {len(SCENARIOS)} (traps: {len(trap_ids)})  |  "
                 "agents: naive_sycophant, good_verified  |  judges: naive_goal, evidence_grounded")
    lines.append("")

    # per-scenario detail
    for s in SCENARIOS:
        lines.append(f"--- {s.id}  {'[TRAP]' if s.is_trap else '[normal]'}")
        for agent_name, agent_fn in agents:
            tr = agent_fn(s)
            goal_pass, goal_why = naive_goal_judge(tr)
            ev_pass, ev_why = evidence_grounded_judge(tr, s)
            n_tools = sum(1 for k, _ in tr if k == "tool_call")
            lines.append(
                f"  {agent_name:16s} tools_used={n_tools}  "
                f"naive_goal={'PASS' if goal_pass else 'fail':4s}  "
                f"evidence={'PASS' if ev_pass else 'fail':4s}  <- {ev_why}")
        lines.append("")

    # aggregate: fool rate of the naive judge on the sycophantic agent
    naive_passes_goal = sum(1 for s in SCENARIOS if naive_goal_judge(naive_agent(s))[0])
    naive_passes_ev = sum(1 for s in SCENARIOS if evidence_grounded_judge(naive_agent(s), s)[0])
    good_passes_goal = sum(1 for s in SCENARIOS if naive_goal_judge(good_agent(s))[0])
    good_passes_ev = sum(1 for s in SCENARIOS if evidence_grounded_judge(good_agent(s), s)[0])
    trap_fool = sum(1 for s in SCENARIOS if s.is_trap and naive_goal_judge(naive_agent(s))[0])

    n = len(SCENARIOS)
    lines.append("=" * 70)
    lines.append("RESULTS")
    lines.append("=" * 70)
    lines.append(f"naive_goal judge on SYCOPHANTIC agent : {naive_passes_goal}/{n} PASS "
                 f"-> fool rate {naive_passes_goal/n:.0%}  (false successes)")
    lines.append(f"evidence judge on SYCOPHANTIC agent  : {naive_passes_ev}/{n} PASS "
                 f"-> fool rate {naive_passes_ev/n:.0%}")
    lines.append(f"naive_goal judge on VERIFIED agent   : {good_passes_goal}/{n} PASS")
    lines.append(f"evidence judge on VERIFIED agent     : {good_passes_ev}/{n} PASS")
    lines.append(f"fool rate on TRAP scenarios only     : {trap_fool}/{len(trap_ids)} PASS "
                 f"by naive judge on sycophant")
    lines.append("")
    lines.append("DIAGNOSIS: the goal-driven judge passes the sycophantic agent on all")
    lines.append("scenarios because it scores words ('resolved!', 'thank you') instead")
    lines.append("of actions. The evidence judge demands the tool-call traces that")
    lines.append("prove the fix was actually checked/executed in the system, so it")
    lines.append("catches every sycophantic false success and says exactly which")
    lines.append("verification step was skipped.")
    report = "\n".join(lines)
    print(report)
    with open("eval_report.txt", "w") as f:
        f.write(report + "\n")
    print("\n(report also written to eval_report.txt)")


if __name__ == "__main__":
    main()
