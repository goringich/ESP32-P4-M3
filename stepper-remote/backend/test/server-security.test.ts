import test from 'node:test';
import assert from 'node:assert/strict';
import {
  browserOriginAllowed,
  isLoopbackHostname,
} from '../src/server.js';

test('operator host predicate recognizes only explicit loopback names', () => {
  assert.equal(isLoopbackHostname('127.0.0.1'), true);
  assert.equal(isLoopbackHostname('localhost'), true);
  assert.equal(isLoopbackHostname('::1'), true);
  assert.equal(isLoopbackHostname('192.168.1.20'), false);
  assert.equal(isLoopbackHostname('example.test'), false);
});

test('browser origin policy is local-only unless remote mode is explicit', () => {
  const previousRemote = process.env.STEPPER_REMOTE_ALLOW_REMOTE;
  const previousAllowed = process.env.STEPPER_REMOTE_ALLOWED_ORIGIN;

  try {
    delete process.env.STEPPER_REMOTE_ALLOW_REMOTE;
    delete process.env.STEPPER_REMOTE_ALLOWED_ORIGIN;

    assert.equal(
      browserOriginAllowed('http://127.0.0.1:5173', '127.0.0.1:3001'),
      true
    );
    assert.equal(
      browserOriginAllowed('https://example.test', '127.0.0.1:3001'),
      false
    );

    process.env.STEPPER_REMOTE_ALLOW_REMOTE = '1';
    assert.equal(
      browserOriginAllowed(
        'http://192.168.1.20:3001',
        '192.168.1.20:3001'
      ),
      true
    );

    process.env.STEPPER_REMOTE_ALLOWED_ORIGIN =
      'https://operator.example.test';
    assert.equal(
      browserOriginAllowed(
        'https://operator.example.test',
        '192.168.1.20:3001'
      ),
      true
    );
    assert.equal(
      browserOriginAllowed(
        'https://other.example.test',
        '192.168.1.20:3001'
      ),
      false
    );
  } finally {
    if (previousRemote === undefined) {
      delete process.env.STEPPER_REMOTE_ALLOW_REMOTE;
    } else {
      process.env.STEPPER_REMOTE_ALLOW_REMOTE = previousRemote;
    }

    if (previousAllowed === undefined) {
      delete process.env.STEPPER_REMOTE_ALLOWED_ORIGIN;
    } else {
      process.env.STEPPER_REMOTE_ALLOWED_ORIGIN = previousAllowed;
    }
  }
});
