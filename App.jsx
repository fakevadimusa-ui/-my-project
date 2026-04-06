import { useState, useEffect, useCallback } from "react";
import FiveYearPlan from "./FiveYearPlan.jsx";

const STORAGE_KEY = "kbros-command-center-v2";

const ROADMAP_DATA = [
  {
    id: "foundation", phase: "Phase 1", title: "Foundation", subtitle: "Build the machine",
    status: "current", color: "#4f46e5",
    milestones: [
      { id: "f1", text: "Understand wholesale process end-to-end", done: false },
      { id: "f2", text: "Set up LLC + business bank account", done: false },
      { id: "f3", text: "Build purchase agreement + assignment contract", done: false },
      { id: "f4", text: "Build cash buyer list (10+ buyers)", done: false },
      { id: "f5", text: "Set up lead tracking system (spreadsheet or CRM)", done: false },
      { id: "f6", text: "Learn to pull comps + estimate ARV", done: false },
      { id: "f7", text: "Learn MAO formula (ARV × 0.7 − repairs − fee)", done: false },
      { id: "f8", text: "Practice seller call scripts", done: false },
    ],
  },
  {
    id: "first-deal", phase: "Phase 2", title: "First Deal", subtitle: "Get to $0 → $1",
    status: "locked", color: "#0891b2",
    milestones: [
      { id: "d1", text: "Drive for dollars — find 50 distressed properties", done: false },
      { id: "d2", text: "Pull FSBO leads from Zillow/Craigslist weekly", done: false },
      { id: "d3", text: "Cold call 20 sellers per day for 30 days", done: false },
      { id: "d4", text: "Send first offer / get property under contract", done: false },
      { id: "d5", text: "Assign contract to cash buyer", done: false },
      { id: "d6", text: "Close first deal — collect assignment fee", done: false },
      { id: "d7", text: "Document what worked for repeatable process", done: false },
    ],
  },
  {
    id: "consistency", phase: "Phase 3", title: "Consistency", subtitle: "1–2 deals/month",
    status: "locked", color: "#059669",
    milestones: [
      { id: "c1", text: "Mail 500+ letters/postcards per month", done: false },
      { id: "c2", text: "Add skip tracing for absentee owners", done: false },
      { id: "c3", text: "Build agent referral pipeline (2–3 agents)", done: false },
      { id: "c4", text: "Systematize daily lead gen routine", done: false },
      { id: "c5", text: "Track KPIs: calls, offers, contracts, closes", done: false },
      { id: "c6", text: "Average $5K–$10K per deal", done: false },
      { id: "c7", text: "Stack 3 months of deal revenue", done: false },
    ],
  },
  {
    id: "scale", phase: "Phase 4", title: "Scale", subtitle: "3–5 deals/month",
    status: "locked", color: "#d97706",
    milestones: [
      { id: "s1", text: "Hire virtual assistant for cold calling", done: false },
      { id: "s2", text: "Launch PPC / Google Ads for motivated sellers", done: false },
      { id: "s3", text: "Add SMS/ringless voicemail campaigns", done: false },
      { id: "s4", text: "Build disposition team or JV with other wholesalers", done: false },
      { id: "s5", text: "Create SOPs for every step of the process", done: false },
      { id: "s6", text: "Automate follow-ups with CRM drip sequences", done: false },
      { id: "s7", text: "Hit $20K+/month consistently", done: false },
    ],
  },
  {
    id: "empire", phase: "Phase 5", title: "Empire", subtitle: "Own it, don't operate it",
    status: "locked", color: "#dc2626",
    milestones: [
      { id: "e1", text: "Hire acquisitions manager (commission-based)", done: false },
      { id: "e2", text: "Hire dispo manager to handle buyer side", done: false },
      { id: "e3", text: "Expand to 2nd market (KC, Tulsa, OKC, etc.)", done: false },
      { id: "e4", text: "Add creative finance deals (sub-to, seller finance)", done: false },
      { id: "e5", text: "Start keeping rentals from wholesale pipeline", done: false },
      { id: "e6", text: "Build brand — website, SEO, social proof", done: false },
      { id: "e7", text: "Business runs without you — $50K+/month revenue", done: false },
    ],
  },
];

const INITIAL_CODE_SESSIONS = [
  {
    id: "session-1", date: "Apr 5, 2026", title: "GitHub sync setup",
    summary: "Connected home PC to GitHub, pushed project files, set up repo for cross-device sync.",
    status: "done",
  },
];

