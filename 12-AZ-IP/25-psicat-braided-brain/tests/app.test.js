const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const core = require('../ui/game-core.js');

test('app startup renders scoped atlas cards without requests or implicit exports', () => {
  class Element {
    constructor() {
      this.children = [];
      this.dataset = {};
      this.style = { setProperty() {} };
      this.value = '';
      this.textContent = '';
    }
    set innerHTML(_value) { this.children = []; }
    appendChild(child) { this.children.push(child); }
    append(...children) { this.children.push(...children); }
    addEventListener() {}
    setAttribute() {}
  }
  const nodes = new Map();
  const document = {
    createElement: () => new Element(),
    addEventListener() {},
    getElementById(id) {
      if (id === 'braid-canvas') return null;
      if (!nodes.has(id)) nodes.set(id, new Element());
      return nodes.get(id);
    },
  };
  const context = vm.createContext({
    document, URL, navigator: {},
    fetch() { assert.fail('startup must not contact an external service'); },
    window: {
      PsiCatBraidedBrainCore: core,
      location: { href: 'http://127.0.0.1:8025/ui/index.html' },
      localStorage: {
        getItem: () => null,
        setItem() { assert.fail('startup must not implicitly export or save new records'); },
      },
      addEventListener() {},
    },
  });
  const app = fs.readFileSync(path.join(__dirname, '../ui/app.js'), 'utf8');
  vm.runInContext(app, context);
  assert.equal(nodes.get('target-list').children.length, core.LEVELS[0].targets.length);
  const atlas = nodes.get('atlas-list').children;
  assert.equal(atlas.length, core.getAtlasEntries(core.createCampaignState()).length);
  const text = atlas.flatMap((card) => card.children.map((child) => child.textContent)).join('\n');
  assert.match(text, /Evidence class: established-finding/);
  assert.match(text, /Evidence class: analogy/);
  assert.match(text, /Evidence class: empirical-summary/);
  assert.match(text, /Unvalidated correspondence:/);
  assert.match(nodes.get('privacy-note').textContent, /explicitly export/);
  const serviceWorker = fs.readFileSync(path.join(__dirname, '../sw.js'), 'utf8');
  const cacheName = serviceWorker.match(/const CACHE_NAME = '([^']+)'/)[1];
  assert.equal(vm.runInContext('OFFLINE_CACHE_NAME', context), cacheName);
});
