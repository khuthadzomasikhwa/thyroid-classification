import { useState } from "react";

const YES_NO = [
  ["on_thyroxine", "On thyroxine"],
  ["query_on_thyroxine", "Query on thyroxine"],
  ["on_antithyroid_medication", "On antithyroid medication"],
  ["thyroid_surgery", "Thyroid surgery"],
  ["I131_treatment", "I131 treatment"],
  ["lithium", "Lithium"],
  ["query_hypothyroid", "Query hypothyroid"],
  ["query_hyperthyroid", "Query hyperthyroid"],
  ["pregnant", "Pregnant"],
  ["sick", "Sick"],
  ["tumor", "Tumor"],
  ["psych", "Psychiatric symptoms"],
];

const LABS = [
  ["TSH", "TSH"],
  ["T3", "T3"],
  ["TT4", "TT4"],
  ["T4U", "T4U"],
  ["FTI", "FTI"],
];

const START = {
  age: "",
  sex: "",
  ...Object.fromEntries(YES_NO.map(([key]) => [key, ""])),
  ...Object.fromEntries(LABS.map(([key]) => [key, ""])),
};

export default function App() {
  const [values, setValues] = useState(START);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function setField(key, value) {
    setValues((current) => ({ ...current, [key]: value }));
  }

  async function onSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const ageText = values.age.trim();
    if (ageText !== "") {
      const age = Number(ageText);
      if (!Number.isFinite(age) || !Number.isInteger(age)) {
        setResult(null);
        setError("Age must be a whole number.");
        setBusy(false);
        return;
      }
    }
    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      const body = await response.json();
      if (!response.ok) {
        setResult(null);
        setError(body.error || "Could not classify that record.");
        return;
      }
      setResult(body);
    } catch {
      setResult(null);
      setError("Could not reach the model. Leave this page running and try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <header className="top">
        <div className="wrap">
          <h1>Thyroid classification</h1>
          <p>Random forest with SMOTE</p>
        </div>
      </header>

      <main className="wrap">
        <p className="intro">
          Enter one patient record. The model classifies it as no thyroid problem,
          hypothyroid, or hyperthyroid.
        </p>

        <div className="layout">
          <form onSubmit={onSubmit}>
            <section>
              <h2>Patient details</h2>
              <div className="grid">
                <label>
                  <span>Age</span>
                  <input
                    value={values.age}
                    onChange={(event) => setField("age", event.target.value)}
                    inputMode="decimal"
                    placeholder="Not recorded"
                  />
                </label>
                <label>
                  <span>
                    Sex<span className="req">*</span>
                  </span>
                  <select
                    value={values.sex}
                    onChange={(event) => setField("sex", event.target.value)}
                    required
                  >
                    <option value="" disabled>
                      Choose sex
                    </option>
                    <option value="F">Female</option>
                    <option value="M">Male</option>
                    <option value="Unknown">Unknown</option>
                  </select>
                </label>
              </div>
            </section>

            <section>
              <h2>Clinical information</h2>
              <div className="grid">
                {YES_NO.map(([key, label]) => (
                  <label key={key}>
                    <span>
                      {label}
                      <span className="req">*</span>
                    </span>
                    <select
                      value={values[key]}
                      onChange={(event) => setField(key, event.target.value)}
                      required
                    >
                      <option value="" disabled>
                        Choose
                      </option>
                      <option value="0">No</option>
                      <option value="1">Yes</option>
                    </select>
                  </label>
                ))}
              </div>
            </section>

            <section>
              <h2>Laboratory results</h2>
              <div className="grid">
                {LABS.map(([key, label]) => (
                  <label key={key}>
                    {label}
                    <input
                      value={values[key]}
                      onChange={(event) => setField(key, event.target.value)}
                      inputMode="decimal"
                      placeholder="Not measured"
                    />
                  </label>
                ))}
              </div>
            </section>

            <div className="actions">
              <button type="submit" disabled={busy}>
                {busy ? "Classifying..." : "Classify"}
              </button>
            </div>
          </form>

          <aside className="result" aria-live="polite">
            <h2>Result</h2>
            {error ? <p className="error">{error}</p> : null}
            {result ? (
              <>
                <p className="predicted-label">Predicted class</p>
                <p className="predicted">{result.name}</p>
                <table>
                  <caption>Class probability</caption>
                  <thead>
                    <tr>
                      <th>Class</th>
                      <th>Probability</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.probabilities.map((item) => (
                      <tr key={item.name} className={item.name === result.name ? "chosen" : ""}>
                        <td>{item.name}</td>
                        <td>
                          <span className="prob">{item.value.toFixed(2)}</span>
                          <span className="meter" aria-hidden="true">
                            <span style={{ width: `${Math.round(item.value * 100)}%` }} />
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            ) : (
              <p className="waiting">The classification will appear here.</p>
            )}
          </aside>
        </div>
      </main>
    </>
  );
}
