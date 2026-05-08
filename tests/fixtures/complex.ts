// A function with known high cyclomatic complexity
// Expected: complexity = 1 + 12 = 13 (if, else if, else if, while, for, case x4, &&, ||, ??)

export function processData(input: any, mode: string): any {
  if (input === null) {
    return null;
  } else if (input === undefined) {
    return undefined;
  } else if (Array.isArray(input)) {
    let result = [];
    while (result.length < input.length) {
      for (let i = 0; i < input.length; i++) {
        switch (mode) {
          case 'upper':
            result.push(input[i].toUpperCase());
            break;
          case 'lower':
            result.push(input[i].toLowerCase());
            break;
          case 'trim':
            result.push(input[i].trim());
            break;
          case 'reverse':
            result.push(input[i].split('').reverse().join(''));
            break;
        }
      }
    }
    const isValid = input.length > 0 && result.length > 0;
    const hasMore = input.length > 10 || result.length > 10;
    const fallback = isValid ?? false;
    return result;
  }
  return input;
}

// A simple function for contrast
// Expected: complexity = 1 (no decision points)
export function identity(x: any): any {
  return x;
}
