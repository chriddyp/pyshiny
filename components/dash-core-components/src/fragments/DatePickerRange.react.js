import 'react-dates/initialize';
import {DateRangePicker} from 'react-dates';
import React, {Component} from 'react';
import uniqid from 'uniqid';

import {propTypes} from '../components/DatePickerRange.react';
import convertToMoment from '../utils/convertToMoment';
import LoadingElement from '../utils/LoadingElement';

export default class DatePickerRange extends Component {
    constructor(props) {
        super(props);
        this.propsToState = this.propsToState.bind(this);
        this.onDatesChange = this.onDatesChange.bind(this);
        this.isOutsideRange = this.isOutsideRange.bind(this);
        this.state = {
            focused: false,
            start_date_id: props.start_date_id || uniqid(),
            end_date_id: props.end_date_id || uniqid(),
        };
    }

    propsToState(newProps, force = false) {
        const state = {};

        if (force || newProps.start_date !== this.props.start_date) {
            state.start_date = newProps.start_date;
        }

        if (force || newProps.end_date !== this.props.end_date) {
            state.end_date = newProps.end_date;
        }

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

    onDatesChange({startDate: start_date, endDate: end_date}) {
        const {setProps, updatemode, clearable} = this.props;

        const oldMomentDates = convertToMoment(this.state, [
            'start_date',
            'end_date',
        ]);

        if (start_date && !start_date.isSame(oldMomentDates.start_date)) {
            if (updatemode === 'singledate') {
                setProps({start_date: start_date.format('YYYY-MM-DD')});
            } else {
                this.setState({start_date: start_date.format('YYYY-MM-DD')});
            }
        }

        if (end_date && !end_date.isSame(oldMomentDates.end_date)) {
            if (updatemode === 'singledate') {
                setProps({end_date: end_date.format('YYYY-MM-DD')});
            } else if (updatemode === 'bothdates') {
                setProps({
                    start_date: this.state.start_date,
                    end_date: end_date.format('YYYY-MM-DD'),
                });
            }
        }

        if (
            clearable &&
            !start_date &&
            !end_date &&
            (oldMomentDates.start_date !== start_date ||
                oldMomentDates.end_date !== end_date)
        ) {
            setProps({start_date: null, end_date: null});
        }
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

    render() {
        const {focusedInput} = this.state;

        const {
            calendar_orientation,
            clearable,
            day_size,
            disabled,
            display_format,
            end_date_placeholder_text,
            first_day_of_week,
            is_RTL,
            minimum_nights,
            month_format,
            number_of_months_shown,
            reopen_calendar_on_clear,
            show_outside_days,
            start_date_placeholder_text,
            stay_open_on_select,
            with_full_screen_portal,
            with_portal,
            id,
            style,
            className,
            start_date_id,
            end_date_id,
        } = this.props;

        const {initial_visible_month} = convertToMoment(this.props, [
            'initial_visible_month',
        ]);

        const {start_date, end_date} = convertToMoment(this.state, [
            'start_date',
            'end_date',
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
                <DateRangePicker
                    daySize={day_size}
                    disabled={disabled}
                    displayFormat={display_format}
                    enableOutsideDays={show_outside_days}
                    endDate={end_date}
                    endDatePlaceholderText={end_date_placeholder_text}
                    firstDayOfWeek={first_day_of_week}
                    focusedInput={focusedInput}
                    initialVisibleMonth={() => {
                        if (initial_visible_month) {
                            return initial_visible_month;
                        } else if (end_date && focusedInput === 'endDate') {
                            return end_date;
                        } else if (start_date && focusedInput === 'startDate') {
                            return start_date;
                        }
                        return start_date;
                    }}
                    isOutsideRange={this.isOutsideRange}
                    isRTL={is_RTL}
                    keepOpenOnDateSelect={stay_open_on_select}
                    minimumNights={minimum_nights}
                    monthFormat={month_format}
                    numberOfMonths={number_of_months_shown}
                    onDatesChange={this.onDatesChange}
                    onFocusChange={focusedInput =>
                        this.setState({focusedInput})
                    }
                    orientation={calendar_orientation}
                    reopenPickerOnClearDates={reopen_calendar_on_clear}
                    showClearDates={clearable}
                    startDate={start_date}
                    startDatePlaceholderText={start_date_placeholder_text}
                    withFullScreenPortal={
                        with_full_screen_portal && verticalFlag
                    }
                    withPortal={with_portal && verticalFlag}
                    startDateId={start_date_id || this.state.start_date_id}
                    endDateId={end_date_id || this.state.end_date_id}
                    verticalHeight={baselineHeight + day_size * 6 + 'px'}
                />
            </LoadingElement>
        );
    }
}

DatePickerRange.propTypes = propTypes;
