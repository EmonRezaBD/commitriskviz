import json
import re


def count_decision_points(code):
    keywords = r'\b(if|else|for|while|switch|case|catch)\b'
    operators = re.findall(r'(\&\&\|\||\?)', code)
    keyword_matches = re.findall(keywords, code)
    return len(keyword_matches) + len(operators)



def main():
    with open("data/singleFuncDataset.jsonl") as f:
        lines = f.readlines()
        entry = json.loads(lines[4]) #test entry

    # Step 3: Test it on our single entry
    before = entry["Before_commit_codebase"]
    after = entry["After_commit_codebase"]
    added = entry["Only_addition_codes"]
    deleted = entry["Only_deletion_codes"]

    cc_before = count_decision_points(before)
    cc_after = count_decision_points(after)
    cc_delta = cc_after - cc_before

    flow_added = count_decision_points(added)
    flow_deleted = count_decision_points(deleted)
    flow_score = flow_added + flow_deleted

    before_lines = len(before.split("\n")) #counting lines in the original function
    change_lines = len(added.split("\n")) + len(deleted.split("\n"))
    change_ratio = change_lines / max(before_lines, 1)

    print(f"Title: {entry['Commit title']}")
    print(f"CC Before: {cc_before}, After: {cc_after}, Delta: {cc_delta}")
    print(f"Flow Score: {flow_score} (added={flow_added}, deleted={flow_deleted})")
    print(f"Change Ratio: {change_ratio:.2f}")

if __name__ == "__main__":
    main()