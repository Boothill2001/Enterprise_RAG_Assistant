"""Run evaluation harness against the golden QA dataset."""

from src.eval.harness import run_evaluation


def main() -> None:
    print("=== Enterprise RAG Assistant — Evaluation ===\n")
    print("Running evaluation...\n")

    summary = run_evaluation()

    print(f"{'Metric':<30} {'Value':>10}")
    print("─" * 42)
    print(f"{'Total questions':<30} {summary.total:>10}")
    print(f"{'Passed':<30} {summary.passed:>10}")
    print(f"{'Failed':<30} {summary.failed:>10}")
    print(f"{'Pass rate':<30} {summary.pass_rate:>9.1%}")
    print(f"{'Hit rate @5 (RAG)':<30} {summary.hit_rate:>9.1%}")
    print(f"{'Citation accuracy (avg)':<30} {summary.avg_citation_accuracy:>9.1%}")
    print(f"{'Refusal accuracy (OOS)':<30} {summary.refusal_accuracy:>9.1%}")
    print(f"{'RBAC leak rate':<30} {summary.rbac_leak_rate:>9.1%}")
    print(f"{'Tool routing accuracy':<30} {summary.tool_routing_accuracy:>9.1%}")

    failed = [r for r in summary.results if not r.passed]
    if failed:
        print(f"\n--- Failed Questions ({len(failed)}) ---\n")
        for r in failed:
            print(f"  Q: {r.question}")
            print(f"  Intent: {r.intent} | Predicted: {r.predicted_intent} | Role: {r.required_role}")
            print(f"  Reason: {r.failure_reason}")
            print()

    print("=== Done ===")


if __name__ == "__main__":
    main()
