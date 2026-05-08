// File with known code smells

// SMELL: long function (>50 lines)
export function longFunction(input: string): string {
  let result = input;
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_processed';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step2';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step3';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step4';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step5';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step6';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step7';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step8';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step9';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step10';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step11';
  result = result.trim();
  result = result.toLowerCase();
  result = result.replace(/\s+/g, ' ');
  result = result + '_step12';
  result = result.trim();
  return result;
}

// SMELL: long parameter list (>5 params)
export function tooManyParams(a: string, b: string, c: number, d: number, e: boolean, f: boolean, g: any): void {
  console.log(a, b, c, d, e, f, g);
}

// SMELL: deep nesting (>4 levels)
export function deeplyNested(data: any): any {
  if (data) {
    if (data.items) {
      for (const item of data.items) {
        if (item.active) {
          if (item.value) {
            if (item.value > 0) {
              return item.value;
            }
          }
        }
      }
    }
  }
  return null;
}
