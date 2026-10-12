import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { Script, createContext } from 'node:vm';
import test from 'node:test';

const pages = ['../index.html', '../infantil/online/index.html'];
const contactUrl = 'https://wa.me/5551983300503?text=Teste%20local';

function conversionHandler(relativePath, gtag) {
  const html = readFileSync(fileURLToPath(new URL(relativePath, import.meta.url)), 'utf8');
  const script = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)]
    .map((match) => match[1])
    .find((source) => source.includes('function gtag_report_conversion('));
  assert.ok(script, `Conversion handler not found in ${relativePath}`);
  const sandbox = { window: { location: 'original-page' } };
  if (gtag !== undefined) sandbox.gtag = gtag;
  const context = createContext(sandbox);
  new Script(script, { filename: relativePath }).runInContext(context);
  return { sandbox, invoke: () => context.gtag_report_conversion(contactUrl) };
}

for (const page of pages) {
  test(`${page}: permits native WhatsApp navigation when tracking never calls back`, () => {
    const handler = conversionHandler(page, () => {});
    assert.equal(handler.invoke(), true, 'The onclick must not cancel the native contact link');
    assert.equal(handler.sandbox.window.location, 'original-page');
  });

  test(`${page}: permits native navigation when tracking is unavailable`, () => {
    const handler = conversionHandler(page);
    assert.equal(handler.invoke(), true);
    assert.equal(handler.sandbox.window.location, 'original-page');
  });

  test(`${page}: permits native navigation when tracking throws`, () => {
    const handler = conversionHandler(page, () => { throw new Error('Tracking unavailable'); });
    assert.equal(handler.invoke(), true);
    assert.equal(handler.sandbox.window.location, 'original-page');
  });

  test(`${page}: preserves the conversion payload without redirecting the page`, () => {
    const events = [];
    const handler = conversionHandler(page, (...args) => {
      events.push(args);
      if (typeof args[2]?.event_callback === 'function') args[2].event_callback();
    });
    assert.equal(handler.invoke(), true);
    assert.equal(handler.sandbox.window.location, 'original-page');
    assert.equal(events.length, 1);
    assert.equal(events[0][0], 'event');
    assert.equal(events[0][1], 'conversion');
    assert.deepEqual(JSON.parse(JSON.stringify(events[0][2])), {
      send_to: 'AW-18436097662/dh4_CNvs-PAcEP6MgtdE', value: 500.0, currency: 'BRL'
    });
  });
}
