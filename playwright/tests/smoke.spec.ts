import { test, expect } from '@playwright/test';

test('home page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Audio Transcription Platform/i);
  await expect(page.getByRole('heading', { name: /Audio Transcription Platform/i })).toBeVisible();
});
