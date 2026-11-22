// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { Workspace } from './Workspace'
import { request } from './api'

vi.mock('./api', () => ({ request: vi.fn() }))
const sample = { id: 'debit', title: 'UPI debit', message: 'UPI debit INR 480' }
const low = { risk_level: 'Low', risk_score: 0, risk_reasons: [], risk_warning: null }
const result = { ...low, language: 'hinglish', what_happened: 'Message kehta hai ki ₹480 kate hain.', what_to_do_next: ['Official app check karein.'], analogy: null }
const api = vi.mocked(request)

beforeEach(() => {
  api.mockReset()
  api.mockImplementation(async path => {
    if (path === '/api/examples') return [sample]
    return result
  })
})
afterEach(cleanup)

it('inserts a sample, analyzes with the selected language and clears output', async () => {
  render(<Workspace/>)
  fireEvent.click(await screen.findByRole('button', { name: 'UPI debit' }))
  expect(screen.queryByRole('group', { name: 'Prompt technique' })).toBeNull()
  fireEvent.click(screen.getByRole('radio', { name: 'Hinglish' }))
  fireEvent.click(screen.getByRole('button', { name: 'Analyze Message' }))
  expect(await screen.findByText(result.what_happened)).toBeTruthy()
  expect(api).toHaveBeenCalledWith('/api/analyze', { message: sample.message, language: 'hinglish' }, expect.any(AbortSignal))
  fireEvent.click(screen.getByRole('button', { name: 'Clear Message' }))
  expect(screen.queryByText(result.what_happened)).toBeNull()
  expect((screen.getByLabelText('Financial message') as HTMLTextAreaElement).value).toBe('')
})

it('disables duplicate submissions while waiting', async () => {
  let complete: (value: unknown) => void = () => {}
  api.mockImplementation(path => path === '/api/analyze'
    ? new Promise(resolve => { complete = resolve })
    : Promise.resolve([sample]))
  render(<Workspace/>)
  fireEvent.click(await screen.findByRole('button', { name: 'UPI debit' }))
  const button = screen.getByRole('button', { name: 'Analyze Message' }) as HTMLButtonElement
  fireEvent.click(button)
  expect(button.disabled).toBe(true)
  expect(screen.getByRole('status').textContent).toContain('Understanding')
  fireEvent.click(button)
  expect(api.mock.calls.filter(([path]) => path === '/api/analyze')).toHaveLength(1)
  complete(result)
  await screen.findByText(result.what_happened)
  expect(button.disabled).toBe(false)
})

it('validates empty input and surfaces a backend error', async () => {
  render(<Workspace/>)
  const submit = screen.getByRole('button', { name: 'Analyze Message' })
  fireEvent.click(submit)
  expect(screen.getByRole('alert').textContent).toMatch(/Enter a message/)
  fireEvent.click(await screen.findByRole('button', { name: 'UPI debit' }))
  api.mockRejectedValueOnce(new Error('The provider timed out.'))
  fireEvent.click(submit)
  expect((await screen.findByRole('alert')).textContent).toMatch(/timed out/)
})
