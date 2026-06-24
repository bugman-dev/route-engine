def validate_capacity(locations, cabs):

    employee_count = len(locations) - 1
    total_capacity = sum(
        cab["capacity"]

        for cab in cabs
    )

    if total_capacity < employee_count:
        raise ValueError(
            f"Not enough seats. "
            f"Employees={employee_count}, "
            f"Capacity={total_capacity}"
        )