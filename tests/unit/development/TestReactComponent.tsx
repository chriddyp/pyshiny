import React from 'react';
// A react component with a ton of TypeScript types to run tests over

class Message {}
type SomeString = "Hello"

/**
 * This is a description of the component.
 * It's multiple lines long.
 */
export default function ReactComponent({
    optionalArray,
    optionalBool,
    optionalFunc,
    optionalNumber = 42,
    optionalObject,
    optionalString = 'hello world',
    optionalSymbol,
    optionalNode,
    optionalElement,
    optionalMessage,
    optionalEnum,
    optionalUnion,
    optionalArrayOf,
    optionalObjectOf,
    optionalObjectWithShapeAndNestedDescription,
    optionalAny,
    customProp,
    customArrayProp,
    children,
    id,
}: {
  optionalArray?: any[];
  optionalBool?: boolean;
  optionalFunc?: () => void;
  optionalNumber?: number;
  optionalObject?: object;
  optionalString?: string;
  optionalSymbol?: symbol;
  optionalNode?: React.ReactNode;
  optionalElement?: React.ReactElement;
  optionalMessage?: Message;
  optionalEnum?: 'News' | 'Photos';
  optionalUnion?: string | number | Message;
  optionalArrayOf?: number[];
  optionalObjectOf?: { [key: string]: number };
  optionalObjectWithShapeAndNestedDescription?: {
      color?: string;
      fontSize?: number;
      figure?: {
          data?: object[];
          layout?: object;
      };
  };
  optionalAny?: any;
  customProp?: `${SomeString} World`;
  customArrayProp?: Array<`${SomeString} World`>;
  children?: React.ReactNode;
  id?: string;
}) {
  return <div>{children}</div>;
}
