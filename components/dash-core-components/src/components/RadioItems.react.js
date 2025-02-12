/**
 * added support for title in option to provide tooltips 
 * and ensured compatibility with radioItems and checklist
 * and maintained structure 
 */
/**
 * here updated the RadioItems.js
 */
import PropTypes from 'prop-types';
import React, {Component} from 'react';
import './css/react-select@1.0.0-rc.3.min.css';
import {sanitizeOptions} from '../utils/optionTypes';

/**
 * RadioItems is a component that encapsulates several radio item inputs.
 * The values and labels of the RadioItems are specified in the `options`
 * property, and the selected item is specified with the `value` property.
 * Each radio item is rendered as an input with a surrounding label.
 */

export default class RadioItems extends Component {
    render() {
        const {
            id,
            className,
            style,
            inputClassName,
            inputStyle,
            labelClassName,
            labelStyle,
            options,
            setProps,
            loading_state,
            value,
            inline,
        } = this.props;

        let ids = {};
        if (id) {
            ids = {id, key: id};
        }
        return (
            <div
                data-dash-is-loading={
                    (loading_state && loading_state.is_loading) || undefined
                }
                {...ids}
                className={className}
                style={style}
            >
                {sanitizeOptions(options).map(option => (
                    <label
                        title={option.title || ''}
                        style={{
                            display: inline ? 'inline-block' : 'block',
                            ...labelStyle,
                        }}
                        className={labelClassName}
                        key={option.value}
                    >
                        <input
                            checked={option.value === value}
                            className={inputClassName}
                            disabled={Boolean(option.disabled)}
                            style={inputStyle}
                            type="radio"
                            onChange={() => {
                                setProps({value: option.value});
                            }}
                        />
                        {option.label}
                    </label>
                ))}
            </div>
        );
    }
}

RadioItems.propTypes = {
    /**
     * An array of options, or inline dictionary of options
     */
    options: PropTypes.oneOfType([
        PropTypes.object,
        PropTypes.arrayOf(
            PropTypes.exact({
                label: PropTypes.node.isRequired,
                value: PropTypes.oneOfType([
                    PropTypes.string,
                    PropTypes.number,
                    PropTypes.bool,
                ]).isRequired,
                disabled: PropTypes.bool,
                title: PropTypes.string, // Added title prop for tooltips
            })
        ),
    ]),

    value: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
        PropTypes.bool,
    ]),

    inline: PropTypes.bool,
    style: PropTypes.object,
    className: PropTypes.string,
    inputStyle: PropTypes.object,
    inputClassName: PropTypes.string,
    labelStyle: PropTypes.object,
    labelClassName: PropTypes.string,
    id: PropTypes.string,
    setProps: PropTypes.func,

    loading_state: PropTypes.shape({
        is_loading: PropTypes.bool,
        prop_name: PropTypes.string,
        component_name: PropTypes.string,
    }),

    persistence: PropTypes.oneOfType([
        PropTypes.bool,
        PropTypes.string,
        PropTypes.number,
    ]),

    persisted_props: PropTypes.arrayOf(PropTypes.oneOf(['value'])),
    persistence_type: PropTypes.oneOf(['local', 'session', 'memory']),
};

RadioItems.defaultProps = {
    inputStyle: {},
    inputClassName: '',
    labelStyle: {},
    labelClassName: '',
    options: [],
    persisted_props: ['value'],
    persistence_type: 'local',
    inline: false,
};

/**
 * added title attribute to the <lable> enabling tooltips when hovering 
 * over radio items and updated proptypes to include title in options 
 * ensuring proper validation and also maintained backward compatibility with 
 * dash application
 */