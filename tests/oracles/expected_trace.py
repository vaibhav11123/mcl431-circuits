"""SequenceBench expected rows. Independent of the implementation under test."""


def expected_trace(actions: list[str], cylinders: list[str]) -> list[dict[str, int]]:
    state = {cid: 0 for cid in cylinders}
    rows = [dict(state)]
    for act in actions:
        if act.endswith("+") or act.endswith("_ON"):
            cid = act[:-1] if act.endswith("+") else act[:-3]
            if cid in state:
                state[cid] = 1
        elif act.endswith("-") or act.endswith("_OFF"):
            cid = act[:-1] if act.endswith("-") else act[:-4]
            if cid in state:
                state[cid] = 0
        rows.append(dict(state))
    return rows
