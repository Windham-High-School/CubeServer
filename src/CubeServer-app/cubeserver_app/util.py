import re

import pymongo

order_re = re.compile("^order\[(?P<index>[0-9]+)\]\[(?P<name>.*)\]$")

ORDER_MAPPING = {"asc": pymongo.ASCENDING, "desc": pymongo.DESCENDING}


def parse_query(cls, cols, args, filter=None):
    # order[0][column]=0&order[0][dir]=desc&start=0&length=5
    order = [
        (int(a[0].groups()[0]), a[0].groups()[1], a[1])
        for a in [(order_re.match(x[0]), x[1]) for x in args.items()]
        if a[0]
    ]

    groups = {}
    for seq, key, val in order:
        if seq not in groups:
            groups[seq] = {}

        groups[seq][key] = val

    sorted_groups = list(groups.items())
    sorted_groups.sort(key=lambda x: x[0])

    col_keys = list(cols.keys())
    sort = []
    for _, x in sorted_groups:
        field_name, direction = col_keys[int(x["column"])], ORDER_MAPPING[x["dir"]]
        col = cols[field_name]
        if col.allow_sort is not True and col.allow_sort:
            field_name = col.allow_sort
        sort.append((field_name, direction))

    limit = int(args.get("length", 5))
    if limit == -1:
        limit = 0

    count = cls.count_documents(filter or {})
    return count, cls.find(
        filter=filter, skip=int(args.get("start", 0)), limit=limit, sort=sort
    )
