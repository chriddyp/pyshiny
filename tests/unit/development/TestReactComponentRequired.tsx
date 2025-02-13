// A react component with a ton of TypeScript types to run tests over
import React from 'react';

class Message {}
type SomeString = "Hello"

/**
 * This is a description of the component.
 * It's multiple lines long.
 */
export default function ReactComponent({
    requiredArray,
    requiredBool,
    requiredFunc,
    requiredNumber = 42,
    requiredObject,
    requiredString = 'hello world',
    requiredSymbol,
    requiredNode,
    requiredElement,
    requiredMessage,
    requiredEnum,
    requiredUnion,
    requiredArrayOf,
    requiredObjectOf,
    requiredObjectWithShapeAndNestedDescription,
    requiredAny,
    customProp,
    customArrayProp,
    children,
    id,
}: {
  requiredArray: any[];
  requiredBool: boolean;
  requiredFunc: () => void;
  requiredNumber: number;
  requiredObject: object;
  requiredString: string;
  requiredSymbol: symbol;
  requiredNode: React.ReactNode;
  requiredElement: React.ReactElement;
  requiredMessage: Message;
  requiredEnum: 'News' | 'Photos';
  requiredUnion: string | number | Message;
  requiredArrayOf: number[];
  requiredObjectOf: { [key: string]: number };
  requiredObjectWithShapeAndNestedDescription: {
      color: string;
      fontSize: number;
      figure: {
          data: object[];
          layout: object;
      };
  };
  requiredAny: any;
  customProp: `${SomeString} World`;
  customArrayProp: Array<`${SomeString} World`>;
  children: React.ReactNode;
  id: string;
}) {
  return <div>{children}</div>;
}
