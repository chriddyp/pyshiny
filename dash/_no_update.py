class NoUpdate:
    def to_plotly_json(self):  # pylint: disable=no-self-use
        return {"_dash_no_update": "_dash_no_update"}

    @staticmethod
    def is_no_update(obj):
        return isinstance(obj, NoUpdate) or (
            isinstance(obj, dict) and obj == {"_dash_no_update": "_dash_no_update"}
        )
