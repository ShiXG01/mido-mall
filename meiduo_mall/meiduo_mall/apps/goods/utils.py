
def get_breadcrumb(category):
    """
    获取面包屑导航
    :param category:类别对象：可能是一级，二级或三级
    :return:一级：返回一级类别；二级：返回一级加二级类别；三级：返回一级加二级加三级类别
    """
    breadcrumb = {
        'cat1': '',
        'cat2': '',
        'cat3': ''
    }
    if category.parent is None:  # 一级类别
        breadcrumb['cat1'] = category
    elif category.subs.count() == 0:  # 三级类别
        breadcrumb['cat1'] = category.parent.parent
        breadcrumb['cat2'] = category.parent
        breadcrumb['cat3'] = category
    else:  # 二级类别
        breadcrumb['cat1'] = category.parent
        breadcrumb['cat2'] = category

    return breadcrumb
