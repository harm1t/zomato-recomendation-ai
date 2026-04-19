'use client';

import { useState } from 'react';
import PreferencesForm from './PreferencesForm';
import RecommendationsGrid from './RecommendationsGrid';
import styles from './RecommendationClient.module.css';

export default function RecommendationClient() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRecommend = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail ? (Array.isArray(data.detail) ? data.detail.map(d => d.msg).join('; ') : data.detail) : 'Failed to fetch');
      }
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <section className={styles.heroSection}>
        <div className={styles.heroOverlay}></div>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>Find Your Perfect Meal with Zomato AI</h1>
          <PreferencesForm onSubmit={handleRecommend} loading={loading} />
          {error && <div className={styles.errorBanner}>{error}</div>}
        </div>
      </section>

      {results && (
        <section className={styles.resultsSection}>
          <div className={styles.resultsContainer}>
            <h2 className={styles.resultsTitle}>Personalized Picks for You</h2>
            <p className={styles.resultsSummary}>{results.summary}</p>
            <RecommendationsGrid items={results.items || []} />
          </div>
        </section>
      )}
    </>
  );
}
