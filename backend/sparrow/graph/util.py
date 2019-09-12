from inflection import camelize as __camelize

def camelize(s):
    return __camelize(s, False)
