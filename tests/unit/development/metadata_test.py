# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.development.base_component import ComponentType # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Table(Component):
    """A Table component.
This is a description of the component.
It's multiple lines long.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- id (string; optional)

- aria-* (string; optional)

- customArrayProp (list; optional)

- customProp (optional)

- data-* (string; optional)

- in (string; optional)

- optionalAny (boolean | number | string | dict | list; optional)

- optionalArray (list; optional):
    Description of optionalArray.

- optionalArrayOf (list of numbers; optional)

- optionalBool (boolean; optional)

- optionalElement (dash component; optional)

- optionalEnum (a value equal to: 'News', 'Photos'; optional)

- optionalNode (a list of or a singular dash component, string or number; optional)

- optionalNumber (number; default 42)

- optionalObject (dict; optional)

- optionalObjectOf (dict with strings as keys and values of type number; optional)

- optionalObjectWithExactAndNestedDescription (dict; optional)

    `optionalObjectWithExactAndNestedDescription` is a dict with keys:

    - color (string; optional)

    - fontSize (number; optional)

    - figure (dict; optional):
        Figure is a plotly graph object.

        `figure` is a dict with keys:

        - data (list of dicts; optional):
            data is a collection of traces.

        - layout (dict; optional):
            layout describes the rest of the figure.

- optionalObjectWithShapeAndNestedDescription (dict; optional)

    `optionalObjectWithShapeAndNestedDescription` is a dict with keys:

    - color (string; optional)

    - fontSize (number; optional)

    - figure (dict; optional):
        Figure is a plotly graph object.

        `figure` is a dict with keys:

        - data (list of dicts; optional):
            data is a collection of traces.

        - layout (dict; optional):
            layout describes the rest of the figure.

- optionalString (string; default 'hello world')

- optionalUnion (string | number; optional)"""
    _children_props = ['optionalNode', 'optionalElement']
    _base_nodes = ['optionalNode', 'optionalElement', 'children']
    _namespace = 'TableComponents'
    _type = 'Table'
    OptionalObjectWithExactAndNestedDescriptionFigure = TypedDict(
        "OptionalObjectWithExactAndNestedDescriptionFigure",
            {
            "data": NotRequired[typing.Sequence[dict]],
            "layout": NotRequired[dict]
        }
    )

    OptionalObjectWithExactAndNestedDescription = TypedDict(
        "OptionalObjectWithExactAndNestedDescription",
            {
            "color": NotRequired[str],
            "fontSize": NotRequired[typing.Union[int, float, numbers.Number]],
            "figure": NotRequired["OptionalObjectWithExactAndNestedDescriptionFigure"]
        }
    )

    OptionalObjectWithShapeAndNestedDescriptionFigure = TypedDict(
        "OptionalObjectWithShapeAndNestedDescriptionFigure",
            {
            "data": NotRequired[typing.Sequence[dict]],
            "layout": NotRequired[dict]
        }
    )

    OptionalObjectWithShapeAndNestedDescription = TypedDict(
        "OptionalObjectWithShapeAndNestedDescription",
            {
            "color": NotRequired[str],
            "fontSize": NotRequired[typing.Union[int, float, numbers.Number]],
            "figure": NotRequired["OptionalObjectWithShapeAndNestedDescriptionFigure"]
        }
    )

    @_explicitize_args
    def __init__(
        self,
        children: typing.Optional[typing.Union[str, int, float, ComponentType, typing.Sequence[typing.Union[str, int, float, ComponentType]]]] = None,
        optionalArray: typing.Optional[typing.Sequence] = None,
        optionalBool: typing.Optional[bool] = None,
        optionalFunc: typing.Optional[typing.Any] = None,
        optionalNumber: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        optionalObject: typing.Optional[dict] = None,
        optionalString: typing.Optional[str] = None,
        optionalSymbol: typing.Optional[typing.Any] = None,
        optionalNode: typing.Optional[typing.Union[str, int, float, ComponentType, typing.Sequence[typing.Union[str, int, float, ComponentType]]]] = None,
        optionalElement: typing.Optional[ComponentType] = None,
        optionalMessage: typing.Optional[typing.Any] = None,
        optionalEnum: typing.Optional[Literal["News", "Photos"]] = None,
        optionalUnion: typing.Optional[typing.Union[str, typing.Union[int, float, numbers.Number], typing.Any]] = None,
        optionalArrayOf: typing.Optional[typing.Sequence[typing.Union[int, float, numbers.Number]]] = None,
        optionalObjectOf: typing.Optional[typing.Dict[typing.Union[str, float, int], typing.Union[int, float, numbers.Number]]] = None,
        optionalObjectWithExactAndNestedDescription: typing.Optional["OptionalObjectWithExactAndNestedDescription"] = None,
        optionalObjectWithShapeAndNestedDescription: typing.Optional["OptionalObjectWithShapeAndNestedDescription"] = None,
        optionalAny: typing.Optional[typing.Any] = None,
        customProp: typing.Optional[typing.Any] = None,
        customArrayProp: typing.Optional[typing.Sequence[typing.Any]] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'aria-*', 'customArrayProp', 'customProp', 'data-*', 'in', 'optionalAny', 'optionalArray', 'optionalArrayOf', 'optionalBool', 'optionalElement', 'optionalEnum', 'optionalNode', 'optionalNumber', 'optionalObject', 'optionalObjectOf', 'optionalObjectWithExactAndNestedDescription', 'optionalObjectWithShapeAndNestedDescription', 'optionalString', 'optionalUnion']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'aria-*', 'customArrayProp', 'customProp', 'data-*', 'in', 'optionalAny', 'optionalArray', 'optionalArrayOf', 'optionalBool', 'optionalElement', 'optionalEnum', 'optionalNode', 'optionalNumber', 'optionalObject', 'optionalObjectOf', 'optionalObjectWithExactAndNestedDescription', 'optionalObjectWithShapeAndNestedDescription', 'optionalString', 'optionalUnion']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Table, self).__init__(children=children, **args)
