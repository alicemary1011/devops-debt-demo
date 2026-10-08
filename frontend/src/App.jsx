import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://localhost:10000/analyze";

function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const runAnalysis = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(API_URL);

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();

      setReport(data.analysis);
    } catch (err) {
      setError(
        "Unable to connect to the Docker analyzer. Make sure the Docker container is running."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAnalysis();
  }, []);

  /*
    The analyzer report contains a findings array.
    We use it to calculate the dashboard statistics.
  */
  const findings = report?.findings || [];

  const highCount = findings.filter(
    (item) => item.severity?.toLowerCase() === "high"
  ).length;

  const mediumCount = findings.filter(
    (item) => item.severity?.toLowerCase() === "medium"
  ).length;

  const lowCount = findings.filter(
    (item) => item.severity?.toLowerCase() === "low"
  ).length;

  const categoryCounts = findings.reduce((result, item) => {
    const category = item.category || "Other";

    result[category] = (result[category] || 0) + 1;

    return result;
  }, {});

  return (
    <div className="dashboard">

      {/* HEADER */}

      <header className="header">
        <div>
          <p className="eyebrow">DEVOPS TOOL</p>

          <h1>Technical Debt Analyzer</h1>

          <p className="subtitle">
            Continuous detection of technical debt across CI/CD,
            Docker and infrastructure configuration.
          </p>
        </div>

        <button
          className="analyze-button"
          onClick={runAnalysis}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Run Analysis"}
        </button>
      </header>


      {/* ERROR */}

      {error && (
        <div className="error">
          {error}
        </div>
      )}


      {/* LOADING */}

      {loading && !report ? (
        <div className="loading">
          Analyzing repository...
        </div>
      ) : (
        <>

          {/* STATISTICS */}

          <section className="stats-grid">

            <div className="stat-card">
              <span>Total Debt</span>
              <strong>{findings.length}</strong>
            </div>

            <div className="stat-card high">
              <span>High Severity</span>
              <strong>{highCount}</strong>
            </div>

            <div className="stat-card medium">
              <span>Medium Severity</span>
              <strong>{mediumCount}</strong>
            </div>

            <div className="stat-card low">
              <span>Low Severity</span>
              <strong>{lowCount}</strong>
            </div>

          </section>


          {/* MAIN CONTENT */}

          <section className="content-grid">

            {/* FINDINGS */}

            <div className="panel">

              <div className="panel-header">

                <div>
                  <p className="eyebrow">
                    DETECTED ISSUES
                  </p>

                  <h2>
                    Technical Debt Findings
                  </h2>
                </div>

                <span className="count-badge">
                  {findings.length}
                </span>

              </div>


              {findings.length === 0 ? (

                <div className="empty">
                  No technical debt detected.
                </div>

              ) : (

                <div className="findings">

                  {findings.map((item, index) => (

                    <div
                      className="finding"
                      key={item.id || index}
                    >

                      <div className="finding-id">
                        {item.id || `D00${index + 1}`}
                      </div>

                      <div className="finding-main">

                        <h3>
                          {item.title ||
                            item.description ||
                            "Technical debt detected"}
                        </h3>

                        <p>
                          {item.description ||
                            "Technical debt detected by the analyzer."}
                        </p>

                      </div>

                      <span
                        className={`severity ${
                          item.severity?.toLowerCase() || "low"
                        }`}
                      >
                        {item.severity || "LOW"}
                      </span>

                    </div>

                  ))}

                </div>

              )}

            </div>


            {/* CATEGORY BREAKDOWN */}

            <div className="panel">

              <div className="panel-header">

                <div>
                  <p className="eyebrow">
                    BREAKDOWN
                  </p>

                  <h2>
                    Debt by Category
                  </h2>
                </div>

              </div>


              <div className="categories">

                {Object.entries(categoryCounts).map(
                  ([category, count]) => (

                    <div
                      className="category-row"
                      key={category}
                    >

                      <div className="category-info">

                        <span>
                          {category}
                        </span>

                        <strong>
                          {count}
                        </strong>

                      </div>

                      <div className="bar">

                        <div
                          className="bar-fill"
                          style={{
                            width: `${
                              (count / findings.length) * 100
                            }%`,
                          }}
                        />

                      </div>

                    </div>

                  )
                )}

                {findings.length === 0 && (
                  <div className="empty">
                    No categories available.
                  </div>
                )}

              </div>

            </div>

          </section>


          {/* DEVOPS PIPELINE */}

          <section className="pipeline">

            <div>

              <p className="eyebrow">
                DEVOPS PIPELINE
              </p>

              <h2>
                Implementation
              </h2>

            </div>


            <div className="pipeline-flow">

              <div className="pipeline-step">

                <span className="dot success"></span>

                <strong>
                  GitHub
                </strong>

                <small>
                  Source
                </small>

              </div>


              <span className="arrow">
                →
              </span>


              <div className="pipeline-step">

                <span className="dot success"></span>

                <strong>
                  GitHub Actions
                </strong>

                <small>
                  CI/CD
                </small>

              </div>


              <span className="arrow">
                →
              </span>


              <div className="pipeline-step">

                <span className="dot success"></span>

                <strong>
                  Docker
                </strong>

                <small>
                  Container
                </small>

              </div>


              <span className="arrow">
                →
              </span>


              <div className="pipeline-step">

                <span className="dot success"></span>

                <strong>
                  Analyzer
                </strong>

                <small>
                  Detection
                </small>

              </div>


              <span className="arrow">
                →
              </span>


              <div className="pipeline-step">

                <span className="dot active"></span>

                <strong>
                  Dashboard
                </strong>

                <small>
                  Visualization
                </small>

              </div>

            </div>

          </section>

        </>
      )}

    </div>
  );
}

export default App;