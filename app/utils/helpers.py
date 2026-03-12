def parse_pagination(page, per_page, default_page=1, default_per_page=10, max_per_page=50):
    try:
        page = int(page) if page is not None else default_page
        per_page = int(per_page) if per_page is not None else default_per_page
    except (TypeError, ValueError):
        return None, None, {"error": "page et per_page doivent etre des entiers"}, 400

    if page < 1:
        return None, None, {"error": "page doit etre >= 1"}, 400
    if per_page < 1:
        return None, None, {"error": "per_page doit etre >= 1"}, 400
    if per_page > max_per_page:
        return None, None, {"error": f"per_page ne doit pas depasser {max_per_page}"}, 400

    return page, per_page, None, None


def paginate_list(items, page, per_page):
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = items[start:end]

    return {
        "items": paginated_items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    }
