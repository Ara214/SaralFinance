import { useEffect, useRef, useState, type FormEvent } from 'react'
import { ArrowRight, CircleAlert, LockKeyhole, ShieldCheck, Sparkles } from 'lucide-react'
import { motion, useReducedMotion } from 'motion/react'
import { request, type Language, type Result, type Sample, type Risk } from './api'

const languages: [Language, string, string][] = [['english', 'English', 'en'], ['hindi', 'हिंदी', 'hi'], ['hinglish', 'Hinglish', 'hi-Latn']]
const limit = 1500

function RiskCard({ risk }: { risk: Risk }) {
  return <article className="result-card">
    <div className="risk-head"><h3><ShieldCheck size={20}/> Risk level</h3><span className={`risk ${risk.risk_level.toLowerCase()}`}>{risk.risk_level} risk</span></div>
    {risk.risk_reasons.length ? <ul>{risk.risk_reasons.map(reason => <li key={reason}>{reason}</li>)}</ul> : <p>No significant indicators detected.</p>}
    <small>Use your official app or a verified number to confirm the message.</small>
  </article>
}

function WarningCard({ warning }: { warning: string }) {
  return <article className="result-card warning"><h3><CircleAlert size={20}/> Risk warning</h3><p>{warning}</p></article>
}

function ResultCards({ result }: { result: Result }) {
  const reduced = useReducedMotion()
  const locale = languages.find(([id]) => id === result.language)?.[2]
  return <motion.div className="result-stack" initial={reduced ? false : { opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
    <section className="result-card"><h3>What happened?</h3><p lang={locale}>{result.what_happened}</p></section>
    <section className="result-card"><h3>What should you do next?</h3><ul lang={locale}>{result.what_to_do_next.map((step, i) => <li key={i}>{step}</li>)}</ul></section>
    <RiskCard risk={result}/>
    {result.risk_warning && <WarningCard warning={result.risk_warning}/>}
    {result.analogy && <section className="result-card"><h3>Simple analogy</h3><p lang={locale}>{result.analogy}</p></section>}
  </motion.div>
}

export function Workspace() {
  const [message, setMessage] = useState('')
  const [language, setLanguage] = useState<Language>('english')
  const [examples, setExamples] = useState<Sample[]>([])
  const [metadataError, setMetadataError] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [single, setSingle] = useState<Result>()
  const active = useRef<AbortController | null>(null)
  const field = useRef<HTMLTextAreaElement>(null)
  useEffect(() => {
    const controller = new AbortController()
    request<Sample[]>('/api/examples', undefined, controller.signal).then(setExamples).catch(e => {
      if (!controller.signal.aborted) setMetadataError(e.message)
    })
    return () => { controller.abort(); active.current?.abort() }
  }, [])

  function resetOutput() { setError(''); setSingle(undefined) }

  async function submit(e: FormEvent) {
    e.preventDefault()
    if (active.current) return
    resetOutput()
    const trimmed = message.trim()
    if (!trimmed || [...trimmed].length > limit) {
      setError('Enter a message between 1 and 1,500 characters.')
      field.current?.focus()
      return
    }
    const controller = new AbortController()
    active.current = controller
    setBusy(true)
    try {
      setSingle(await request<Result>('/api/analyze', { message: trimmed, language }, controller.signal))
    } catch (failure) {
      if (!controller.signal.aborted) setError(failure instanceof Error ? failure.message : 'Could not analyze this message.')
    } finally {
      if (active.current === controller) { active.current = null; setBusy(false) }
    }
  }

  return <section className="workspace wrap">
    <header className="workspace-heading"><h1>Let’s make it simple.</h1><p>Paste your financial message below, and we'll help you understand what it says.</p></header>
    <div className="workspace-grid">
      <div>
        <form className="form-card" onSubmit={submit} aria-busy={busy}>
          <label htmlFor="message">Financial message</label>
          <textarea id="message" ref={field} disabled={busy} value={message} onChange={e => { setMessage([...e.target.value].slice(0, limit).join('')); resetOutput() }} aria-describedby="char-counter privacy" placeholder="Paste your banking SMS, UPI alert, KYC notification, or financial message here..."/>
          <div id="char-counter" className="counter">{[...message].length} / {limit.toLocaleString('en-IN')}</div>
          <fieldset disabled={busy}><legend>Response language</legend><div className="segmented">{languages.map(([id, label, locale]) => <label key={id}><input type="radio" name="language" value={id} checked={language === id} onChange={() => { setLanguage(id); resetOutput() }}/><span lang={locale}>{label}</span></label>)}</div></fieldset>
          {error && <p role="alert" className="error">{error}</p>}
          <div className="actions"><button className="button" type="submit" disabled={busy}>Analyze Message<ArrowRight size={17}/></button><button className="button secondary" type="button" disabled={busy || !message} onClick={() => { setMessage(''); resetOutput(); field.current?.focus() }}>Clear Message</button></div>
        </form>
        <article className="sample-card"><h3>Try a sample</h3>{metadataError && <p>{metadataError}</p>}<div className="samples">{examples.map(example => <button disabled={busy} type="button" key={example.id} onClick={() => { setMessage(example.message); resetOutput(); field.current?.focus() }}>{example.title}</button>)}</div></article>
        <p className="privacy" id="privacy"><LockKeyhole size={16}/> Remove personal details and secret codes before submitting.</p>
      </div>
      <aside aria-label="Analysis results" aria-live="polite">{single ? <ResultCards result={single}/> : !busy && <div className="empty-result"><Sparkles size={25}/><h2>Your explanation</h2><p>Analyze a message to see what it says, what signs to look for, and what you can do next.</p></div>}{busy && <Loading/>}</aside>
    </div>
  </section>
}

function Loading() {
  return <div className="empty-result" role="status"><span className="spinner"/><p>Understanding your financial message...</p></div>
}
