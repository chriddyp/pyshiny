import lazyLoadMathJax from '../utils/LazyLoader/mathjax';
import React, {Component} from 'react';
// /build/withPolyfill for IE11 support - https://github.com/maslianok/react-resize-detector/issues/144
import ResizeDetector from 'react-resize-detector/build/withPolyfill';
import {
    equals,
    filter,
    has,
    includes,
    isNil,
    mergeDeepRight,
    omit,
    type,
} from 'ramda';
import PropTypes from 'prop-types';
import {graphPropTypes, graphDefaultProps} from '../components/Graph.react';
/* global Plotly:true */

/**
 * `autosize: true` causes Plotly.js to conform to the parent element size.
 * This is necessary for `dcc.Graph` call to `Plotly.Plots.resize(target)` to do something.
 *
 * Users can override this value for specific use-cases by explicitly passing `autoresize: true`
 * if `responsive` is not set to True.
 */
const RESPONSIVE_LAYOUT = {
    autosize: true,
    height: undefined,
    width: undefined,
};

const AUTO_LAYOUT = {};

const UNRESPONSIVE_LAYOUT = {
    autosize: false,
};

/**
 * `responsive: true` causes Plotly.js to resize the graph on `window.resize`.
 * This is necessary for `dcc.Graph` call to `Plotly.Plots.resize(target)` to do something.
 *
 * Users can override this value for specific use-cases by explicitly passing `responsive: false`
 * if `responsive` is not set to True.
 */
const RESPONSIVE_CONFIG = {
    responsive: true,
};

const AUTO_CONFIG = {};

const UNRESPONSIVE_CONFIG = {
    responsive: false,
};

const filterEventData = (gd, eventData, event) => {
    let filteredEventData;
    if (includes(event, ['click', 'hover', 'selected'])) {
        const points = [];

        if (isNil(eventData)) {
            return null;
        }

        /*
         * remove `data`, `layout`, `xaxis`, etc
         * objects from the event data since they're so big
         * and cause JSON stringify ciricular structure errors.
         *
         * also, pull down the `customdata` point from the data array
         * into the event object
         */
        const data = gd.data;

        for (let i = 0; i < eventData.points.length; i++) {
            const fullPoint = eventData.points[i];
            const pointData = filter(function (o) {
                return !includes(type(o), ['Object', 'Array']);
            }, fullPoint);

            // permit a bounding box to pass through, if present
            if (has('bbox', fullPoint)) {
                pointData.bbox = fullPoint.bbox;
            }

            if (
                has('curveNumber', fullPoint) &&
                has('customdata', data[pointData.curveNumber])
            ) {
                if (has('pointNumber', fullPoint)) {
                    if (typeof fullPoint.pointNumber === 'number') {
                        pointData.customdata =
                            data[pointData.curveNumber].customdata[
                                fullPoint.pointNumber
                            ];
                    } else if (
                        !fullPoint.pointNumber &&
                        fullPoint.data.mode.includes('lines')
                    ) {
                        pointData.customdata =
                            data[pointData.curveNumber].customdata;
                    }
                } else if (has('pointNumbers', fullPoint)) {
                    pointData.customdata = fullPoint.pointNumbers.map(function (
                        point
                    ) {
                        return data[pointData.curveNumber].customdata[point];
                    });
                }
            }

            // specific to histogram. see https://github.com/plotly/plotly.js/pull/2113/
            if (has('pointNumbers', fullPoint)) {
                pointData.pointNumbers = fullPoint.pointNumbers;
            }

            points[i] = pointData;
        }
        filteredEventData = {points};
    } else if (event === 'relayout' || event === 'restyle') {
        /*
         * relayout shouldn't include any big objects
         * it will usually just contain the ranges of the axes like
         * "xaxis.range[0]": 0.7715822247381828,
         * "xaxis.range[1]": 3.0095292008680063`
         */
        filteredEventData = eventData;
    }
    if (has('range', eventData)) {
        filteredEventData.range = eventData.range;
    }
    if (has('lassoPoints', eventData)) {
        filteredEventData.lassoPoints = eventData.lassoPoints;
    }
    return filteredEventData;
};

