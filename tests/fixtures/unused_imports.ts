import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import * as lodash from 'lodash';

export function MyComponent() {
  const [value, setValue] = useState(0);
  return value;
}
