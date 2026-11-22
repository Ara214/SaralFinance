import { useEffect, useState, type ReactNode } from 'react'
import { Link, NavLink, Route, Routes, useLocation } from 'react-router-dom'
import { ArrowDown, ArrowDownRight, ArrowRight, BookOpen, Check, Clipboard, Fingerprint, Languages, LockKeyhole, Menu, MessageSquareText, ShieldCheck, X } from 'lucide-react'
import { Workspace } from './Workspace'

const nav = [['/', 'Home'], ['/analyze', 'Analyze'], ['/how-it-works', 'How It Works'], ['/about', 'About']]
function Brand() {
  return <Link className="brand" to="/"><span className="brand-icon"><Fingerprint size={22} /></span>Saral<span>Finance</span></Link>
}

function Navbar() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()
  return <header className={pathname === '/' ? 'navbar dark' : 'navbar'}>
    <div className="wrap nav-inner">
      <Brand />
      <button className="menu-toggle" type="button" aria-label={open ? 'Close navigation' : 'Open navigation'} aria-expanded={open} onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button>
      <nav aria-label="Main navigation" className={open ? 'nav-links is-open' : 'nav-links'} onKeyDown={e => { if (e.key === 'Escape') setOpen(false) }}>
        {nav.map(([to, label]) => <NavLink end key={to} to={to} onClick={() => setOpen(false)}>{label}</NavLink>)}
      </nav>
      {pathname === '/' && <Link className="button nav-action" to="/analyze">Get Started <ArrowRight size={16} /></Link>}
    </div>
  </header>
}

export function ActionLink({ to, children, variant = '' }: { to: string; children: ReactNode; variant?: string }) {
  return <Link className={`button ${variant}`} to={to}>{children}<ArrowRight size={17} /></Link>
}

const steps = [
  [Clipboard, 'Paste your message', 'Add a banking alert, UPI notification, KYC reminder, or another financial message.'],
  [Languages, 'Choose your language', 'Read the explanation in English, Hindi, or conversational Hinglish.'],
  [ShieldCheck, 'Understand & stay safe', 'See what the message claims, the signals it contains, and how to verify it.'],
] as const
const features = [
  [BookOpen, 'Simple explanations', 'Understand amounts, dates, and financial terms in plain language.'],
  [Languages, 'Three languages', 'Use English, Hindi in Devanagari, or Hinglish in Roman script.'],
  [ShieldCheck, 'Suspicious message awareness', 'See which signals triggered a low, medium, or high risk rating.'],
  [LockKeyhole, 'Practical safety guidance', 'Get verification steps you can follow through official channels.'],
] as const

function Guide({ full = false }: { full?: boolean }) {
  return <section className="section wrap">
    <div className="section-heading"><h2>{full ? 'How SaralFinance works' : 'How it works'}</h2><p>From a confusing message to a clear next step.</p></div>
    <div className="grid-three">{steps.map(([Icon, title, description]) => <article className="info-card" key={title}><Icon /><h3>{title}</h3><p>{description}</p></article>)}</div>
    {full && <div className="guide-detail"><h3>What goes into your result?</h3><p>The app prepares an explanation in your chosen language. A separate rule engine checks for indicators such as requests for credentials, pressure to act quickly and unverified links. The app also uses a trained classifier to spot wording that may need extra caution.</p><ActionLink to="/analyze">Analyze a message</ActionLink></div>}
  </section>
}

function Hero() {
  return <section className="hero dark"><div className="ambient" aria-hidden="true"><div className="ambient-glow"><i/><i/><i/></div><div className="ambient-ribbons"><i/><i/><i/></div></div>
    <div className="hero-inner wrap">
      <div className="hero-copy">
        <h1>Finance,<br/><em>made simple.</em></h1>
        <p className="hero-lead">Understand every message.<br/>Make every decision with confidence.</p>
        <p className="hero-description">From banking alerts to suspicious messages, SaralFinance transforms complicated financial communication into clear, simple explanations in your preferred language.</p>
        <div className="actions"><ActionLink to="/analyze" variant="light-button">Simplify a Message</ActionLink><Link className="button outline" to="/how-it-works">Explore How It Works <ArrowDownRight size={17} /></Link></div>
      </div>
      <div className="hero-visual" aria-label="Example of a simplified bank alert">
        <div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="orbit orbit-three"/>
        <div className="example-flow">
          <div className="example-original"><span className="example-icon"><MessageSquareText size={19}/></span><div><strong>Banking alert</strong><p>UPI alert: INR 480 debited for a payment to Demo Kirana.</p></div></div>
          <div className="flow-arrow"><ArrowDown size={19}/></div>
          <div className="example-clear"><div className="example-caption"><span className="example-icon"><Check size={17}/></span> WHAT HAPPENED?</div><p>The alert says you paid <strong>₹480</strong> at Demo Kirana using UPI.</p><div className="example-next"><ShieldCheck size={17}/> Check the transaction in your official banking app.</div></div>
        </div>
      </div>
    </div>
    <div className="hero-bottom wrap"><span>English <i/> हिंदी <i/> Hinglish</span><Link to="/how-it-works" aria-label="Learn how it works"><ArrowDown size={18}/></Link></div>
  </section>
}

function Home() {
  return <><Hero/><Guide/><section className="surface section"><div className="wrap"><div className="section-heading"><h2>Why SaralFinance?</h2></div><div className="grid-four">{features.map(([Icon, title, description]) => <article className="info-card" key={title}><Icon/><h3>{title}</h3><p>{description}</p></article>)}</div></div></section>
    <section className="section final-cta dark"><h2>Clarity begins with understanding.</h2><ActionLink variant="light-button" to="/analyze">Try SaralFinance</ActionLink></section></>
}

function About() {
  return <section className="section wrap about"><h1>About SaralFinance</h1><p>SaralFinance is a university prompt engineering project by Team ZeroShot. It helps people understand financial messages and discover ways to verify them independently.</p><h2>Privacy</h2><p>The app does not store submitted messages. When online explanations are available, submitted text may be processed by an external service. Remove personal details, account numbers, OTPs, PINs, CVVs and passwords before submitting a message.</p><h2>Educational use</h2><p>Risk ratings use message patterns and a trained classifier. A low rating cannot authenticate a sender or confirm that a transaction took place. Use official channels to verify the original message.</p><ActionLink to="/analyze">Try the analyzer</ActionLink></section>
}

function Footer() {
  return <footer><div className="wrap footer-top"><div><Brand/><p>Built by Team ZeroShot</p></div><nav aria-label="Footer navigation"><Link to="/analyze">Analyzer</Link><Link to="/about">Privacy & About</Link></nav></div><div className="wrap footer-note">Educational use only. Verify financial messages through your official banking or payment app.</div></footer>
}

export default function App() {
  const { pathname } = useLocation()
  useEffect(() => { window.scrollTo(0, 0) }, [pathname])
  return <><a className="skip" href="#main-content">Skip to content</a><Navbar/><main id="main-content">
    <Routes><Route path="/" element={<Home/>}/><Route path="/analyze" element={<Workspace/>}/><Route path="/how-it-works" element={<Guide full/>}/><Route path="/about" element={<About/>}/><Route path="*" element={<section className="section wrap"><h1>Page not found</h1><ActionLink to="/">Go home</ActionLink></section>}/></Routes>
  </main><Footer/></>
}
