// @vitest-environment jsdom
import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { App } from './App';

test('wyświetla ekran szkieletu', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: 'Generator danych' })).toBeTruthy();
  expect(screen.getByText('Szkielet aplikacji')).toBeTruthy();
});
