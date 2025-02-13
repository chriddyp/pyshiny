import React, {Component} from 'react';
import Dropzone from 'react-dropzone';

import {propTypes} from '../components/Upload.react';
import LoadingElement from '../utils/LoadingElement';

export default class Upload extends Component {
    constructor() {
        super();
        this.onDrop = this.onDrop.bind(this);
    }

    onDrop(files) {
        const {multiple, setProps} = this.props;
        const newProps = {
            contents: [],
            filename: [],
            last_modified: [],
        };
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = () => {
                /*
                 * I'm not sure if reader.onload will be executed in order.
                 * For example, if the 1st file is larger than the 2nd one,
                 * the 2nd file might load first.
                 */
                newProps.contents.push(reader.result);
                newProps.filename.push(file.name);
                // eslint-disable-next-line no-magic-numbers
                newProps.last_modified.push(file.lastModified / 1000);
                if (newProps.contents.length === files.length) {
                    if (multiple) {
                        setProps(newProps);
                    } else {
                        setProps({
                            contents: newProps.contents[0],
                            filename: newProps.filename[0],
                            last_modified: newProps.last_modified[0],
                        });
                    }
                }
            };
            reader.readAsDataURL(file);
        });
    }

    render() {
        const {
            id,
            children,
            accept,
            disabled,
            disable_click,
            max_size,
            min_size,
            multiple,
            className,
            className_active,
            className_reject,
            className_disabled,
            style,
            style_active,
            style_reject,
            style_disabled,
        } = this.props;
        return (
            <LoadingElement id={id}>
                <Dropzone
                    onDrop={this.onDrop}
                    accept={accept}
                    disabled={disabled}
                    disableClick={disable_click}
                    maxSize={max_size === -1 ? Infinity : max_size}
                    minSize={min_size}
                    multiple={multiple}
                    className={className}
                    activeClassName={className_active}
                    rejectClassName={className_reject}
                    disabledClassName={className_disabled}
                    style={style}
                    activeStyle={style_active}
                    rejectStyle={style_reject}
                    disabledStyle={style_disabled}
                >
                    {children}
                </Dropzone>
            </LoadingElement>
        );
    }
}

Upload.propTypes = propTypes;
