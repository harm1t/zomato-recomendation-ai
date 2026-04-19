import { useState, useEffect } from 'react';
import styles from './PreferencesForm.module.css';

export default function PreferencesForm({ onSubmit, loading }) {
  const [localities, setLocalities] = useState([]);
  
  useEffect(() => {
    fetch('/api/v1/localities')
      .then(r => r.json())
      .then(data => setLocalities(data.slice(0, 8000)))
      .catch(e => console.error("Could not fetch localities", e));
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const payload = {
      location: fd.get('location'),
      cuisine: fd.get('cuisine')?.trim() || undefined,
      min_rating: parseFloat(fd.get('min_rating')) || 0,
      budget_min_inr: fd.get('budget_min_inr') ? parseInt(fd.get('budget_min_inr'), 10) : undefined,
      budget_max_inr: fd.get('budget_max_inr') ? parseInt(fd.get('budget_max_inr'), 10) : undefined,
      extras: fd.get('extras')?.trim() || undefined
    };
    onSubmit(payload);
  };

  return (
    <form className={styles.formContainer} onSubmit={handleSubmit}>
      <div className={styles.grid}>
        <div className={styles.field}>
          <label>LOCALITY</label>
          <select name="location" required defaultValue="">
            <option value="" disabled>e.g. Banashankari</option>
            {localities.map(loc => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
        </div>

        <div className={styles.field}>
          <label>CUISINE</label>
          <input type="text" name="cuisine" placeholder="e.g. North Indian" />
        </div>

        <div className={styles.field}>
          <label>MIN BUDGET (₹)</label>
          <input type="number" name="budget_min_inr" min="0" step="50" placeholder="0" />
        </div>

        <div className={styles.field}>
          <label>MAX BUDGET (₹)</label>
          <input type="number" name="budget_max_inr" min="0" step="50" placeholder="1000" />
        </div>

        <div className={styles.field}>
          <label>MIN RATING (1-5)</label>
          <div className={styles.ratingInputWrapper}>
            <span className={styles.star}>★</span>
            <input type="number" name="min_rating" min="0" max="5" step="0.1" defaultValue="4.0" />
          </div>
        </div>

        <div className={styles.field}>
          <label>SPECIFIC CRAVINGS</label>
          <input type="text" name="extras" placeholder="e.g. Biryani, Butter Chicken" />
        </div>
      </div>

      <button type="submit" className={styles.submitBtn} disabled={loading}>
        {loading ? "Getting Recommendations..." : "Get Recommendations"}
      </button>
    </form>
  );
}
