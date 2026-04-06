export default function FiveYearPlan() {
  const milestones = [
    {
      year: "2026", label: "Foundation Year", color: "#4f46e5",
      goals: [
        "Go full-time in business by summer",
        "Close first wholesale deal",
        "Stack cash through roofing sales",
        "Build cash buyer list (10+ buyers)",
        "LLC + business bank account",
      ],
    },
    {
      year: "2027", label: "First Major Win", color: "#0891b2",
      goals: [
        "Mercedes S580 (2021+) — earned, not stressed over",
        "$80–100K from roofing (managed)",
        "First house flip — $20–35K profit",
        "2+ rental properties cash flowing",
        "$200K+ annual income",
      ],
    },
    {
      year: "2028", label: "Scale", color: "#059669",
      goals: [
        "Wholesaling + flips running consistently",
        "Rentals generating $14–24K/year",
        "Trading generating $18–36K/year",
        "Roofing runs without daily involvement",
        "Time freedom — you choose your day",
      ],
    },
    {
      year: "2029", label: "Empire Mode", color: "#d97706",
      goals: [
        "McLaren 720S",
        "Cadillac Escalade (family)",
        "Porsche Macan GTS (wife)",
        "Team of 20 people",
        "Expanding: Branson → STL → KC",
      ],
    },
    {
      year: "2031", label: "5-Year Vision", color: "#dc2626",
      goals: [
        "$5M net worth",
        "$700K home — paid off",
        "$1M beach house (Airbnb income)",
        "Wholesale + Flips + Rentals pipeline running",
        "Giving built into every business from day one",
      ],
    },
  ];

  const incomeTable = [
    { stream: "Roofing (managed)",  target: "$80–100K" },
    { stream: "House flipping",     target: "$40–60K"  },
    { stream: "Rental properties",  target: "$14–24K"  },
    { stream: "Trading",            target: "$18–36K"  },
    { stream: "Total",              target: "$152–220K+", bold: true },
  ];

  return (
    <div style={{ fontFamily: "Inter, sans-serif", color: "#1a1a1a" }}>
      <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>5-Year Vision</h2>
      <p style={{ color: "#666", marginBottom: 28, fontSize: 14 }}>
        Faith first. Every number below is a byproduct of doing the work with integrity.
      </p>

      {/* Timeline */}
      <div style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 36 }}>
        {milestones.map((m) => (
          <div key={m.year} style={{
            border: `2px solid ${m.color}20`,
            borderLeft: `4px solid ${m.color}`,
            borderRadius: 10,
            padding: "14px 18px",
            background: `${m.color}08`,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
              <span style={{
                background: m.color, color: "#fff", borderRadius: 6,
                padding: "2px 10px", fontSize: 13, fontWeight: 700,
              }}>{m.year}</span>
              <span style={{ fontWeight: 600, fontSize: 15 }}>{m.label}</span>
            </div>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {m.goals.map((g, i) => (
                <li key={i} style={{ fontSize: 13, color: "#444", marginBottom: 3 }}>{g}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Income table */}
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Income Stack by 2028</h3>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
        <thead>
          <tr style={{ background: "#f5f5f5" }}>
            <th style={{ textAlign: "left", padding: "8px 12px", borderRadius: "6px 0 0 6px" }}>Income Stream</th>
            <th style={{ textAlign: "right", padding: "8px 12px", borderRadius: "0 6px 6px 0" }}>Annual Target</th>
          </tr>
        </thead>
        <tbody>
          {incomeTable.map((row) => (
            <tr key={row.stream} style={{
              borderBottom: "1px solid #eee",
              fontWeight: row.bold ? 700 : 400,
              background: row.bold ? "#f9f9f9" : "transparent",
            }}>
              <td style={{ padding: "8px 12px" }}>{row.stream}</td>
              <td style={{ padding: "8px 12px", textAlign: "right", color: row.bold ? "#059669" : "#333" }}>{row.target}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <p style={{ marginTop: 24, fontSize: 12, color: "#999", textAlign: "center" }}>
        Lifestyle upgrades come AFTER assets are acquired — not before.
      </p>
    </div>
  );
}
