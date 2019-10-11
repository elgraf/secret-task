from copy import deepcopy


def chart_slice(chart1, chart2):
    if len(chart1) < len(chart2):
        chart1, chart2 = chart2, chart1
    result = deepcopy(chart1)
    rc_modif = reversed(chart2)
    c_cur = next(rc_modif)
    for point in reversed(result):
        if point["date"] >= c_cur["date"]:
            point["m"] += c_cur["m"]
        else:
            c_cur = next(rc_modif, None)
            if c_cur is None:
                break
    ic_modif = iter(chart2)
    c_cur = next(ic_modif)
    for i, point in enumerate(result):
        if point["date"] == c_cur["date"]:
            c_cur = next(ic_modif, None)
            if c_cur is None:
                break
            continue
        elif point["date"] > c_cur["date"]:
            if i:
                c_cur["m"] += result[i-1]["m"]
            result.insert(i, c_cur)
            c_cur = next(ic_modif, None)
            if c_cur is None:
                break
    return result
