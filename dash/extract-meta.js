#!/usr/bin/env node
if (process.env.MODULES_PATH) {
    module.paths.push(process.env.MODULES_PATH);
}
let ts,
    tsEnabled = true;
try {
    ts = require('typescript');
} catch (e) {
    ts = {};
    tsEnabled = false;
}
const fs = require('fs');
const path = require('path');
const reactDocs = require('react-docgen');

const args = process.argv.slice(2);
const src = args.slice(2);
const ignorePattern = args[0] ? new RegExp(args[0]) : null;
const reservedPatterns = args[1]
    ? args[1].split('|').map(part => new RegExp(part))
    : [];

function help() {
    console.error('usage: ');
    console.error(
        'extract-meta ^fileIgnorePattern ^forbidden$|^props$|^patterns$' +
        ' path/to/component(s) [path/to/more/component(s) ...] > metadata.json'
    );
}

if (!src.length) {
    help();
    process.exit(1);
}

function getTsConfigCompilerOptions() {
    // Since extract-meta can be run on JavaScript sources, if trying to get the
    // config doesn't work, we can fall back gracefully.
    try {
        const tsconfig = ts.getParsedCommandLineOfConfigFile('tsconfig.json', { esModuleInterop: true }, ts.sys);
        return tsconfig?.options ?? {};
    } catch {
        return {};
    }
}

let failedBuild = false;
const excludedDocProps = ['setProps', 'id', 'className', 'style'];

const isOptional = prop => (prop.getFlags() & ts.SymbolFlags.Optional) !== 0;

const PRIMITIVES = [
    'string',
    'number',
    'bool',
    'any',
    'array',
    'object',
    'node'
];

// These types take too long to parse because of heavy nesting.
const BANNED_TYPES = [
    'Document',
    'ShadowRoot',
    'ChildNode',
    'ParentNode',
];
const unionSupport = PRIMITIVES.concat('boolean', 'Element');

const reArray = new RegExp(`(${unionSupport.join('|')})\\[\\]`);

const isArray = rawType => reArray.test(rawType);

const isUnionLiteral = typeObj =>
    typeObj.types.every(
        t =>
            t.getFlags() &
            (ts.TypeFlags.StringLiteral |
                ts.TypeFlags.NumberLiteral |
                ts.TypeFlags.EnumLiteral |
                ts.TypeFlags.Undefined)
    );

function logError(error, filePath) {
    if (filePath) {
        process.stderr.write(`Error with path ${filePath}\n`);
    }
    process.stderr.write(error + '\n');
    if (error instanceof Error) {
        process.stderr.write(error.stack + '\n');
    }
}

function isReservedPropName(propName) {
    reservedPatterns.forEach(reservedPattern => {
        if (reservedPattern.test(propName)) {
            process.stderr.write(
                `\nERROR: "${propName}" matches reserved word ` +
                `pattern: ${reservedPattern.toString()}\n`
            );
            failedBuild = true;
        }
    });
    return failedBuild;
}

function checkDocstring(name, value) {
    if (
        !value ||
        (value.length < 1 && !excludedDocProps.includes(name.split('.').pop()))
    ) {
        logError(`\nDescription for ${name} is missing!`);
    }
}

function docstringWarning(doc) {
    checkDocstring(doc.displayName, doc.description);

    const exportedDisplayName = doc.exportedName || doc.displayName
    if (doc && doc.props) {
        Object.entries(doc.props || {}).forEach(([name, p]) =>
            checkDocstring(`${exportedDisplayName}.${name}`, p.description)
        );
    } else {
        // Soft fail
        console.warn(`${exportedDisplayName} does not have any props`)
    }
}

function zipArrays(...arrays) {
    const arr = [];
    for (let i = 0; i <= arrays[0].length - 1; i++) {
        arr.push(arrays.map(a => a[i]));
    }
    return arr;
}

function cleanPath(filepath) {
    return filepath.split(path.sep).join('/');
}

function parseJSX(filepath) {
    try {
        const src = fs.readFileSync(filepath);
        const doc = reactDocs.parse(src);
        Object.keys(doc.props).forEach(propName =>
            isReservedPropName(propName)
        );
        docstringWarning(doc);
        return doc;
    } catch (error) {
        logError(error, filepath);
    }
}

