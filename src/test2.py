def format_time(t):
    unit="s"
    units=["m", "h", "d"]
    mults=[60, 60, 24]

    for i in range(len(units)):
        print(i, t, units[i], mults[i])
        if t>=mults[i]:
            t/=mults[i]
            unit=units[i]
        else:
            break
    return f"{t:.2f}{unit}"

t=5032.883882522583
t2=format_time(t)
print(t2)