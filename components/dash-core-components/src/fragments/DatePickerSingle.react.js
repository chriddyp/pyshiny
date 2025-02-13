import 'react-dates/initialize';

import {SingleDatePicker} from 'react-dates';
import moment from 'moment';
import React, {Component} from 'react';

import {propTypes} from '../components/DatePickerSingle.react';
import convertToMoment from '../utils/convertToMoment';
import LoadingElement from '../utils/LoadingElement';

export default class DatePickerSingle extends Component {
    constructor() {
        super();
        this.propsToState = this.propsToState.bind(this);
        this.isOutsideRange = this.isOutsideRange.bind(this);
        this.onDateChange = this.onDateChange.bind(this);
        this.state = {focused: false};
    }

    propsToState(newProps, force = false) {
        const state = {};

        if (
            force ||
            newProps.max_date_allowed !== this.props.max_date_allowed
        ) {
            state.max_date_allowed = convertToMoment(newProps, [
                'max_date_allowed',
            ]).max_date_allowed;
        }

        if (
            force ||
            newProps.min_date_allowed !== this.props.min_date_allowed
        ) {
            state.min_date_allowed = convertToMoment(newProps, [
                'min_date_allowed',
            ]).min_date_allowed;
        }

        if (force || newProps.disabled_days !== this.props.disabled_days) {
            state.disabled_days = convertToMoment(newProps, [
                'disabled_days',
            ]).disabled_days;
        }

        if (Object.keys(state).length) {
            this.setState(state);
        }
    }

    UNSAFE_componentWillReceiveProps(newProps) {
        this.propsToState(newProps);
    }

    UNSAFE_componentWillMount() {
        this.propsToState(this.props, true);
    }

    isOutsideRange(date) {
        return (
            (this.state.min_date_allowed &&
                date.isBefore(this.state.min_date_allowed)) ||
            (this.state.max_date_allowed &&
                date.isAfter(this.state.max_date_allowed)) ||
            (this.state.disabled_days &&
                this.state.disabled_days.some(d => date.isSame(d, 'day')))
        );
    }

    onDateChange(date) {
        const {setProps} = this.props;
        const payload = {date: date ? date.format('YYYY-MM-DD') : null};
        setProps(payload);
    }

    render() {
        const {focused} = this.state;

        const {
            calendar_orientation,
            clearable,
            day_size,
            disabled,
            display_format,
            first_day_of_week,
            is_RTL,
            month_format,
            number_of_months_shown,
            placeholder,
            reopen_calendar_on_clear,
            show_outside_days,
            stay_open_on_select,
            with_full_screen_portal,
            with_portal,
            id,
            style,
            className,
        } = this.props;

        const {date, initial_visible_month} = convertToMoment(this.props, [
            'date',
            'initial_visible_month',
        ]);

        const verticalFlag = calendar_orientation !== 'vertical';

        const DatePickerWrapperStyles = {
            position: 'relative',
            display: 'inline-block',
            ...style,
        };

        // the height in px of the top part of the calendar (that holds
        // the name of the month)
        const baselineHeight = 145;

        return (
            <LoadingElement
                id={id}
                style={DatePickerWrapperStyles}
                className={className}
            >
                <SingleDatePicker
                    date={date}
                    onDateChange={this.onDateChange}
                    focused={focused}
                    onFocusChange={({focused}) => this.setState({focused})}
                    initialVisibleMonth={() =>
                        date || initial_visible_month || moment()
                    }
                    isOutsideRange={this.isOutsideRange}
                    numberOfMonths={number_of_months_shown}
                    withPortal={with_portal && verticalFlag}
                    withFullScreenPortal={
                        with_full_screen_portal && verticalFlag
                    }
                    firstDayOfWeek={first_day_of_week}
                    enableOutsideDays={show_outside_days}
                    monthFormat={month_format}
                    displayFormat={display_format}
                    placeholder={placeholder}
                    showClearDate={clearable}
                    disabled={disabled}
                    keepOpenOnDateSelect={stay_open_on_select}
                    reopenPickerOnClearDate={reopen_calendar_on_clear}
                    isRTL={is_RTL}
                    orientation={calendar_orientation}
                    daySize={day_size}
                    verticalHeight={baselineHeight + day_size * 6 + 'px'}
                />
            </LoadingElement>
        );
    }
}

DatePickerSingle.propTypes = propTypes;
