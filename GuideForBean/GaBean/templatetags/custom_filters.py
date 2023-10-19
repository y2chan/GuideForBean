from django import template

register = template.Library()

@register.filter(name='filter_stNm')
def filter_stNm(data_list):
    seen = set()
    result = []
    for data in data_list:
        stNm = data.get('stNm')  # 딕셔너리에서 'stNm' 키에 해당하는 값을 가져옵니다.
        if stNm is not None and stNm not in seen:
            result.append(data)
            seen.add(stNm)
    return result

@register.filter
def abs_filter(value):
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return value