const INITIAL_NEXT_STEPS = [
  { id: "ns1", text: "Clone repo on school PC", done: false },
  { id: "ns2", text: "Set up CLAUDE.md with project context", done: false },
  { id: "ns3", text: "Build daily pull/push Git habit", done: false },
];

export default function KBrosCommandCenter() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [expandedPhase, setExpandedPhase] = useState("foundation");
  const [newSession, setNewSession] = useState({ title: "", summary: "" });
  const [newStep, setNewStep] = useState("");
  const [showAddSession, setShowAddSession] = useState(false);
  const [leads, setLeads] = useState([]);
  const [leadsUpdated, setLeadsUpdated] = useState("");
  const [leadStatuses, setLeadStatuses] = useState(() => {
    try { return JSON.parse(localStorage.getItem("kbros-lead-statuses") || "{}"); } catch { return {}; }
  });

  useEffect(() => {
    fetch("/leads.json")
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d) { setLeads(d.leads || []); setLeadsUpdated(d.updated || ""); }
      })
      .catch(() => {});
  }, []);

  const setLeadStatus = (id, status) => {
    const updated = { ...leadStatuses, [id]: status };
    setLeadStatuses(updated);
    localStorage.setItem("kbros-lead-statuses", JSON.stringify(updated));
  };

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setData(JSON.parse(saved));
      } else {
        const initial = { roadmap: ROADMAP_DATA, codeSessions: INITIAL_CODE_SESSIONS, nextSteps: INITIAL_NEXT_STEPS };
        setData(initial);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
      }
    } catch {
      setData({ roadmap: ROADMAP_DATA, codeSessions: INITIAL_CODE_SESSIONS, nextSteps: INITIAL_NEXT_STEPS });
    }
    setLoading(false);
  }, []);

  const saveData = useCallback((newData) => {
    setData(newData);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(newData)); }
    catch (e) { console.error("Save failed:", e); }
  }, []);

  const toggleMilestone = (phaseId, milestoneId) => {
    const updated = { ...data };
    updated.roadmap = updated.roadmap.map((phase) =>
      phase.id === phaseId
        ? { ...phase, milestones: phase.milestones.map((m) => m.id === milestoneId ? { ...m, done: !m.done } : m) }
        : phase
    );
    updated.roadmap = updated.roadmap.map((phase, i) => {
      const allDone = phase.milestones.every((m) => m.done);
      const anyDone = phase.milestones.some((m) => m.done);
      const prevAllDone = i === 0 || updated.roadmap[i - 1].milestones.every((m) => m.done);
      if (allDone) return { ...phase, status: "done" };
      if (anyDone || (i === 0) || prevAllDone) return { ...phase, status: "current" };
      return { ...phase, status: "locked" };
    });
    saveData(updated);
  };

  const toggleNextStep = (stepId) => {
    const updated = { ...data, nextSteps: data.nextSteps.map((s) => s.id === stepId ? { ...s, done: !s.done } : s) };
    saveData(updated);
  };

  const addSession = () => {
    if (!newSession.title.trim()) return;
    const updated = {
      ...data, codeSessions: [{
        id: `session-${Date.now()}`,
        date: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
        title: newSession.title, summary: newSession.summary, status: "done",
      }, ...data.codeSessions],
    };
    saveData(updated);
    setNewSession({ title: "", summary: "" });
    setShowAddSession(false);
  };

  const addNextStep = () => {
    if (!newStep.trim()) return;
    saveData({ ...data, nextSteps: [...data.nextSteps, { id: `ns-${Date.now()}`, text: newStep, done: false }] });
    setNewStep("");
  };

  const removeNextStep = (id) => saveData({ ...data, nextSteps: data.nextSteps.filter((s) => s.id !== id) });
  const removeSession = (id) => saveData({ ...data, codeSessions: data.codeSessions.filter((s) => s.id !== id) });

  if (loading || !data) {
    return (
      <div style={s.loadingWrap}>
        <div style={s.spinner} />
        <div style={s.loadingText}>Loading command center...</div>
      </div>
    );
  }

  const totalMilestones = data.roadmap.reduce((a, p) => a + p.milestones.length, 0);
  const doneMilestones = data.roadmap.reduce((a, p) => a + p.milestones.filter((m) => m.done).length, 0);
  const progressPct = Math.round((doneMilestones / totalMilestones) * 100);
  const phaseProgress = (phase) => Math.round((phase.milestones.filter((m) => m.done).length / phase.milestones.length) * 100);
  const currentPhase = data.roadmap.find((p) => p.status === "current") || data.roadmap[0];
  const nextStepsDone = data.nextSteps.filter((s) => s.done).length;

  return (
    <div style={s.page}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #f4f4f5; }
        button { cursor: pointer; transition: opacity 0.15s; }
        button:hover { opacity: 0.82; }
        .mrow:hover { background: #f5f5f5 !important; }
        .pgcard:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-1px); }
        .pgcard { transition: all 0.2s; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeUp { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
        .fade { animation: fadeUp 0.3s ease; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-thumb { background: #ddd; border-radius: 3px; }
      `}</style>

      {/* HEADER */}
      <div style={s.header}>
        <div style={s.headerInner}>
          <div style={s.brand}>
            <div style={s.logo}>K</div>
            <div>
              <div style={s.brandName}>KBros Command Center</div>
              <div style={s.brandSub}>Wholesaling Empire · Springfield, MO</div>
            </div>
          </div>
          <div style={s.headerStats}>
            <StatPill label="Overall" value={`${progressPct}%`} color="#4f46e5" />
            <StatPill label="Milestones" value={`${doneMilestones}/${totalMilestones}`} color="#059669" />
            <StatPill label="Sessions" value={data.codeSessions.length} color="#0891b2" />
            <StatPill label="Next Steps" value={`${nextStepsDone}/${data.nextSteps.length}`} color="#d97706" />
          </div>
        </div>
        <div style={s.masterBar}>
          <div style={{ ...s.masterFill, width: `${progressPct}%` }} />
        </div>
      </div>

      {/* TABS */}
      <div style={s.tabsWrap}>
        <div style={s.tabs}>
          {[{ key: "overview", label: "Overview" }, { key: "leads", label: `Leads ${leads.length ? `(${leads.filter(l=>l.score>=3).length} hot)` : ""}` }, { key: "roadmap", label: "Roadmap" }, { key: "sessions", label: "Code Log" }, { key: "next", label: "Next Steps" }, { key: "vision", label: "5-Year Vision" }].map((tab) => (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)}
              style={{ ...s.tab, ...(activeTab === tab.key ? s.tabActive : {}) }}>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div style={s.content}>

        {/* ── OVERVIEW ── */}
        {activeTab === "overview" && (
          <div className="fade">
            <div style={s.overviewTop}>
              <div style={s.ringWrap}>
                <ProgressRing pct={progressPct} size={180} stroke={14} color="#4f46e5" />
                <div style={s.ringInner}>
                  <div style={s.ringPct}>{progressPct}%</div>
                  <div style={s.ringLabel}>complete</div>
                </div>
              </div>
              <div style={s.overviewRight}>
                <div style={s.overviewLabel}>Currently in</div>
                <div style={s.currentPhaseTitle}>{currentPhase.phase}: {currentPhase.title}</div>
                <div style={s.currentPhaseSub}>{currentPhase.subtitle}</div>
                <div style={s.miniBarWrap}>
                  <div style={s.miniBarLabel}><span>Phase progress</span><span>{phaseProgress(currentPhase)}%</span></div>
                  <div style={s.miniBarTrack}>
                    <div style={{ ...s.miniBarFill, width: `${phaseProgress(currentPhase)}%`, background: currentPhase.color }} />
                  </div>
                </div>
                <div style={{ ...s.badge, background: currentPhase.color + "18", color: currentPhase.color }}>
                  {currentPhase.milestones.filter(m => m.done).length} of {currentPhase.milestones.length} milestones done
                </div>
              </div>
            </div>

            <div style={s.phaseGrid}>
              {data.roadmap.map((phase) => (
                <div key={phase.id} className="pgcard"
                  style={{ ...s.phaseGridCard, borderTop: `3px solid ${phase.color}` }}
                  onClick={() => { setActiveTab("roadmap"); setExpandedPhase(phase.id); }}>
                  <div style={s.phaseGridTop}>
                    <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, color: phase.color }}>{phase.phase}</span>
                    {phase.status === "done" && <span style={{ color: "#059669", fontSize: 12 }}>✓ Done</span>}
                    {phase.status === "locked" && <span style={{ color: "#bbb", fontSize: 11 }}>🔒</span>}
                    {phase.status === "current" && <span style={{ color: phase.color, fontSize: 11, fontWeight: 700 }}>● Active</span>}
                  </div>
                  <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 2 }}>{phase.title}</div>
                  <div style={{ fontSize: 11, color: "#999", marginBottom: 10 }}>{phase.subtitle}</div>
                  <div style={{ height: 4, background: "#f0f0f0", borderRadius: 2, marginBottom: 4 }}>
                    <div style={{ height: 4, borderRadius: 2, background: phase.color, width: `${phaseProgress(phase)}%`, transition: "width 0.4s" }} />
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: phase.color }}>{phaseProgress(phase)}%</div>
                </div>
              ))}
            </div>

            {data.nextSteps.filter(st => !st.done).length > 0 && (
              <div style={s.quickNext}>
                <div style={s.quickNextTitle}>Up next</div>
                {data.nextSteps.filter(st => !st.done).slice(0, 3).map(step => (
                  <div key={step.id} style={s.quickNextItem}>
                    <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#d97706", flexShrink: 0 }} />
                    {step.text}
                  </div>
                ))}
                {data.nextSteps.filter(st => !st.done).length > 3 && (
                  <button onClick={() => setActiveTab("next")} style={s.seeAllBtn}>
                    See all {data.nextSteps.filter(st => !st.done).length} steps →
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── ROADMAP ── */}
        {activeTab === "roadmap" && (
          <div className="fade">
            <div style={s.phaseNav}>
              {data.roadmap.map((phase) => (
                <button key={phase.id} onClick={() => setExpandedPhase(phase.id)}
                  style={{
                    ...s.phaseBtn,
                    ...(expandedPhase === phase.id ? { border: `2px solid ${phase.color}`, boxShadow: `0 0 0 3px ${phase.color}18` } : {}),
                    ...(phase.status === "done" ? { background: "#f0fdf4" } : {}),
                  }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: 1, color: phase.color }}>{phase.phase}</span>
                    {phase.status === "done" && <span style={{ fontSize: 12, color: "#059669" }}>✓</span>}
                    {phase.status === "locked" && <span style={{ fontSize: 11 }}>🔒</span>}
                  </div>
                  <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 2 }}>{phase.title}</div>
                  <div style={{ fontSize: 11, color: "#999", marginBottom: 10 }}>{phase.subtitle}</div>
                  <div style={{ height: 3, background: "#f0f0f0", borderRadius: 2, marginBottom: 4 }}>
                    <div style={{ height: 3, borderRadius: 2, background: phase.color, width: `${phaseProgress(phase)}%` }} />
                  </div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: phase.color }}>{phaseProgress(phase)}%</div>
                </button>
              ))}
            </div>

            {data.roadmap.filter((p) => p.id === expandedPhase).map((phase) => (
              <div key={phase.id} style={{ ...s.milestoneCard, borderTop: `4px solid ${phase.color}` }}>
                <div style={s.milestoneHeader}>
                  <div>
                    <h2 style={{ fontSize: 20, fontWeight: 800, color: phase.color }}>{phase.phase}: {phase.title}</h2>
                    <p style={{ fontSize: 13, color: "#888", marginTop: 4 }}>{phase.subtitle}</p>
                  </div>
                  <div style={{ fontSize: 26, fontWeight: 800 }}>
                    <span style={{ color: phase.color }}>{phase.milestones.filter(m => m.done).length}</span>
                    <span style={{ color: "#ddd" }}> / {phase.milestones.length}</span>
                  </div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {phase.milestones.map((m) => (
                    <button key={m.id} className="mrow" onClick={() => toggleMilestone(phase.id, m.id)}
                      style={{ ...s.milestoneItem, ...(m.done ? { background: "#f0fdf4", borderColor: "#bbf7d0" } : {}) }}>
                      <div style={{ ...s.checkbox, ...(m.done ? { background: phase.color, borderColor: phase.color, color: "#fff" } : { borderColor: phase.color + "66" }) }}>
                        {m.done && "✓"}
                      </div>
                      <span style={{ fontSize: 14, color: m.done ? "#aaa" : "#222", textDecoration: m.done ? "line-through" : "none" }}>
                        {m.text}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ── CODE LOG ── */}
        {activeTab === "sessions" && (
          <div className="fade">
            <div style={s.sectionTop}>
              <h2 style={s.sectionTitle}>Claude Code Session Log</h2>
              <button onClick={() => setShowAddSession(!showAddSession)} style={s.addBtn}>+ Log Session</button>
            </div>
            {showAddSession && (
              <div style={s.addForm}>
                <input style={s.input} placeholder="What did you build?" value={newSession.title}
                  onChange={(e) => setNewSession({ ...newSession, title: e.target.value })} />
                <input style={s.input} placeholder="Quick summary..." value={newSession.summary}
                  onChange={(e) => setNewSession({ ...newSession, summary: e.target.value })} />
                <div style={{ display: "flex", gap: 8 }}>
                  <button onClick={addSession} style={s.submitBtn}>Save Session</button>
                  <button onClick={() => setShowAddSession(false)} style={s.cancelBtn}>Cancel</button>
                </div>
              </div>
            )}
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {data.codeSessions.map((session, i) => (
                <div key={session.id} style={s.sessionCard}>
                  <div style={s.sessionNum}>#{data.codeSessions.length - i}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                      <div style={{ fontSize: 11, color: "#aaa", fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.5 }}>{session.date}</div>
                      <button onClick={() => removeSession(session.id)} style={s.removeBtn}>×</button>
                    </div>
                    <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 4 }}>{session.title}</h3>
                    <p style={{ fontSize: 13, color: "#777", lineHeight: 1.5 }}>{session.summary}</p>
                  </div>
                </div>
              ))}
              {data.codeSessions.length === 0 && <div style={s.emptyState}>No sessions logged yet.</div>}
            </div>
          </div>
        )}

        {/* ── NEXT STEPS ── */}
        {activeTab === "next" && (
          <div className="fade">
            <div style={s.sectionTop}>
              <h2 style={s.sectionTitle}>Next Steps</h2>
              <span style={{ fontSize: 13, fontWeight: 600, color: "#d97706", background: "#fef3c7", padding: "4px 12px", borderRadius: 20 }}>
                {nextStepsDone}/{data.nextSteps.length} done
              </span>
            </div>
            <div style={{ display: "flex", gap: 8, margin: "16px 0" }}>
              <input style={{ ...s.input, flex: 1 }} placeholder="Add a next step..."
                value={newStep} onChange={(e) => setNewStep(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addNextStep()} />
              <button onClick={addNextStep} style={s.submitBtn}>Add</button>
            </div>
            {data.nextSteps.length > 0 && (
              <div style={{ ...s.miniBarTrack, marginBottom: 16 }}>
                <div style={{ ...s.miniBarFill, width: `${Math.round((nextStepsDone / data.nextSteps.length) * 100)}%`, background: "#d97706" }} />
              </div>
            )}
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {data.nextSteps.map((step) => (
                <div key={step.id} style={{ ...s.stepItem, ...(step.done ? { background: "#f0fdf4", borderColor: "#bbf7d0" } : {}) }}>
                  <button onClick={() => toggleNextStep(step.id)} style={{
                    ...s.checkbox,
                    ...(step.done ? { background: "#059669", borderColor: "#059669", color: "#fff" } : { borderColor: "#d97706" }),
                  }}>{step.done && "✓"}</button>
                  <span style={{ fontSize: 14, flex: 1, textDecoration: step.done ? "line-through" : "none", color: step.done ? "#aaa" : "#222" }}>
                    {step.text}
                  </span>
                  <button onClick={() => removeNextStep(step.id)} style={s.removeBtn}>×</button>
                </div>
              ))}
              {data.nextSteps.length === 0 && <div style={s.emptyState}>All clear! Add your next moves above.</div>}
            </div>
          </div>
        )}

        {/* ── LEADS ── */}
        {activeTab === "leads" && (
          <div className="fade">
            {/* Header row */}
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:16, flexWrap:"wrap", gap:8 }}>
              <div>
                <h2 style={s.sectionTitle}>Zillow Lead Feed</h2>
                {leadsUpdated && <div style={{ fontSize:12, color:"#aaa", marginTop:3 }}>Last scan: {new Date(leadsUpdated).toLocaleString()}</div>}
              </div>
              <div style={{ display:"flex", gap:8 }}>
                <StatPill label="Total" value={leads.length} color="#4f46e5" />
                <StatPill label="Hot" value={leads.filter(l=>l.score>=3).length} color="#dc2626" />
                <StatPill label="Deals" value={leads.filter(l=>l.isDeal).length} color="#059669" />
              </div>
            </div>

            {leads.length === 0 ? (
              <div style={{ ...s.emptyState, background:"#fff", borderRadius:14, border:"1px solid #e4e4e7", padding:48 }}>
                <div style={{ fontSize:32, marginBottom:12 }}>🏚</div>
                <div style={{ fontWeight:700, marginBottom:6 }}>No leads loaded yet</div>
                <div style={{ fontSize:13, color:"#aaa" }}>Run <code style={{ background:"#f4f4f5", padding:"2px 6px", borderRadius:4 }}>py scripts/zillow_scraper.py</code> to pull fresh leads</div>
              </div>
            ) : (
              <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
                {leads.map((lead) => {
                  const status = leadStatuses[lead.id] || lead.status || "New";
                  const isHot  = lead.score >= 3;
                  const isDeal = lead.isDeal;
                  const borderColor = isDeal ? "#059669" : isHot ? "#dc2626" : "#e4e4e7";
                  const badgeBg    = isDeal ? "#dcfce7" : isHot ? "#fee2e2" : "#fef3c7";
                  const badgeColor = isDeal ? "#059669" : isHot ? "#dc2626" : "#d97706";
                  const badgeText  = isDeal ? "DEAL NOW" : isHot ? "HOT" : "WARM";
                  const statusColors = { New:"#4f46e5", Called:"#0891b2", "Offer Made":"#d97706", Dead:"#aaa", Closed:"#059669" };
                  return (
                    <div key={lead.id} style={{ background:"#fff", border:`1px solid ${borderColor}`, borderLeft:`4px solid ${borderColor}`, borderRadius:14, padding:"18px 20px" }}>
                      {/* Top row */}
                      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:12, flexWrap:"wrap", gap:8 }}>
                        <div style={{ flex:1 }}>
                          <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:4, flexWrap:"wrap" }}>
                            <span style={{ background:badgeBg, color:badgeColor, fontSize:10, fontWeight:800, padding:"2px 8px", borderRadius:6, letterSpacing:0.5 }}>{badgeText}</span>
                            <span style={{ fontSize:11, background:"#f4f4f5", color:"#666", padding:"2px 8px", borderRadius:6 }}>Score {lead.score}</span>
                            {lead.dom > 0 && <span style={{ fontSize:11, background:"#f4f4f5", color:"#666", padding:"2px 8px", borderRadius:6 }}>DOM {lead.dom}d</span>}
                          </div>
                          <div style={{ fontSize:16, fontWeight:700, color:"#111" }}>{lead.address}</div>
                          {lead.signals && <div style={{ fontSize:12, color:"#888", marginTop:3 }}>{lead.signals}</div>}
                        </div>
                        {/* Status picker */}
                        <select value={status} onChange={e => setLeadStatus(lead.id, e.target.value)}
                          style={{ fontSize:12, fontWeight:600, color:statusColors[status]||"#555", background:"#f9f9f9", border:"1px solid #e4e4e7", borderRadius:8, padding:"5px 10px", fontFamily:"Inter,sans-serif", cursor:"pointer" }}>
                          {["New","Called","Offer Made","Dead","Closed"].map(s => <option key={s}>{s}</option>)}
                        </select>
                      </div>

                      {/* Deal numbers */}
                      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(120px, 1fr))", gap:8, marginBottom:12 }}>
                        {[
                          { label:"Asking",   value:lead.price,   color:"#111"    },
                          { label:"Offer At", value:lead.offerAt, color:"#4f46e5" },
                          { label:"MAO",      value:lead.mao,     color:"#0891b2" },
                          { label:"Profit",   value:lead.profitLabel, color: isDeal ? "#059669" : "#d97706" },
                        ].map(n => (
                          <div key={n.label} style={{ background:"#f9f9f9", borderRadius:10, padding:"10px 14px" }}>
                            <div style={{ fontSize:10, color:"#aaa", fontWeight:700, textTransform:"uppercase", letterSpacing:0.5, marginBottom:4 }}>{n.label}</div>
                            <div style={{ fontSize:14, fontWeight:700, color:n.color }}>{n.value || "—"}</div>
                          </div>
                        ))}
                      </div>

                      {/* Footer row */}
                      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", flexWrap:"wrap", gap:8 }}>
                        <div style={{ display:"flex", gap:16, fontSize:12, color:"#888" }}>
                          {lead.agentPhone && <span>Agent: <strong style={{ color:"#333" }}>{lead.agentPhone}</strong></span>}
                          <span>Your #: <strong style={{ color:"#4f46e5" }}>{lead.yourNumber}</strong></span>
                        </div>
                        <a href={lead.url} target="_blank" rel="noreferrer"
                          style={{ fontSize:12, fontWeight:600, color:"#4f46e5", background:"#eff0fe", padding:"6px 14px", borderRadius:8, textDecoration:"none" }}>
                          View on Zillow →
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ── 5-YEAR VISION ── */}
        {activeTab === "vision" && (
          <div className="fade" style={{ margin: "0 -24px" }}>
            <FiveYearPlan />
          </div>
        )}
      </div>

      <div style={s.footer}>K Brothers Renovation LLC · Springfield, MO · Built with Claude Code</div>
    </div>
  );
}

function StatPill({ label, value, color }) {
  return (
    <div style={{ background: "#fff", border: "1px solid #e4e4e7", borderRadius: 10, padding: "10px 16px", textAlign: "center", minWidth: 72 }}>
      <div style={{ fontSize: 18, fontWeight: 800, color }}>{value}</div>
      <div style={{ fontSize: 11, color: "#999", marginTop: 2, textTransform: "uppercase", letterSpacing: 0.5 }}>{label}</div>
    </div>
  );
}

function ProgressRing({ pct, size, stroke, color }) {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#f0f0f0" strokeWidth={stroke} />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={stroke}
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
        style={{ transition: "stroke-dasharray 0.6s ease" }} />
    </svg>
  );
}

const s = {
  page: { fontFamily: "'Inter', sans-serif", minHeight: "100vh", background: "#f4f4f5", color: "#111" },
  loadingWrap: { display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100vh", gap: 12 },
  spinner: { width: 32, height: 32, border: "3px solid #eee", borderTop: "3px solid #4f46e5", borderRadius: "50%", animation: "spin 0.8s linear infinite" },
  loadingText: { color: "#999", fontSize: 14 },
  header: { background: "#fff", borderBottom: "1px solid #e4e4e7" },
  headerInner: { maxWidth: 1000, margin: "0 auto", padding: "20px 24px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 },
  brand: { display: "flex", alignItems: "center", gap: 14 },
  logo: { width: 44, height: 44, borderRadius: 12, background: "linear-gradient(135deg, #4f46e5, #7c3aed)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, fontWeight: 800 },
  brandName: { fontSize: 18, fontWeight: 800, letterSpacing: -0.5 },
  brandSub: { fontSize: 12, color: "#999", marginTop: 2 },
  headerStats: { display: "flex", gap: 10, flexWrap: "wrap" },
  masterBar: { height: 4, background: "#f0f0f0" },
  masterFill: { height: 4, background: "linear-gradient(90deg, #4f46e5, #7c3aed)", transition: "width 0.6s ease" },
  tabsWrap: { background: "#fff", borderBottom: "1px solid #e4e4e7" },
  tabs: { maxWidth: 1000, margin: "0 auto", padding: "0 24px", display: "flex" },
  tab: { padding: "14px 20px", fontSize: 13, fontWeight: 600, color: "#888", background: "transparent", border: "none", borderBottom: "2px solid transparent", fontFamily: "'Inter', sans-serif" },
  tabActive: { color: "#4f46e5", borderBottom: "2px solid #4f46e5" },
  content: { maxWidth: 1000, margin: "0 auto", padding: "24px" },
  overviewTop: { display: "flex", gap: 32, alignItems: "center", background: "#fff", borderRadius: 16, padding: 28, marginBottom: 16, flexWrap: "wrap", border: "1px solid #e4e4e7" },
  ringWrap: { position: "relative", flexShrink: 0 },
  ringInner: { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", textAlign: "center" },
  ringPct: { fontSize: 32, fontWeight: 800, color: "#4f46e5" },
  ringLabel: { fontSize: 11, color: "#aaa", textTransform: "uppercase", letterSpacing: 0.5 },
  overviewRight: { flex: 1, minWidth: 200 },
  overviewLabel: { fontSize: 11, color: "#aaa", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 6 },
  currentPhaseTitle: { fontSize: 22, fontWeight: 800, marginBottom: 4 },
  currentPhaseSub: { fontSize: 14, color: "#777", marginBottom: 16 },
  miniBarWrap: { marginBottom: 12 },
  miniBarLabel: { display: "flex", justifyContent: "space-between", fontSize: 12, color: "#999", marginBottom: 6 },
  miniBarTrack: { height: 6, background: "#f0f0f0", borderRadius: 3, overflow: "hidden" },
  miniBarFill: { height: 6, borderRadius: 3, transition: "width 0.5s ease" },
  badge: { display: "inline-block", padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600 },
  phaseGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12, marginBottom: 16 },
  phaseGridCard: { background: "#fff", border: "1px solid #e4e4e7", borderRadius: 12, padding: "16px 14px", cursor: "pointer" },
  phaseGridTop: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 },
  quickNext: { background: "#fff", border: "1px solid #e4e4e7", borderRadius: 12, padding: "18px 20px" },
  quickNextTitle: { fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: 0.5, color: "#aaa", marginBottom: 12 },
  quickNextItem: { display: "flex", alignItems: "center", gap: 10, fontSize: 14, color: "#333", marginBottom: 8 },
  seeAllBtn: { fontSize: 12, color: "#4f46e5", background: "none", border: "none", fontFamily: "'Inter', sans-serif", fontWeight: 600, marginTop: 4, padding: 0 },
  phaseNav: { display: "flex", gap: 8, marginBottom: 16, overflowX: "auto", paddingBottom: 4 },
  phaseBtn: { flex: "1 0 140px", padding: "14px 12px 10px", background: "#fff", border: "1px solid #e4e4e7", borderRadius: 12, textAlign: "left", fontFamily: "'Inter', sans-serif", minWidth: 140 },
  milestoneCard: { background: "#fff", border: "1px solid #e4e4e7", borderRadius: 14, padding: 24 },
  milestoneHeader: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 },
  milestoneItem: { display: "flex", alignItems: "center", gap: 12, padding: "12px 14px", borderRadius: 10, border: "1px solid #f0f0f0", background: "#fafafa", fontFamily: "'Inter', sans-serif", textAlign: "left", width: "100%" },
  checkbox: { width: 22, height: 22, borderRadius: 6, border: "2px solid #ddd", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, flexShrink: 0, background: "#fff", fontFamily: "'Inter', sans-serif", padding: 0 },
  sectionTop: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 },
  sectionTitle: { fontSize: 20, fontWeight: 800 },
  addBtn: { padding: "8px 16px", background: "#4f46e5", color: "#fff", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 600, fontFamily: "'Inter', sans-serif" },
  addForm: { display: "flex", flexDirection: "column", gap: 8, marginBottom: 16, padding: 16, background: "#fff", border: "1px solid #e4e4e7", borderRadius: 12 },
  input: { padding: "10px 14px", border: "1px solid #e0e0e0", borderRadius: 8, fontSize: 14, fontFamily: "'Inter', sans-serif", outline: "none", background: "#fff" },
  submitBtn: { padding: "10px 20px", background: "#4f46e5", color: "#fff", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 600, fontFamily: "'Inter', sans-serif", alignSelf: "flex-start" },
  cancelBtn: { padding: "10px 16px", background: "#f4f4f5", color: "#555", border: "none", borderRadius: 8, fontSize: 13, fontWeight: 600, fontFamily: "'Inter', sans-serif" },
  sessionCard: { display: "flex", gap: 16, background: "#fff", border: "1px solid #e4e4e7", borderRadius: 12, padding: "16px 18px" },
  sessionNum: { width: 28, height: 28, borderRadius: 8, background: "#f4f4f5", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: "#999", flexShrink: 0, marginTop: 2 },
  removeBtn: { width: 24, height: 24, border: "none", background: "transparent", color: "#ccc", fontSize: 18, fontFamily: "'Inter', sans-serif", padding: 0, display: "flex", alignItems: "center", justifyContent: "center" },
  stepItem: { display: "flex", alignItems: "center", gap: 12, padding: "14px 16px", background: "#fff", border: "1px solid #e4e4e7", borderRadius: 10 },
  emptyState: { textAlign: "center", padding: 40, color: "#ccc", fontSize: 14 },
  footer: { textAlign: "center", padding: "24px 16px", fontSize: 12, color: "#bbb" },
};
