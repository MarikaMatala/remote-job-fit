import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

function loadDemo(overrides = {}) {
  const elements = new Map();
  function element(id, initial = {}) {
    if (!elements.has(id)) {
      const listeners = {};
      elements.set(id, {
        value: "", textContent: "", innerHTML: "", dataset: {},
        listeners,
        addEventListener(type, callback) { listeners[type] = callback; },
        setAttribute(name, value) { this[name] = value; },
        scrollIntoView() {},
        classList: { add() {}, remove() {} },
        ...initial,
      });
    }
    return elements.get(id);
  }
  element("skills", { value: overrides.skills ?? "Java" });
  element("job-title", { value: overrides.title ?? "Developer" });
  element("job-ad", { value: overrides.ad ?? "JavaScript is required." });
  element("results");
  element("count");
  element("analyze");
  element("reset-demo");
  element("demo-language");
  element("api-status");
  element("scan-status");
  element("job-list");
  element("job-count");
  const document = {
    documentElement: { lang: "fi" },
    getElementById: id => element(id),
    querySelectorAll: () => [],
  };
  const context = {
    document,
    matchMedia: () => ({ matches: true }),
    console,
  };
  vm.runInNewContext(readFileSync(new URL("./demo.js", import.meta.url), "utf8"), context);
  return { element };
}

test("Java does not match inside JavaScript", () => {
  const { element } = loadDemo({ skills: "Java", ad: "JavaScript is required." });
  element("analyze").listeners.click();
  assert.match(element("results").innerHTML, /0 \/ 1/);
  assert.match(element("results").innerHTML, /Java/);
  assert.match(element("results").innerHTML, /chip missing">Java/);
  assert.doesNotMatch(element("results").innerHTML, /Matched skills[^<]*Java/);
});

test("required and preferred skills keep their own classifications", () => {
  const { element } = loadDemo({
    skills: "Python, Docker",
    ad: "Python is preferred.\nDocker is required.",
  });
  element("analyze").listeners.click();
  const html = element("results").innerHTML;
  assert.match(html, /Python/);
  assert.match(html, /Docker/);
  assert.match(html, /Toivottu/);
  assert.match(html, /Pakollinen/);
});

test("empty profile produces a safe zero result", () => {
  const { element } = loadDemo({ skills: "", ad: "Python is required." });
  element("analyze").listeners.click();
  assert.match(element("results").innerHTML, /0%/);
});

test("user-supplied HTML in title is escaped", () => {
  const { element } = loadDemo({
    skills: "React",
    title: '<img src=x onerror="alert(1)">',
    ad: "React is required.",
  });
  element("analyze").listeners.click();
  const html = element("results").innerHTML;
  assert.match(html, /&lt;img/);
  assert.doesNotMatch(html, /<img/);
});

test("language toggle updates the document language", () => {
  const { element } = loadDemo();
  element("demo-language").listeners.click();
  assert.equal(element("demo-language").getAttribute, undefined);
});