/**
 * Graph can be used to render any plotly.js-powered data visualization.
 *
 * You can define callbacks based on user interaction with Graphs such as
 * hovering, clicking or selecting
 */
class PlotlyGraph extends Component {
    constructor(props) {
        super(props);
        this.gd = React.createRef();
        this._hasPlotted = false;
        this._prevGd = null;
        this._queue = Promise.resolve();

        this.bindEvents = this.bindEvents.bind(this);
        this.getConfig = this.getConfig.bind(this);
        this.getConfigOverride = this.getConfigOverride.bind(this);
        this.getLayout = this.getLayout.bind(this);
        this.getLayoutOverride = this.getLayoutOverride.bind(this);
        this.graphResize = this.graphResize.bind(this);
        this.isResponsive = this.isResponsive.bind(this);
        this.amendTraces = this.amendTraces.bind(this);

        this.state = {override: {}, originals: {}};
    }

    plot(props) {
        let {figure, config} = props;
        const {animate, animation_options, responsive, mathjax} = props;

        const gd = this.gd.current;
        figure = props._dashprivate_transformFigure(figure, gd);
        config = props._dashprivate_transformConfig(config, gd);

        const configClone = this.getConfig(config, responsive);
        // add typesetMath | not exposed to the dash API
        configClone.typesetMath = mathjax;

        const figureClone = {
            data: figure?.data,
            layout: this.getLayout(figure?.layout, responsive),
            frames: figure?.frames,
            config: configClone,
        };

        if (
            animate &&
            this._hasPlotted &&
            figure.data.length === gd.data.length
        ) {
            // in case we've have figure frames,
            // we need to recreate frames before animation
            if (figure.frames) {
                return Plotly.deleteFrames(gd)
                    .then(() => Plotly.addFrames(gd, figure.frames))
                    .then(() =>
                        Plotly.animate(gd, figureClone, animation_options)
                    );
            }
            return Plotly.animate(gd, figureClone, animation_options);
        }

        gd.classList.add('dash-graph--pending');

        return lazyLoadMathJax(mathjax)
            .then(() => {
                const gd = this.gd.current;
                return gd && Plotly.react(gd, figureClone);
            })
            .then(() => {
                const gd = this.gd.current;

                // double-check gd hasn't been unmounted
                if (!gd) {
                    return;
                }

                gd.classList.remove('dash-graph--pending');

                // in case we've made a new DOM element, transfer events
                if (this._hasPlotted && gd !== this._prevGd) {
                    if (this._prevGd && this._prevGd.removeAllListeners) {
                        this._prevGd.removeAllListeners();
                        Plotly.purge(this._prevGd);
                    }
                    this._hasPlotted = false;
                }

                if (!this._hasPlotted) {
                    this.bindEvents();
                    this.graphResize(true);
                    this._hasPlotted = true;
                    this._prevGd = gd;
                }
            });
    }

