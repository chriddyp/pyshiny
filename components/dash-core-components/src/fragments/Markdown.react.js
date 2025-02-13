import React, {Component} from 'react';
import {mergeDeepRight, pick, type} from 'ramda';
import JsxParser from 'react-jsx-parser';
import Markdown from 'react-markdown';
import RemarkMath from 'remark-math';

import Math from './Math.react';
import MarkdownHighlighter from '../utils/MarkdownHighlighter';
import {propTypes} from '../components/Markdown.react';

import DccLink from './../components/Link.react';
import LoadingElement from '../utils/LoadingElement';

export default class DashMarkdown extends Component {
    constructor(props) {
        super(props);

        if (MarkdownHighlighter.isReady !== true) {
            MarkdownHighlighter.isReady.then(() => {
                this.setState({});
            });
        }
        this.highlightCode = this.highlightCode.bind(this);
        this.dedent = this.dedent.bind(this);
    }

    componentDidMount() {
        this.highlightCode();
    }

    componentDidUpdate() {
        this.highlightCode();
    }

    highlightCode() {
        const isHighlighted = node => {
            // a highlighted node will have <span> children which are what color the text
            return node.children.length > 0;
        };

        if (this.mdContainer) {
            const nodes = this.mdContainer.querySelectorAll('pre code');

            if (MarkdownHighlighter.hljs) {
                for (let i = 0; i < nodes.length; i++) {
                    if (!isHighlighted(nodes[i])) {
                        nodes[i].removeAttribute('data-highlighted');
                        MarkdownHighlighter.hljs.highlightElement(nodes[i]);
                    }
                }
            } else {
                MarkdownHighlighter.loadhljs();
            }
        }
    }

    dedent(text) {
        const lines = text.split(/\r\n|\r|\n/);
        let commonPrefix = null;
        for (const line of lines) {
            const preMatch = line && line.match(/^\s*(?=\S)/);
            if (preMatch) {
                const prefix = preMatch[0];
                if (commonPrefix !== null) {
                    for (let i = 0; i < commonPrefix.length; i++) {
                        // Like Python's textwrap.dedent, we'll remove both
                        // space and tab characters, but only if they match
                        if (prefix[i] !== commonPrefix[i]) {
                            commonPrefix = commonPrefix.substr(0, i);
                            break;
                        }
                    }
                } else {
                    commonPrefix = prefix;
                }

                if (!commonPrefix) {
                    break;
                }
            }
        }

        const commonLen = commonPrefix ? commonPrefix.length : 0;
        return lines
            .map(line => {
                return line.match(/\S/) ? line.substr(commonLen) : '';
            })
            .join('\n');
    }

    render() {
        const {
            id,
            style,
            className,
            highlight_config,
            dangerously_allow_html,
            link_target,
            mathjax,
            children,
            dedent,
        } = this.props;

        const textProp =
            type(children) === 'Array' ? children.join('\n') : children;
        const displayText =
            dedent && textProp ? this.dedent(textProp) : textProp;

        const componentTransforms = {
            dccLink: props => <DccLink {...props} />,
            dccMarkdown: props => (
                <Markdown
                    {...mergeDeepRight(
                        pick(['dangerously_allow_html', 'dedent'], this.props),
                        pick(['children'], props)
                    )}
                />
            ),
            dashMathjax: props => (
                <Math tex={props.value} inline={props.inline} />
            ),
        };

        const regexMath = value => {
            const newValue = value.replace(
                /(\${1,2})((?:\\.|[^$])+)\1/g,
                function (m, tag, src) {
                    const inline = tag.length === 1 || src.indexOf('\n') === -1;
                    return `<dashMathjax value='${src}' inline='${inline}'/>`;
                }
            );
            return newValue;
        };

        return (
            <LoadingElement
                id={id}
                ref={node => {
                    this.mdContainer = node;
                }}
                style={style}
                className={
                    ((highlight_config && highlight_config.theme) ||
                        className) &&
                    `${className ? className : ''} ${
                        highlight_config &&
                        highlight_config.theme &&
                        highlight_config.theme === 'dark'
                            ? 'hljs-dark'
                            : ''
                    }`
                }
            >
                <Markdown
                    source={displayText}
                    escapeHtml={!dangerously_allow_html}
                    linkTarget={link_target}
                    plugins={mathjax ? [RemarkMath] : []}
                    renderers={{
                        math: props => (
                            <Math tex={props.value} inline={false} />
                        ),

                        inlineMath: props => (
                            <Math tex={props.value} inline={true} />
                        ),

                        html: props =>
                            props.escapeHtml ? (
                                props.value
                            ) : (
                                <JsxParser
                                    jsx={
                                        mathjax
                                            ? regexMath(props.value)
                                            : props.value
                                    }
                                    components={componentTransforms}
                                    renderInWrapper={false}
                                />
                            ),
                    }}
                />
            </LoadingElement>
        );
    }
}

DashMarkdown.propTypes = propTypes;