function gatherComponents(sources, components = {}) {
    const names = [];
    const filepaths = [];

    const gather = filepath => {
        if (ignorePattern && ignorePattern.test(filepath)) {
            return;
        }
        const extension = path.extname(filepath);
        if (['.jsx', '.js'].includes(extension)) {
            components[cleanPath(filepath)] = parseJSX(filepath);
        } else if (['.tsx', 'ts'].includes(extension)) {
            try {
                const name = /(.*)\.(ts|tsx)/.exec(path.basename(filepath))[1];
                filepaths.push(filepath);
                names.push(name);
            } catch (err) {
                process.stderr.write(
                    `ERROR: Invalid component file ${filepath}: ${err}`
                );
            }
        }
    };

    sources.forEach(sourcePath => {
        if (fs.lstatSync(sourcePath).isDirectory()) {
            fs.readdirSync(sourcePath).forEach(f => {
                const filepath = path.join(sourcePath, f);
                if (fs.lstatSync(filepath).isDirectory()) {
                    gatherComponents([filepath], components);
                } else {
                    gather(filepath);
                }
            });
        } else {
            gather(sourcePath);
        }
    });

    if (!tsEnabled) {
        return components;
    }

    const program = ts.createProgram(filepaths, getTsConfigCompilerOptions());
    const checker = program.getTypeChecker();

    const coerceValue = t => {
        // May need to improve for shaped/list literals.
        if (t.isStringLiteral()) return `'${t.value}'`;
        return t.value;
    };

    const getComponentFromExport = exp => {
        const decl = exp.valueDeclaration || exp.declarations[0];
        const type = checker.getTypeOfSymbolAtLocation(exp, decl);
        const typeSymbol = type.symbol || type.aliasSymbol;

        if (!typeSymbol) {
            return exp;
        }

        const symbolName = typeSymbol.getName();

        if (
            (symbolName === 'MemoExoticComponent' ||
                symbolName === 'ForwardRefExoticComponent') &&
            exp.valueDeclaration &&
            ts.isExportAssignment(exp.valueDeclaration) &&
            ts.isCallExpression(exp.valueDeclaration.expression)
        ) {
            const component = checker.getSymbolAtLocation(
                exp.valueDeclaration.expression.arguments[0]
            );

            if (component) return component;
        }
        return exp;
    };

    const getParent = node => {
        let parent = node;
        while (parent.parent) {
            if (parent.parent.kind === ts.SyntaxKind.SourceFile) {
                // We want the parent before the source file.
                break;
            }
            parent = parent.parent;
        }
        return parent;
    };

    const getEnum = typeObj => ({
        name: 'enum',
        value: typeObj.types.map(t => ({
            value: coerceValue(t),
            computed: false
        }))
    });

    const getUnion = (typeObj, propObj, parentType) => {
        let name = 'union',
            value;

        // Union only do base types
        value = typeObj.types
            .filter(t => {
                let typeName = t.intrinsicName;
                if (!typeName) {
                    if (t.members) {
                        typeName = 'object';
                    }
                }
                return (
                    unionSupport.includes(typeName) ||
                    isArray(checker.typeToString(t))
                );
            })
            .map(t => getPropType(t, propObj, parentType));

        if (!value.length) {
            name = 'any';
            value = undefined;
        }
        return {
            name,
            value
        };
    };

    const getPropTypeName = propName => {
        if (propName.includes('=>') || propName === 'Function') {
            return 'func';
        } else if (propName === 'boolean') {
            return 'bool';
        } else if (propName === '[]') {
            return 'array';
        } else if (
            propName === 'Element' ||
            propName === 'ReactNode' ||
            propName === 'ReactElement'
        ) {
            return 'node';
        }
        return propName;
    };

    const getPropType = (propType, propObj, parentType = null) => {
        // Types can get namespace prefixes or not.
        let name = checker.typeToString(propType).replace(/^React\./, '');
        let value, elements;
        const raw = name;

        const newParentType = (parentType || []).concat(raw)

        if (propType.isUnion()) {
            if (isUnionLiteral(propType)) {
                return {...getEnum(propType), raw};
            } else if (raw.includes('|')) {
                return {...getUnion(propType, propObj, newParentType), raw};
            }
        }

        name = getPropTypeName(name);

        // Shapes & array support.
        if (!PRIMITIVES.concat('enum', 'func', 'union').includes(name)) {
            if (
                // Excluding object with arrays in the raw.
                (name.includes('[]') && name.endsWith("]")) ||
                name.includes('Array')
            ) {
                name = 'arrayOf';
                const replaced = raw.replace('[]', '');
                if (unionSupport.includes(replaced)) {
                    // Simple types are easier.
                    value = {
                        name: getPropTypeName(replaced),
                        raw: replaced
                    };
                } else {
                    // Complex types get the type parameter (Array<type>)
                    const [nodeType] = checker.getTypeArguments(propType);

                    if (nodeType) {
                        value = getPropType(
                            nodeType, propObj, newParentType,
                        );
                    } else {
                        // Not sure, might be unsupported here.
                        name = 'array';
                    }
                }
            } else if (
                name === 'tuple' ||
                (name.startsWith('[') && name.endsWith(']'))
            ) {
                name = 'tuple';
                elements = propType.resolvedTypeArguments.map(
                    t => getPropType(t, propObj, newParentType)
                );
            } else if (
                BANNED_TYPES.includes(name) ||
                (parentType && parentType.includes(name))
            ) {
                console.error(`Warning nested type: ${name}`);
                name = 'any';
            } else {
                name = 'shape';
                // If the type is declared as union it will have a types attribute.
                if (propType.types && propType.types.length) {
                    if (isUnionLiteral(propType)) {
                        return {...getEnum(propType), raw};
                    }
                    return {
                        ...getUnion(propType, propObj, newParentType),
                        raw
                    };
                } else if (propType.indexInfos && propType.indexInfos.length) {
                    const {type} = propType.indexInfos[0];
                    name = 'objectOf';
                    value = getPropType(type, propObj, newParentType);
                } else {
                    value = getProps(
                        checker.getPropertiesOfType(propType),
                        propObj,
                        [],
                        {},
                        true,
                        newParentType,
                    );
                }
            }
        }

        return {
            name,
            value,
            elements,
            raw
        };
    };

    const getDefaultProps = (symbol, source) => {
        const statements = source.statements.filter(
            stmt =>
                (!!stmt.name &&
                    checker.getSymbolAtLocation(stmt.name) === symbol) ||
                ts.isExpressionStatement(stmt) ||
                ts.isVariableStatement(stmt)
        );
        return statements.reduce((acc, statement) => {
            let propMap = {};

            statement.getChildren().forEach(child => {
                let {right} = child;
                if (right && ts.isIdentifier(right)) {
                    const value = source.locals.get(right.escapedText);
                    if (
                        value &&
                        value.valueDeclaration &&
                        ts.isVariableDeclaration(value.valueDeclaration) &&
                        value.valueDeclaration.initializer
                    ) {
                        right = value.valueDeclaration.initializer;
                    }
                }
                if (right) {
                    const {properties} = right;
                    if (properties) {
                        propMap = getDefaultPropsValues(properties);
                    }
                }
            });

            return {
                ...acc,
                ...propMap
            };
        }, {});
    };

    const getPropComment = symbol => {
        // Doesn't work too good with the JsDocTags losing indentation.
        // But used only in props should be fine.
        const comment = symbol.getDocumentationComment();
        const tags = symbol.getJsDocTags();
        if (comment && comment.length) {
            return comment
                .map(c => c.text)
                .concat(
                    tags.map(t =>
                        ['@', t.name].concat((t.text || []).map(e => e.text))
                    )
                )
                .join('\n');
        }
        return '';
    };

    const getPropsForFunctionalComponent = type => {
        const callSignatures = type.getCallSignatures();

        for (const sig of callSignatures) {
            const params = sig.getParameters();
            if (params.length === 0) {
                continue;
            }

            // There is only one parameter for functional components: props
            const p = params[0];
            if (p.name === 'props' || params.length === 1) {
                return p;
            }
        }
        return null;
    };

    const getPropsForClassComponent = (typeSymbol, source, defaultProps) => {
        const childs = source.getChildAt(0);
        let stop;

        for (let i = 0, n = childs.getChildCount(); i < n && !stop; i++) {
            const c = childs.getChildAt(i);
            if (!ts.isClassDeclaration(c)) continue;

            if (!c.heritageClauses) continue;

            for (const clause of c.heritageClauses) {
                if (clause.token !== ts.SyntaxKind.ExtendsKeyword) continue;
                const t = clause.types[0];
                const propType = t.typeArguments[0];

                const type = checker.getTypeFromTypeNode(propType);

                return getProps(
                    type.getProperties(),
                    typeSymbol,
                    [],
                    defaultProps
                );
            }
        }
    };

    const getDefaultPropsValues = properties =>
        properties.reduce((acc, p) => {
            if (!p.name || !p.initializer) {
                return acc;
            }
            let propName, value;

            switch (p.name.kind) {
                case ts.SyntaxKind.NumericLiteral:
                case ts.SyntaxKind.StringLiteral:
                case ts.SyntaxKind.Identifier:
                    propName = p.name.text;
                    break;
                case ts.SyntaxKind.ComputedPropertyName:
                    propName = p.name.getText();
                    break;
            }

            const {initializer} = p;

            switch (initializer.kind) {
                case ts.SyntaxKind.StringLiteral:
                    value = `'${initializer.text}'`;
                    break;
                case ts.SyntaxKind.NumericLiteral:
                    value = initializer.text;
                    break;
                case ts.SyntaxKind.NullKeyword:
                    value = 'null';
                    break;
                case ts.SyntaxKind.FalseKeyword:
                    value = 'false';
                    break;
                case ts.SyntaxKind.TrueKeyword:
                    value = 'true';
                    break;
                default:
                    try {
                        value = initializer.getText();
                    } catch (e) {
                        value = undefined;
                    }
            }

            acc[propName] = {value, computed: false};

            return acc;
        }, {});

    const getDefaultPropsForClassComponent = (type, source) => {
        // For class component, the type has its own property, then get the
        // first declaration and one of them will be either
        // an ObjectLiteralExpression or an Identifier which get in the
        // newChild with the proper props.
        const defaultProps = type.getProperty('defaultProps');
        if (!defaultProps) {
            return {};
        }
        const decl = defaultProps.getDeclarations()[0];
        let propValues = {};

        decl.getChildren().forEach(child => {
            let newChild = child;

            if (ts.isIdentifier(child)) {
                // There should be two identifier, the first is ignored.
                const value = source.locals.get(child.escapedText);
                if (
                    value &&
                    value.valueDeclaration &&
                    ts.isVariableDeclaration(value.valueDeclaration) &&
                    value.valueDeclaration.initializer
                ) {
                    newChild = value.valueDeclaration.initializer;
                }
            }

            const {properties} = newChild;
            if (properties) {
                propValues = getDefaultPropsValues(properties);
            }
        });
        return propValues;
    };

    const getProps = (
        properties,
        propsObj,
        baseProps = [],
        defaultProps = {},
        flat = false,
        parentType = null,
    ) => {
        const results = {};

        properties.forEach(prop => {
            const name = prop.getName();
            if (isReservedPropName(name)) {
                return;
            }
            const propType = checker.getTypeOfSymbolAtLocation(
                prop,
                propsObj.valueDeclaration
            );
            const baseProp = baseProps.find(p => p.getName() === name);
            const defaultValue = defaultProps[name];

            const required =
                !isOptional(prop) &&
                (!baseProp || !isOptional(baseProp)) &&
                defaultValue === undefined;

            const description = getPropComment(prop);

            let result = {
                description,
                required,
                defaultValue
            };
            const type = getPropType(propType, propsObj, parentType);
            // root object is inserted as type,
            // otherwise it's flat in the value prop.
            if (!flat) {
                result.type = type;
            } else {
                result = {...result, ...type};
            }

            results[name] = result;
        });

        return results;
    };

    const getPropInfo = (propsObj, defaultProps) => {
        const propsType = checker.getTypeOfSymbolAtLocation(
            propsObj,
            propsObj.valueDeclaration
        );
        const baseProps = propsType.getApparentProperties();
        let propertiesOfProps = baseProps;

        if (propsType.isUnionOrIntersection()) {
            propertiesOfProps = [
                ...checker.getAllPossiblePropertiesOfTypes(propsType.types),
                ...baseProps
            ];

            if (!propertiesOfProps.length) {
                const subTypes = checker.getAllPossiblePropertiesOfTypes(
                    propsType.types.reduce(
                        (all, t) => [...all, ...(t.types || [])],
                        []
                    )
                );
                propertiesOfProps = [...subTypes, ...baseProps];
            }
        }

        return getProps(propertiesOfProps, propsObj, baseProps, defaultProps);
    };

    zipArrays(filepaths, names).forEach(([filepath, name]) => {
        const source = program.getSourceFile(filepath);
        const moduleSymbol = checker.getSymbolAtLocation(source);
        const exports = checker.getExportsOfModule(moduleSymbol);

        exports.forEach(exp => {
            let rootExp = getComponentFromExport(exp);
            const declaration =
                rootExp.valueDeclaration || rootExp.declarations[0];
            const type = checker.getTypeOfSymbolAtLocation(
                rootExp,
                declaration
            );

            let commentSource = rootExp;
            const typeSymbol = type.symbol || type.aliasSymbol;
            const originalName = rootExp.getName();

            if (!rootExp.valueDeclaration) {
                if (
                    originalName === 'default' &&
                    !typeSymbol &&
                    (rootExp.flags & ts.SymbolFlags.Alias) !== 0
                ) {
                    // Some type of Exotic?
                    commentSource =
                        checker.getAliasedSymbol(
                            commentSource
                        ).valueDeclaration;
                } else if (!typeSymbol) {
                    // Invalid component
                    return null;
                } else {
                    // Function components.
                    rootExp = typeSymbol;
                    commentSource = rootExp.valueDeclaration || rootExp.declarations[0];
                    if (
                        commentSource &&
                        commentSource.parent
                    ) {
                        // Function with export later like `const MyComponent = (props) => <></>;`
                        commentSource = getParent(
                            commentSource.parent
                        );
                    }
                }
            } else if (
                type.symbol &&
                (ts.isPropertyAccessExpression(declaration) ||
                    ts.isPropertyDeclaration(declaration))
            ) {
                commentSource = type.symbol.declarations[0];
            }

            if (commentSource.valueDeclaration) {
                commentSource = commentSource.valueDeclaration; // class components
                if (
                    commentSource.parent &&
                    commentSource.parent.kind !== ts.SyntaxKind.SourceFile
                ) {
                    // Memo components
                    commentSource = commentSource.parent;
                }
            }

            const isArrowFunction = ts.isArrowFunction(declaration)
            const isClass = ts.isClassDeclaration(declaration);
            const isFunction = ts.isFunctionDeclaration(declaration)

            if (!isArrowFunction && !isClass && !isFunction) {
                // we do not care about these exports
                return null
            }

            if (isArrowFunction || isFunction) {
                const signature = checker.getSignaturesOfType(type, ts.SignatureKind.Call)[0];
                const returnType = checker.typeToString(signature.getReturnType());
                if (!['Element', 'any', 'null'].includes(returnType)) {
                    // Not JSX so no need to classifiy as compnent
                    return null;
                }
            }

            let defaultProps = getDefaultProps(typeSymbol, source);
            const propsType = getPropsForFunctionalComponent(type);
            const isContext = !!type.getProperty('isContext');

            let props;

            if (propsType) {
                if (
                    propsType.valueDeclaration &&
                    propsType.valueDeclaration.name &&
                    propsType.valueDeclaration.name.elements &&
                    propsType.valueDeclaration.name.elements.length
                ) {
                    defaultProps = getDefaultPropsValues(propsType.valueDeclaration.name.elements);
                }
                props = getPropInfo(propsType, defaultProps);
            } else {
                defaultProps = getDefaultPropsForClassComponent(type, source);
                props = getPropsForClassComponent(
                    typeSymbol,
                    source,
                    defaultProps
                );
            }

            if (!props) {
                // Ensure empty components has props.
                props = {};
            }

            const fullText = source.getFullText();
            let description = '';
            const commentRanges = ts.getLeadingCommentRanges(
                fullText,
                commentSource.getFullStart()
            );
            if (commentRanges && commentRanges.length) {
                description = commentRanges
                    .map(r =>
                        fullText
                            .slice(r.pos + 4, r.end - 3)
                            .split('\n')
                            .map(s => s.replace(/^(\s*\*?\s)/, ''))
                            .filter(e => e)
                            .join('\n')
                    )
                    .join('');
            }
            const doc = {
                displayName: name,
                description,
                props,
                isContext,
                exportedName: rootExp.name
            };
            docstringWarning(doc);

            // todo: Add support for mutiple components in single file
            components[cleanPath(filepath)] = doc;
        });
    });

    return components;
}

const metadata = gatherComponents(Array.isArray(src) ? src : [src]);
if (!failedBuild) {
    process.stdout.write(JSON.stringify(metadata, null, 2));
} else {
    logError('extract-meta failed');
    process.exit(1);
}
