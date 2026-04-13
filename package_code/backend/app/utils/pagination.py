def get_pagination_args(request, default_limit=100, max_limit=200):
    try:
        limit = int(request.args.get("limit", default_limit))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return default_limit, 0
    if limit > max_limit:
        limit = max_limit
    if limit < 1:
        limit = default_limit
    if offset < 0:
        offset = 0
    return limit, offset
