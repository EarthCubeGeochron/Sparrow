from webargs.fields import DelimitedList, Str


class NestedModelField(DelimitedList):
    """
    Field for for parsing nested model configurations
    """

    def _deserialize(self, value, attr, data, **kwargs):
        if value == "all":
            return value
        return super()._deserialize(self, value, attr, data, **kwargs)
