from webargs.fields import DelimitedList, Str


class NestedModelField(DelimitedList):
    """
    Field for for parsing nested model configurations
    """

    def _deserialize(self, value, *args, **kwargs):
        if value == "all":
            return value
        return super()._deserialize(value, *args, **kwargs)
