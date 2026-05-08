// File with known security issues for testing detection

// HIGH: hardcoded secret
const apiKey = "FAKE_KEY_FOR_TESTING_00000000";

// HIGH: AWS key
const awsKey = "AKIAIOSFODNN7EXAMPLE";

// MEDIUM: eval usage
function dangerous(code: string) {
  return eval(code);
}

// MEDIUM: innerHTML
function render(el: HTMLElement, html: string) {
  el.innerHTML = html;
}

// MEDIUM: Function constructor
const fn = new Function('return 42');

// LOW: non-https URL
const endpoint = "http://api.example.com/data";

// SAFE: https URL (should NOT be flagged)
const safeEndpoint = "https://api.example.com/data";

// SAFE: localhost http (should NOT be flagged)
const localApi = "http://localhost:3000/api";