    amendTraces(p, oldProps, newProps) {
        const {prependData: oldPrepend, extendData: oldExtend} = oldProps;
        const {prependData: newPrepend, extendData: newExtend} = newProps;
        const _this = this;

        function mergeTraces(props, dataKey, plotlyFnKey) {
            const clearState = props.clearState;
            const dataArray = props[dataKey];

            let _p = Promise.resolve();

            dataArray.forEach(data => {
                let updateData, traceIndices, maxPoints;
                if (Array.isArray(data) && typeof data[0] === 'object') {
                    [updateData, traceIndices, maxPoints] = data;
                } else {
                    updateData = data;
                }

                if (!traceIndices) {
                    function getFirstProp(data) {
                        return data[Object.keys(data)[0]];
                    }

                    function generateIndices(data) {
                        return Array.from(
                            Array(getFirstProp(data).length).keys()
                        );
                    }
                    traceIndices = generateIndices(updateData);
                }

                _p = _p.then(() => {
                    const gd = _this.gd.current;
                    return (
                        gd &&
                        Plotly[plotlyFnKey](
                            gd,
                            updateData,
                            traceIndices,
                            maxPoints
                        )
                    );
                });
            });

            return _p.then(() => clearState(dataKey));
        }

        let modified = false;

        if (newPrepend?.length && oldPrepend !== newPrepend) {
            modified = true;
            p = p.then(() =>
                mergeTraces(newProps, 'prependData', 'prependTraces')
            );
        }

        if (newExtend?.length && oldExtend !== newExtend) {
            modified = true;
            p = p.then(() =>
                mergeTraces(newProps, 'extendData', 'extendTraces')
            );
        }

        if (modified) {
            p = p.then(() =>
                newProps._dashprivate_onFigureModified(newProps.figure)
            );
        }

        return p;
    }

    getConfig(config, responsive) {
        return mergeDeepRight(config, this.getConfigOverride(responsive));
    }

    getLayout(layout, responsive) {
        if (!layout) {
            return layout;
        }
        const override = this.getLayoutOverride(responsive);
        const {override: prev_override, originals: prev_originals} = this.state;
        // Store the original data that we're about to override
        const originals = {};
        for (const key in override) {
            if (layout[key] !== prev_override[key]) {
                originals[key] = layout[key];
            } else if (prev_originals.hasOwnProperty(key)) {
                originals[key] = prev_originals[key];
            }
        }
        this.setState({override, originals});
        // Undo the previous override, but only for keys that the user did not change
        for (const key in prev_originals) {
            if (layout[key] === prev_override[key]) {
                layout[key] = prev_originals[key];
            }
        }
        // Apply the current override
        for (const key in override) {
            layout[key] = override[key];
        }
        return layout; // not really a clone
    }

    getConfigOverride(responsive) {
        switch (responsive) {
            case false:
                return UNRESPONSIVE_CONFIG;
            case true:
                return RESPONSIVE_CONFIG;
            default:
                return AUTO_CONFIG;
        }
    }

    getLayoutOverride(responsive) {
        switch (responsive) {
            case false:
                return UNRESPONSIVE_LAYOUT;
            case true:
                return RESPONSIVE_LAYOUT;
            default:
                return AUTO_LAYOUT;
        }
    }

    isResponsive(props) {
        const {config, figure, responsive} = props;

        if (type(responsive) === 'Boolean') {
            return responsive;
        }

        return Boolean(
            config.responsive &&
                (!figure.layout ||
                    ((figure.layout.autosize ||
                        isNil(figure.layout.autosize)) &&
                        (isNil(figure.layout.height) ||
                            isNil(figure.layout.width))))
        );
    }

    graphResize(force = false) {
        if (!force && !this.isResponsive(this.props)) {
            return;
        }

        const gd = this.gd.current;
        if (!gd) {
            return;
        }

        gd.classList.add('dash-graph--pending');

        Plotly.Plots.resize(gd)
            .catch(() => {})
            .finally(() => gd.classList.remove('dash-graph--pending'));
    }

