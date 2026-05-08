// A simple TypeScript file with known metrics
// 2 comment lines, 2 blank lines, 10 code lines = 14 total

import { Request, Response } from 'express';

export function greet(name: string): string {
  return `Hello, ${name}`;
}

export const add = (a: number, b: number): number => {
  return a + b;
};

export function isEven(n: number): boolean {
  if (n % 2 === 0) {
    return true;
  }
  return false;
}
