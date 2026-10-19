def get_error_count(item):
    return item[1]


def get_top_sources(error_count):
    sorted_sources = sorted(error_count.items(), key=get_error_count, reverse=True)
    return sorted_sources[:5]