    bindEvents() {
        const {
            setProps,
            clear_on_unhover,
            relayoutData,
            restyleData,
            hoverData,
            selectedData,
        } = this.props;

        const gd = this.gd.current;

        gd.on('plotly_click', eventData => {
            const clickData = filterEventData(gd, eventData, 'click');
            if (!isNil(clickData)) {
                setProps({clickData});
            }
        });
        gd.on('plotly_clickannotation', eventData => {
            const clickAnnotationData = omit(
                ['event', 'fullAnnotation'],
                eventData
            );
            setProps({clickAnnotationData});
        });
        gd.on('plotly_hover', eventData => {
            const hover = filterEventData(gd, eventData, 'hover');
            if (!isNil(hover) && !equals(hover, hoverData)) {
                setProps({hoverData: hover});
            }
        });
        gd.on('plotly_selected', eventData => {
            const selected = filterEventData(gd, eventData, 'selected');
            if (!isNil(selected) && !equals(selected, selectedData)) {
                setProps({selectedData: selected});
            }
        });
        gd.on('plotly_deselect', () => {
            setProps({selectedData: null});
        });
        gd.on('plotly_relayout', eventData => {
            const relayout = filterEventData(gd, eventData, 'relayout');
            if (!isNil(relayout) && !equals(relayout, relayoutData)) {
                setProps({relayoutData: relayout});
            }
        });
        gd.on('plotly_restyle', eventData => {
            const restyle = filterEventData(gd, eventData, 'restyle');
            if (!isNil(restyle) && !equals(restyle, restyleData)) {
                setProps({restyleData: restyle});
            }
        });
        gd.on('plotly_unhover', () => {
            if (clear_on_unhover) {
                setProps({hoverData: null});
            }
        });
    }

    getStyle() {
        const {responsive} = this.props;
        let {style} = this.props;

        // When there is no forced responsive style, return the original style property
        if (!responsive) {
            return style;
        }

        // Otherwise, if the height is not set, we make the graph size equal to the parent one
        if (!style) {
            style = {};
        }

        if (!style.height) {
            return Object.assign({height: '100%'}, style);
        }

        return style;
    }

    componentDidMount() {
        const p = this.plot(this.props);
        this._queue = this.amendTraces(p, {}, this.props);
    }

    componentWillUnmount() {
        const gd = this.gd.current;
        if (gd && gd.removeAllListeners) {
            gd.removeAllListeners();
            if (this._hasPlotted) {
                Plotly.purge(gd);
            }
        }
    }

    shouldComponentUpdate(nextProps) {
        return (
            this.props.id !== nextProps.id ||
            JSON.stringify(this.props.style) !==
                JSON.stringify(nextProps.style) ||
            JSON.stringify(this.props.loading_state) !==
                JSON.stringify(nextProps.loading_state)
        );
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        const idChanged = this.props.id !== nextProps.id;
        if (idChanged) {
            /*
             * then the dom needs to get re-rendered with a new ID.
             * the graph will get updated in componentDidUpdate
             */
            return;
        }

        let p = this._queue;

        if (
            this.props.mathjax !== nextProps.mathjax ||
            this.props.figure !== nextProps.figure ||
            this.props._dashprivate_transformConfig !==
                nextProps._dashprivate_transformConfig ||
            this.props._dashprivate_transformFigure !==
                nextProps._dashprivate_transformFigure
        ) {
            p = p.then(() => this.plot(nextProps));
        }

        this._queue = this.amendTraces(p, this.props, nextProps);
    }

    componentDidUpdate(prevProps) {
        if (
            prevProps.id !== this.props.id ||
            prevProps.mathjax !== this.props.mathjax
        ) {
            this._queue = this._queue.then(() => this.plot(this.props));
        }
    }

    render() {
        const {className, id, loading_state} = this.props;
        const style = this.getStyle();

        return (
            <div
                id={id}
                key={id}
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
                className={className}
                style={style}
            >
                <ResizeDetector
                    handleHeight={true}
                    handleWidth={true}
                    refreshMode="debounce"
                    refreshOptions={{trailing: true}}
                    refreshRate={50}
                    onResize={this.graphResize}
                />
                <div ref={this.gd} style={{height: '100%', width: '100%'}} />
            </div>
        );
    }
}

PlotlyGraph.propTypes = {
    ...graphPropTypes,
    prependData: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.array, PropTypes.object])
    ),
    extendData: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.array, PropTypes.object])
    ),
    clearState: PropTypes.func.isRequired,
};

PlotlyGraph.defaultProps = {
    ...graphDefaultProps,
    prependData: [],
    extendData: [],
};

export default PlotlyGraph;
