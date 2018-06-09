from flask import session, request


def get_id():
    if session.get("user_id"):
        user_id = session["user_id"]
    else:
        number = request.form.get("number")
        user_id = number
    return user_id


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


class Page(object):
    def __init__(self, item_count, page=1, page_size=10):
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count // page_size + (
            1 if item_count % page_size > 0 else 0
        )
        if (item_count == 0) or (page > self.page_count):
            self.offset = 0
            self.limit = 0
            self.page = 1
        else:
            self.page = page
            self.offset = self.page_size * (page - 1)
            self.limit = self.page_size * page
        self.page_list = range(1, self.page_count + 1)
        self.has_next = self.page < self.page_count
        self.has_prev = self.page > 1

    def __str__(self):
        return (
            "item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s"
            % (
                self.item_count,
                self.page_count,
                self.page_index,
                self.page_size,
                self.offset,
                self.limit,
            )
        )

    __repr__ = __str__
