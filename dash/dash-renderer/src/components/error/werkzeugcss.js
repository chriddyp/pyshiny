// Werkzeug css included as a string, because we want to inject
// it into an iframe srcDoc

export default `
body {
    margin: 0px;
    overflow: hidden;
}

.traceback {
    background-color: white;
    border: 2px solid #dfe8f3;
    border-radius: 0px 0px 4px 4px;
    color: #506784;
}

h2.traceback {
    background-color: #f3f6fa;
    border: 2px solid #dfe8f3;
    border-bottom: 0px;
    box-sizing: border-box;
    border-radius: 4px 4px 0px 0px;
    color: #506784;
}

h2.traceback em {
    color: #506784;
    font-weight: 100;
}

.traceback pre, .debugger textarea {
    background-color: #F3F6FA;
}

.debugger h1 {
    color: #506784;
    font-family: Roboto;
}

.explanation {
    color: #A2B1C6;
}

/* Hide the Don't Panic! footer */
.debugger .footer {
    display: none;
}

/* Hide all of the Dash traceback stuff that leads up to the call */
.line.before {
    display: none;
}

div.debugger {
    padding: 0px;
}

.debugger h1 {
    display: none;
}

.debugger .errormsg {
    margin: 0;
    color: #506784;
    font-size: 16px;
    background-color: #f3f6fa;
    border: 2px solid #dfe8f3;
    box-sizing: border-box;
    border-radius: 4px;
    padding: 10px;
}

.debugger .pastemessage input {
    display: none;
}

.debugger .explanation {
    display: none;
}

.debugger div.plain {
    border-radius: 4px;
    border-width: 2px;
    color: #506784;
}

.plain {
    display: block !important;
}
.plain > form > p {
    display: none;
}
.plain pre {
    padding: 15px !important;
    overflow-x: scroll;
}

.debugger div.traceback pre {
    cursor: default;
}

.debugger .traceback .source pre.line img {
    display: none;
}
`;
