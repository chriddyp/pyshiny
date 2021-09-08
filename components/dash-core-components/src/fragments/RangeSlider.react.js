import React, {Component} from 'react';
import {assoc, omit, pickBy} from 'ramda';
import {Range, createSliderWithTooltip} from 'rc-slider';
import computeSliderStyle from '../utils/computeSliderStyle';

import 'rc-slider/assets/index.css';

import {propTypes, defaultProps} from '../components/RangeSlider.react';

/**
 * Truncate marks if they are out of Slider interval
 */
const truncateMarks = (min, max, marks) => pickBy(
    (k, mark) => mark >= min && mark <= max,
    marks
)

/**
 * Set marks to min and max if not defined, truncate otherwise
 */
const calcMarks = (min, max, marks) => {
    if (!marks) {
        return {[min]: min, [max]: max}
    }

    return truncateMarks(min, max, marks)
}

/**
 * Calculate default step if not defined
 */
const calcStep = (min, max, step) => {
    if (step !== undefined) {
        return step
    }

    const size = Math.abs(max - min) // interval size
    /**
     * Size multiplied by 10^i to get a nice step value at the end (0.1, 1, 10, 100, ...)
     */
    const divident = size
        .toString()
        .replace('.', '') // removes decimal point
        .replace(/^(\d*?[1-9])0+$/, "$1") // removes trailing zeros

    return size / divident
}

export default class RangeSlider extends Component {
    constructor(props) {
        super(props);
        this.DashSlider = props.tooltip
            ? createSliderWithTooltip(Range)
            : Range;
        this._computeStyle = computeSliderStyle();
        this.state = {value: props.value};
    }

    UNSAFE_componentWillReceiveProps(newProps) {
        if (newProps.tooltip !== this.props.tooltip) {
            this.DashSlider = newProps.tooltip
                ? createSliderWithTooltip(Range)
                : Range;
        }
        if (newProps.value !== this.props.value) {
            this.props.setProps({drag_value: newProps.value});
            this.setState({value: newProps.value});
        }
    }

    UNSAFE_componentWillMount() {
        if (this.props.value !== null) {
            this.props.setProps({drag_value: this.props.value});
            this.setState({value: this.props.value});
        }
    }

    render() {
        const {
            className,
            id,
            loading_state,
            setProps,
            tooltip,
            updatemode,
            vertical,
            verticalHeight,
            min,
            max,
            marks,
            step,
        } = this.props;
        const value = this.state.value;

        let tipProps;
        if (tooltip && tooltip.always_visible) {
            /**
             * clone `tooltip` but with renamed key `always_visible` -> `visible`
             * the rc-tooltip API uses `visible`, but `always_visible is more semantic
             * assigns the new (renamed) key to the old key and deletes the old key
             */
            tipProps = assoc('visible', tooltip.always_visible, tooltip);
            delete tipProps.always_visible;
        } else {
            tipProps = tooltip;
        }

        return (
            <div
                id={id}
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
                className={className}
                style={this._computeStyle(vertical, verticalHeight, tooltip)}
            >
                <this.DashSlider
                    onChange={value => {
                        if (updatemode === 'drag') {
                            setProps({value: value, drag_value: value});
                        } else {
                            this.setState({value: value});
                            setProps({drag_value: value});
                        }
                    }}
                    onAfterChange={value => {
                        if (updatemode === 'mouseup') {
                            setProps({value});
                        }
                    }}
                    /*
                    if/when rc-slider or rc-tooltip are updated to latest versions,
                    we will need to revisit this code as the getTooltipContainer function will need to be a prop instead of a nested property
                    */
                    tipProps={{
                        ...tipProps,
                        getTooltipContainer: node => node,
                    }}
                    style={{position: 'relative'}}
                    value={value}
                    marks={calcMarks(min, max, marks)}
                    step={calcStep(min, max, step)}
                    {...omit(
                        [
                            'className',
                            'value',
                            'drag_value',
                            'setProps',
                            'marks',
                            'updatemode',
                            'verticalHeight',
                            'step',
                        ],
                        this.props
                    )}
                />
            </div>
        );
    }
}

RangeSlider.propTypes = propTypes;
RangeSlider.defaultProps = defaultProps;
